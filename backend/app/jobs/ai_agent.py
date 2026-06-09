import json
import os
import re

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

        prompt = f"""You are a strict job matching assistant. Rate how well the candidate matches the job listing.

Candidate CV:
- Skills: {skills}
- Experience: {experience}
- Education: {education}

Job Listing:
- Title: {job.get('title', '')}
- Company: {job.get('company', '')}
- Location: {job.get('location', '')}
- Description: {job.get('description', '')[:500]}

Scoring criteria (be strict and realistic):
- 80-100: Strong match — candidate has most required skills and relevant experience for this exact role
- 50-79: Partial match — candidate meets some requirements but is missing key skills or experience
- 20-49: Weak match — candidate has transferable skills but significant gaps exist
- 0-19: Poor match — candidate profile does not align with the job requirements

Reply ONLY with a valid JSON object, no markdown, no extra text:
{{"score": <integer 0-100>, "summary": "<1-2 sentence explanation of the match>"}}"""

        try:
            resp = requests.post(
                self.api_url,
                json={
                    'model': self.model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.1,
                    'max_tokens': 250,
                },
                timeout=30,
            )
            
            if resp.status_code != 200:
                print(f"[JobScoringAgent] HTTP Error {resp.status_code}: {resp.text}")
                resp.raise_for_status()

            data = resp.json()
            if 'choices' not in data:
                print(f"[JobScoringAgent] Invalid response from LM Studio: {data}")
                raise KeyError('choices')

            content = data['choices'][0]['message']['content'].strip()

            if '```' in content:
                content = content.split('```')[1].lstrip('json').strip()

            try:
                return json.loads(content)
            except json.JSONDecodeError:
                score_match = re.search(r'"score"\s*:\s*(\d+)', content)
                summary_match = re.search(r'"summary"\s*:\s*"(.*?)(?<!\\)"', content, re.DOTALL)
                if score_match:
                    return {
                        'score': int(score_match.group(1)),
                        'summary': summary_match.group(1).replace('\n', ' ') if summary_match else '',
                    }
                raise
        except Exception as e:
            print(f"[JobScoringAgent] error: {e}")
            return {'score': 0, 'summary': f'AI scoring unavailable: {e}'}
