import os
import requests

FETCH_LIMIT = 5


def fetch_remoteok(job_title, limit=FETCH_LIMIT):
    try:
        resp = requests.get(
            'https://remoteok.com/api',
            headers={'User-Agent': 'FindMyJob/1.0'},
            timeout=10,
        )
        data = resp.json()
        # First item is metadata — skip it
        jobs = [j for j in data if isinstance(j, dict) and j.get('position')]

        if job_title:
            keywords = job_title.lower().split()
            jobs = [
                j for j in jobs
                if any(
                    kw in j.get('position', '').lower()
                    or kw in ' '.join(j.get('tags', [])).lower()
                    for kw in keywords
                )
            ]

        return [
            {
                'title': j.get('position', ''),
                'company': j.get('company', ''),
                'location': 'Remote',
                'description': j.get('description', '')[:600],
                'url': j.get('url', ''),
                'source': 'RemoteOK',
                'tags': j.get('tags', []),
            }
            for j in jobs[:limit]
        ]
    except Exception:
        return []


def fetch_arbeitnow(job_title, location='', limit=FETCH_LIMIT):
    try:
        resp = requests.get(
            'https://www.arbeitnow.com/api/job-board-api',
            timeout=10,
        )
        data = resp.json()
        jobs = data.get('data', [])

        if job_title:
            keywords = job_title.lower().split()
            jobs = [
                j for j in jobs
                if any(
                    kw in j.get('title', '').lower()
                    or kw in j.get('description', '').lower()
                    for kw in keywords
                )
            ]

        return [
            {
                'title': j.get('title', ''),
                'company': j.get('company_name', ''),
                'location': j.get('location', ''),
                'description': j.get('description', '')[:600],
                'url': j.get('url', ''),
                'source': 'Arbeitnow',
                'tags': j.get('tags', []),
            }
            for j in jobs[:limit]
        ]
    except Exception:
        return []


def fetch_hn_hiring(job_title, limit=FETCH_LIMIT):
    try:
        # Find the latest "Ask HN: Who is hiring?" story
        search_resp = requests.get(
            'https://hn.algolia.com/api/v1/search',
            params={
                'query': 'Ask HN: Who is hiring?',
                'tags': 'story',
                'hitsPerPage': 1,
            },
            timeout=10,
        )
        hits = search_resp.json().get('hits', [])
        if not hits:
            return []

        story_id = hits[0].get('objectID', '')

        # Search comments in that story for matching jobs
        comments_resp = requests.get(
            'https://hn.algolia.com/api/v1/search',
            params={
                'query': job_title,
                'tags': f'comment,story_{story_id}',
                'hitsPerPage': limit,
            },
            timeout=10,
        )
        comments = comments_resp.json().get('hits', [])

        return [
            {
                'title': job_title or 'Software Engineer',
                'company': '',
                'location': 'Various',
                'description': c.get('comment_text', '')[:600],
                'url': f"https://news.ycombinator.com/item?id={c.get('objectID', '')}",
                'source': 'HN',
                'tags': [],
            }
            for c in comments
            if c.get('comment_text')
        ]
    except Exception:
        return []


def fetch_adzuna(job_title, location='', limit=FETCH_LIMIT):
    app_id = os.environ.get('ADZUNA_APP_ID', '')
    app_key = os.environ.get('ADZUNA_APP_KEY', '')

    if not app_id or not app_key:
        return []

    try:
        resp = requests.get(
            'https://api.adzuna.com/v1/api/jobs/gb/search/1',
            params={
                'app_id': app_id,
                'app_key': app_key,
                'what': job_title,
                'where': location,
                'results_per_page': limit,
            },
            timeout=10,
        )
        jobs = resp.json().get('results', [])

        return [
            {
                'title': j.get('title', ''),
                'company': j.get('company', {}).get('display_name', ''),
                'location': j.get('location', {}).get('display_name', ''),
                'description': j.get('description', '')[:600],
                'url': j.get('redirect_url', ''),
                'source': 'Adzuna',
                'tags': [],
            }
            for j in jobs
        ]
    except Exception:
        return []
