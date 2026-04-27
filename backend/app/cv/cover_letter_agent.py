import json
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
        skills = ', '.join(cv_data.get('skills', [])) or 'Not specified'
        experience = '; '.join(cv_data.get('experience', [])) or 'Not specified'
        education = '; '.join(cv_data.get('education', [])) or 'Not specified'

        job_title = job.get('title', 'the advertised position')
        job_company = job.get('company', 'your company')
        job_desc = job.get('description', '')[:800]

        prompt = f"""You are an expert cover letter writer. Write a professional, personalised cover letter for the candidate applying to a specific job.

RULES:
1. Address the letter to the hiring manager at {job_company}.
2. Mention the job title "{job_title}" in the opening paragraph.
3. Highlight the TOP 3 most relevant skills from the candidate's CV that match the job description.
4. Reference specific experience from the CV that is relevant.
5. Keep it concise — 3 to 4 paragraphs, around 250-350 words.
6. Use a professional but warm tone.
7. Do NOT fabricate any skills or experience not present in the CV.
8. End with a polite call to action.

CANDIDATE CV:
- Name: {name}
- Skills: {skills}
- Experience: {experience}
- Education: {education}

JOB LISTING:
- Title: {job_title}
- Company: {job_company}
- Description: {job_desc}

Write the cover letter as plain text. Do NOT use markdown formatting. Do NOT wrap in code blocks."""

        try:
            resp = requests.post(
                self.api_url,
                json={
                    'model': self.model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.5,
                    'max_tokens': 1200,
                },
                timeout=60,
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
