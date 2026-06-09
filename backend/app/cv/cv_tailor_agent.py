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

            if after == before:
                continue

            changes.append({
                'id': f'{section_name}-{idx}',
                'before': before,
                'after': after,
                'reason': reason or 'Adjusted wording to better match the job requirements.',
                'status': 'pending',
            })

        return changes

    def _resolve_section_items(self, original_items: list, raw_items) -> list:
        if not isinstance(raw_items, list):
            raw_items = []

        resolved_items = []
        max_len = len(original_items)

        for idx in range(max_len):
            before = str(original_items[idx]).strip()
            raw_item = raw_items[idx] if idx < len(raw_items) else {}

            if isinstance(raw_item, dict):
                after = str(raw_item.get('after', before)).strip() or before
            else:
                after = str(raw_item).strip() or before

            resolved_items.append(after)

        return resolved_items

    def _build_result(self, cv_data: dict, result: dict) -> dict:
        tailored_skills = self._resolve_section_items(cv_data.get('skills', []), result.get('skills'))
        tailored_experience = self._resolve_section_items(cv_data.get('experience', []), result.get('experience'))
        tailored_education = self._resolve_section_items(cv_data.get('education', []), result.get('education'))

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
            'tailored_skills': tailored_skills,
            'tailored_experience': tailored_experience,
            'tailored_education': tailored_education,
        }

    def tailor(self, cv_data: dict, job: dict) -> dict:
        skills = ', '.join(cv_data.get('skills', [])[:12]) or 'Not specified'
        experience = '; '.join(cv_data.get('experience', [])[:3]) or 'Not specified'
        education = '; '.join(cv_data.get('education', [])[:2]) or 'Not specified'

        try:
            resp = requests.post(
                self.api_url,
                json={
                    'model': self.model,
                    'messages': [
                        {
                            'role': 'system',
                            'content': (
                                'You are a CV tailoring expert. '
                                'Rewrite CV items to better match a job description. '
                                'Never invent skills or experience not present in the original CV. '
                                'Keep the same number of items in each list. '
                                'Return ONLY a valid JSON object with keys "skills", "experience", "education". '
                                'Each key maps to a list of objects with "after" and "reason" fields.'
                            ),
                        },
                        {
                            'role': 'user',
                            'content': (
                                f'Rewrite the CV below to better match the job listing. '
                                f'Return JSON only.\n\n'
                                f'CV Skills: {skills}\n'
                                f'CV Experience: {experience}\n'
                                f'CV Education: {education}\n\n'
                                f'Job: {job.get("title", "")} at {job.get("company", "")}\n'
                                f'Description: {job.get("description", "")[:400]}'
                            ),
                        },
                    ],
                    'temperature': 0.3,
                    'max_tokens': 2000,
                },
                timeout=120,
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
