import os

import requests

LM_STUDIO_URL = os.environ.get('LM_STUDIO_URL', 'http://host.docker.internal:1234/v1')
COVER_LETTER_MODEL = os.environ.get(
    'COVER_LETTER_MODEL',
    os.environ.get('JOB_FINDER_MODEL', 'qwen2.5-1.5b-instruct'),
)


class CoverLetterAgent:
    """Generates a personalised cover letter for a specific job listing.

    Uses the candidate's CV data; highlights top 3 matching skills.
    """

    def __init__(self):
        self.model = COVER_LETTER_MODEL
        self.api_url = f'{LM_STUDIO_URL}/chat/completions'

    def generate(self, cv_data: dict, job: dict) -> str:
        name = cv_data.get('name', 'the candidate')
        skills = ', '.join(cv_data.get('skills', [])[:12]) or 'Not specified'
        experience = '; '.join(cv_data.get('experience', [])[:3]) or 'Not specified'
        education = '; '.join(cv_data.get('education', [])[:2]) or 'Not specified'

        job_title = job.get('title', 'the advertised position')
        job_company = job.get('company', 'your company')
        job_desc = job.get('description', '')[:300]

        try:
            resp = requests.post(
                self.api_url,
                json={
                    'model': self.model,
                    'messages': [
                        {
                            'role': 'system',
                            'content': (
                                'You are an expert cover letter writer. '
                                'Write professional, personalised cover letters in plain text. '
                                'Never use markdown or code blocks. '
                                '3 to 4 paragraphs, around 250-350 words. '
                                'Only use skills and experience present in the CV — never fabricate.'
                            ),
                        },
                        {
                            'role': 'user',
                            'content': (
                                f'Write a cover letter for {name} applying to the {job_title} position at {job_company}.\n\n'
                                f'Candidate CV:\n'
                                f'- Skills: {skills}\n'
                                f'- Experience: {experience}\n'
                                f'- Education: {education}\n\n'
                                f'Job description: {job_desc}\n\n'
                                f'Highlight the 3 most relevant skills. Address the hiring manager at {job_company}. End with a call to action.'
                            ),
                        },
                    ],
                    'temperature': 0.5,
                    'max_tokens': 600,
                },
                timeout=120,
            )
            content = resp.json()['choices'][0]['message']['content'].strip()

            # Strip markdown code fences if the model added them
            if '```' in content:
                parts = content.split('```')
                # Take the content between the first pair of fences
                inner = parts[1] if len(parts) >= 3 else parts[0]
                # Remove language tag if present
                lines = inner.split('\n')
                if lines and lines[0].strip().isalpha():
                    lines = lines[1:]
                content = '\n'.join(lines).strip()

            return content

        except Exception as e:
            print(f'[CoverLetterAgent] error: {e}')
            return (
                f'Dear Hiring Manager,\n\n'
                f'I am writing to express my interest in the {job_title} position '
                f'at {job_company}.\n\n'
                f'[Cover letter generation was unavailable. Please edit this text manually.]\n\n'
                f'Sincerely,\n{name}'
            )
