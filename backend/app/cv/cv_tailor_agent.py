import json
import os

import requests

LM_STUDIO_URL = os.environ.get('LM_STUDIO_URL', 'http://host.docker.internal:1234/v1')
CV_TAILOR_MODEL = os.environ.get('CV_TAILOR_MODEL', os.environ.get('JOB_FINDER_MODEL', 'qwen2.5-1.5b-instruct'))


class CVTailorAgent:
    """Rewrites CV bullet points to match a specific job description.

    Uses only skills and experience already present in the original CV —
    never fabricates new ones.
    """

    def __init__(self):
        self.model = CV_TAILOR_MODEL
        self.api_url = f'{LM_STUDIO_URL}/chat/completions'

    def _normalize_section_changes(self, section_name: str, original_items: list, raw_items) -> list:
        if not isinstance(raw_items, list):
            raw_items = []

        changes = []
        max_len = len(original_items)

        for idx in range(max_len):
            before = str(original_items[idx]).strip()
            raw_item = raw_items[idx] if idx < len(raw_items) else {}

            if isinstance(raw_item, dict):
                after = str(raw_item.get('after', before)).strip() or before
                reason = str(raw_item.get('reason', '')).strip()
            else:
                after = str(raw_item).strip() or before
                reason = ''

            changes.append({
                'id': f'{section_name}-{idx}',
                'before': before,
                'after': after,
                'reason': reason or 'Adjusted wording to better match the job requirements.',
                'status': 'pending',
            })

        return changes

    def _build_result(self, cv_data: dict, result: dict) -> dict:
        change_set = {
            'skills': self._normalize_section_changes(
                'skills',
                cv_data.get('skills', []),
                result.get('skills'),
            ),
            'experience': self._normalize_section_changes(
                'experience',
                cv_data.get('experience', []),
                result.get('experience'),
            ),
            'education': self._normalize_section_changes(
                'education',
                cv_data.get('education', []),
                result.get('education'),
            ),
        }

        return {
            'change_set': change_set,
            'tailored_skills': [item['after'] for item in change_set['skills']],
            'tailored_experience': [item['after'] for item in change_set['experience']],
            'tailored_education': [item['after'] for item in change_set['education']],
        }

    def tailor(self, cv_data: dict, job: dict) -> dict:
        skills = ', '.join(cv_data.get('skills', [])) or 'Not specified'
        experience = '; '.join(cv_data.get('experience', [])) or 'Not specified'
        education = '; '.join(cv_data.get('education', [])) or 'Not specified'

        prompt = f"""You are an expert CV tailoring assistant. Your job is to rewrite the candidate's CV content so it is optimised for a specific job listing.

RULES:
1. Rewrite experience bullet points to emphasise keywords and requirements from the job description.
2. Reorder and rephrase skills to prioritise those most relevant to the job.
3. Adjust education descriptions only if wording can better match the job.
4. NEVER invent skills, experience, or qualifications that are not in the original CV.
5. Keep the same number of items in each list.
6. For every item, include a short reason that explains why the wording changed.

CANDIDATE CV:
- Skills: {skills}
- Experience: {experience}
- Education: {education}

JOB LISTING:
- Title: {job.get('title', '')}
- Company: {job.get('company', '')}
- Description: {job.get('description', '')[:800]}

Reply ONLY with a valid JSON object, no markdown, no extra text:
{{"skills": [{{"after": "<rewritten item>", "reason": "<short why>"}}], "experience": [{{"after": "<rewritten item>", "reason": "<short why>"}}], "education": [{{"after": "<rewritten item>", "reason": "<short why>"}}]}}"""

        try:
            resp = requests.post(
                self.api_url,
                json={
                    'model': self.model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.3,
                    'max_tokens': 1000,
                },
                timeout=60,
            )
            resp.raise_for_status()
            content = resp.json()['choices'][0]['message']['content'].strip()

            # Strip markdown code fences if the model added them
            if '```' in content:
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]

            result = json.loads(content)
            return self._build_result(cv_data, result)
        except Exception as e:
            print(f'[CVTailorAgent] error: {e}')
            return self._build_result(cv_data, {})
