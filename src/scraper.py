import logging
import time
from urllib.parse import urljoin
import requests
from config.settings import USER_AGENT, TIMEOUT, DELAY, RETRIES


class Fetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = USER_AGENT
        self.guard = None
        self.delay = DELAY
        self.last_request = 0
        self.audit = []

    def get(self, url, bootstrap=False):
        current = url
        redirects = []
        for hop in range(6):
            if not bootstrap and (self.guard is None or not self.guard.allowed(current)):
                raise ValueError('Blocked request: ' + current)
            response = None
            for attempt in range(RETRIES):
                time.sleep(max(0, self.delay - (time.monotonic() - self.last_request)))
                self.last_request = time.monotonic()
                try:
                    response = self.session.get(current, timeout=TIMEOUT, allow_redirects=False)
                    self.audit.append({'url': current, 'status_code': response.status_code,
                                       'attempt': attempt + 1})
                    logging.info('GET %s -> %s', current, response.status_code)
                    if response.status_code in (429, 500, 502, 503, 504):
                        if attempt + 1 < RETRIES:
                            retry_after = response.headers.get('Retry-After', '')
                            time.sleep(min(30, int(retry_after)) if retry_after.isdigit() else 2 ** attempt)
                            continue
                    break
                except requests.RequestException:
                    logging.exception('Request failure %s attempt %s', current, attempt + 1)
                    if attempt + 1 == RETRIES:
                        raise
                    time.sleep(2 ** attempt)
            if response.status_code in (301, 302, 303, 307, 308):
                target = urljoin(current, response.headers.get('Location', ''))
                # Never follow an unvalidated redirect, including robots bootstrap.
                from src.utils import normalize
                if not normalize(target, keep_query=True):
                    raise ValueError('Out-of-scope redirect: ' + target)
                if self.guard and not self.guard.allowed(target):
                    raise ValueError('Restricted redirect: ' + target)
                if bootstrap:
                    raise ValueError('Robots bootstrap redirect requires review: ' + target)
                redirects.append({'from': current, 'to': target, 'status_code': response.status_code})
                current = target
                continue
            response.raise_for_status()
            if not response.encoding or response.encoding.lower() == 'iso-8859-1':
                response.encoding = 'utf-8'
            return response, redirects
        raise ValueError('Too many redirects: ' + url)
