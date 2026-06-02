import re
import pdfplumber


def extract_text_from_pdf(file) -> str:
    text_pages = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=1)
            if page_text:
                text_pages.append(page_text)
    return '\n'.join(text_pages)


def parse_cv_text(raw_text: str) -> dict:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    name = lines[0] if lines else ''

    section_headers = {
        'skills':      re.compile(r'(technical\s+)?skills|competențe|competente|abilities', re.IGNORECASE),
        'experience':  re.compile(r'^(work\s+)?(experience|experiență|experienta|history|employment)', re.IGNORECASE),
        'education':   re.compile(r'^(education|educație|educatie|studii|formation)', re.IGNORECASE),
        'projects':    re.compile(r'^projects?', re.IGNORECASE),
        'achievements': re.compile(r'^achievements?|awards?|honors?', re.IGNORECASE),
    }

    sections: dict[str, list[str]] = {k: [] for k in section_headers}
    current_section = None

    for line in lines[1:]:
        # Only treat short lines as potential section headers (headers are rarely > 40 chars)
        matched = False
        if len(line) <= 40:
            for key, pattern in section_headers.items():
                if pattern.search(line):
                    current_section = key
                    matched = True
                    break
        if not matched and current_section:
            sections[current_section].append(line)

    # Projects count as experience for job matching purposes
    combined_experience = sections['experience'] + sections['projects']

    return {
        'name': name,
        'skills': sections['skills'],
        'experience': combined_experience,
        'education': sections['education'],
    }
