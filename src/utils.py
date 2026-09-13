import hashlib
import json
import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote
from config.settings import BASE_URL


def now():
    return datetime.now(timezone.utc).isoformat()


def tidy(value):
    value = re.sub(r'\s+', ' ', value or '').strip()
    return re.sub(r'\s+([.,;:!?])', r'\1', value)


def digest(value):
    if isinstance(value, str):
        value = value.encode('utf-8')
    return hashlib.sha256(value).hexdigest()


def normalize(url, base=BASE_URL, keep_query=False):
    parts = urlsplit(urljoin(base, url))
    if parts.scheme not in ('http', 'https') or parts.username or parts.password:
        return None
    if parts.hostname != urlsplit(BASE_URL).hostname or parts.port not in (None, 80, 443):
        return None
    # Decode before scope checks; collapse dot segments and duplicate slashes.
    path = unquote(parts.path)
    segments = []
    for segment in path.split('/'):
        if segment == '..':
            if segments:
                segments.pop()
        elif segment and segment != '.':
            segments.append(segment)
    path = '/' + '/'.join(segments)
    return urlunsplit(('https', parts.hostname, path, parts.query if keep_query else '', ''))


def filename(url):
    path = urlsplit(url).path.strip('/') or 'homepage'
    return re.sub(r'[^a-zA-Z0-9_-]', '-', path) + '-' + digest(url)[:8]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def write_text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')
