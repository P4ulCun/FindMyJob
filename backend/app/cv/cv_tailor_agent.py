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

CANDIDATE CV:
- Skills: {skills}
- Experience: {experience}
- Education: {education}

JOB LISTING:
- Title: {job.get('title', '')}
- Company: {job.get('company', '')}
- Description: {job.get('description', '')[:800]}

Reply ONLY with a valid JSON object, no markdown, no extra text:
{{"tailored_skills": [<list of strings>], "tailored_experience": [<list of strings>], "tailored_education": [<list of strings>]}}"""

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
            content = resp.json()['choices'][0]['message']['content'].strip()

            # Strip markdown code fences if the model added them
            if '```' in content:
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]

            result = json.loads(content)

            # Ensure all expected keys exist
            return {
                'tailored_skills': result.get('tailored_skills', cv_data.get('skills', [])),
                'tailored_experience': result.get('tailored_experience', cv_data.get('experience', [])),
                'tailored_education': result.get('tailored_education', cv_data.get('education', [])),
            }
        except Exception as e:
            print(f'[CVTailorAgent] error: {e}')
            # Fallback: return original CV data unchanged
            return {
                'tailored_skills': cv_data.get('skills', []),
                'tailored_experience': cv_data.get('experience', []),
                'tailored_education': cv_data.get('education', []),
            }
