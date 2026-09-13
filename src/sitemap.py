from xml.etree import ElementTree as ET
from src.utils import normalize


def parse_sitemap(text):
    root = ET.fromstring(text)
    kind = root.tag.rsplit('}', 1)[-1]
    if kind not in ('urlset', 'sitemapindex'):
        raise ValueError('Unexpected sitemap root: ' + kind)
    entries = []
    for child in root:
        fields = {x.tag.rsplit('}', 1)[-1]: x.text for x in child}
        if fields.get('loc'):
            entries.append({'url': fields['loc'].strip(), 'lastmod': fields.get('lastmod')})
    return kind, entries


def discover(fetcher, root_url, output_dir):
    pending, visited, pages, warnings = [root_url], set(), {}, []
    while pending:
        url = pending.pop(0)
        normalized = normalize(url)
        if not normalized or not fetcher.guard.allowed(url):
            warnings.append({'url': url, 'reason': 'blocked_sitemap'})
            continue
        if normalized in visited:
            continue
        if len(visited) >= 30:
            raise ValueError('Sitemap index safety limit exceeded')
        visited.add(normalized)
        response, _ = fetcher.get(url)
        from src.utils import filename
        (output_dir / (filename(normalized) + '.xml')).write_bytes(response.content)
        kind, entries = parse_sitemap(response.text)
        if kind == 'sitemapindex':
            pending.extend(x['url'] for x in entries)
        else:
            for entry in entries:
                key = normalize(entry['url'])
                if not key:
                    warnings.append({'url': entry['url'], 'reason': 'invalid_or_external_sitemap_url'})
                elif key in pages:
                    warnings.append({'url': key, 'reason': 'duplicate_sitemap_url'})
                else:
                    pages[key] = {'url': key, 'lastmod': entry['lastmod']}
    return list(pages.values()), warnings
