import re
import pdfplumber


def extract_text_from_pdf(file) -> str:
    """Return the full raw text extracted from a PDF file-like object."""
    text_pages = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)
    return '\n'.join(text_pages)


def parse_cv_text(raw_text: str) -> dict:
    """
    Naive heuristic parser that pulls structured sections out of raw CV text.
    Returns a dict with keys: name, skills, experience, education.
    """
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    # --- name: first non-empty line ---
    name = lines[0] if lines else ''

    # --- section splitter ---
    section_headers = {
        'skills': re.compile(r'^(skills|competențe|competente|abilities)', re.IGNORECASE),
        'experience': re.compile(r'^(experience|experiență|experienta|work\s*history|employment)', re.IGNORECASE),
        'education': re.compile(r'^(education|educație|educatie|studii|formation)', re.IGNORECASE),
    }

    sections: dict[str, list[str]] = {k: [] for k in section_headers}
    current_section = None

    for line in lines[1:]:
        matched = False
        for key, pattern in section_headers.items():
            if pattern.search(line):
                current_section = key
                matched = True
                break
        if not matched and current_section:
            sections[current_section].append(line)

    return {
        'name': name,
        'skills': sections['skills'],
        'experience': sections['experience'],
        'education': sections['education'],
    }
