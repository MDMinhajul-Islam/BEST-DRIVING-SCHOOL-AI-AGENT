import logging
import json
from bs4 import BeautifulSoup
from config.settings import ROOT, BASE_URL, DELAY
from src.scraper import Fetcher
from src.robots import RobotsGuard
from src.sitemap import discover
from src.utils import now, digest, filename, write_json


def collect():
    for folder in ['logs', 'data/raw_html', 'data/discovery', 'data/cleaned', 'data/structured', 'reports']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=ROOT / 'logs/scraper.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s', encoding='utf-8')
    old_path = ROOT / 'data/structured/page_metadata.json'
    old = {x['url']: x for x in json.loads(old_path.read_text(encoding='utf-8'))} if old_path.exists() else {}
    fetcher = Fetcher()
    robots, _ = fetcher.get(BASE_URL + 'robots.txt', bootstrap=True)
    if '<html' in robots.text.lower() or 'user-agent:' not in robots.text.lower():
        raise ValueError('Invalid robots.txt; collection stopped without scraping pages')
    (ROOT / 'data/discovery/robots.txt').write_bytes(robots.content)
    fetcher.guard = RobotsGuard(robots.text, BASE_URL + 'robots.txt')
    fetcher.delay = max(DELAY, fetcher.guard.delay())
    pages, warnings = discover(fetcher, BASE_URL + 'sitemap.xml', ROOT / 'data/discovery')
    metadata = []
    for entry in pages:
        url = entry['url']
        record = {'url': url, 'sitemap_lastmod': entry['lastmod'], 'scraped_at': now(),
                  'status_code': None, 'title': None, 'content_hash': None, 'raw_html': None,
                  'redirects': [], 'status': 'pending', 'error': None}
        reason = fetcher.guard.reason(url)
        if reason:
            record.update(status='skipped', error=reason)
        else:
            try:
                response, redirects = fetcher.get(url)
                if 'html' not in response.headers.get('Content-Type', '').lower():
                    raise ValueError('Non-HTML sitemap page')
                raw_path = ROOT / 'data/raw_html' / (filename(url) + '.html')
                raw_path.write_bytes(response.content)
                soup = BeautifulSoup(response.content, 'lxml')
                content_hash = digest(response.content)
                previous = old.get(url, {}).get('content_hash')
                record.update(status='success', status_code=response.status_code,
                              title=soup.title.get_text(' ', strip=True) if soup.title else None,
                              content_hash=content_hash, raw_html=raw_path.relative_to(ROOT).as_posix(),
                              final_url=response.url, redirects=redirects,
                              previous_hash=previous,
                              previous_cleaned_hash=old.get(url, {}).get('cleaned_content_hash'),
                              content_changed=previous is not None and previous != content_hash)
            except Exception as exc:
                record.update(status='failed', error=str(exc), status_code=getattr(getattr(exc, 'response', None), 'status_code', None))
                logging.exception('Failed sitemap page %s', url)
        metadata.append(record)
        print(record['status'], url, flush=True)
    write_json(ROOT / 'data/structured/page_metadata.json', metadata)
    write_json(ROOT / 'data/discovery/sitemap_pages.json', pages)
    write_json(ROOT / 'data/discovery/discovery_warnings.json', warnings)
    write_json(ROOT / 'data/discovery/request_audit.json', fetcher.audit)
    write_json(ROOT / 'data/discovery/collection_manifest.json', {'collected_at': now(), 'user_agent': fetcher.session.headers['User-Agent'], 'request_delay': fetcher.delay})
    return metadata, fetcher.guard, warnings


if __name__ == '__main__':
    collect()
