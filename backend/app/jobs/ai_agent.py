import json
import os

import requests

LM_STUDIO_URL = os.environ.get('LM_STUDIO_URL', 'http://host.docker.internal:1234/v1')
JOB_FINDER_MODEL = os.environ.get('JOB_FINDER_MODEL', 'qwen2.5-1.5b-instruct')


class JobScoringAgent:
    def __init__(self):
        self.model = JOB_FINDER_MODEL
        self.api_url = f'{LM_STUDIO_URL}/chat/completions'

    def score_job(self, job: dict, cv_data: dict) -> dict:
        skills = ', '.join(cv_data.get('skills', [])) or 'Not specified'
        experience = '; '.join(cv_data.get('experience', [])) or 'Not specified'
        education = '; '.join(cv_data.get('education', [])) or 'Not specified'

        prompt = f"""You are a job matching assistant. Rate how well the candidate matches the job listing.

Candidate CV:
- Skills: {skills}
- Experience: {experience}
- Education: {education}

Job Listing:
- Title: {job.get('title', '')}
- Company: {job.get('company', '')}
- Location: {job.get('location', '')}
- Description: {job.get('description', '')[:400]}

Reply ONLY with a valid JSON object, no markdown, no extra text:
{{"score": <integer 0-100>, "summary": "<1-2 sentence explanation of the match>"}}"""

        try:
            resp = requests.post(
                self.api_url,
                json={
                    'model': self.model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.1,
                    'max_tokens': 150,
                },
                timeout=30,
            )
            content = resp.json()['choices'][0]['message']['content'].strip()

            # Strip markdown code fences if the model added them
            if '```' in content:
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]

            return json.loads(content)
        except Exception as e:
            print(f"[JobScoringAgent] error: {e}")
            return {'score': 0, 'summary': f'AI scoring unavailable: {e}'}
