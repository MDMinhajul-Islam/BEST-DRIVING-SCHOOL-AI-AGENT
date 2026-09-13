import argparse
import json
from config.settings import ROOT, BASE_URL
from src.collector import collect
from src.robots import RobotsGuard
from src.pipeline import process
from src.renderer import generate_knowledge
from src.validator import validate


def main():
    parser = argparse.ArgumentParser(description='Public website knowledge preparation. Does not configure Retell.')
    parser.add_argument('--offline', action='store_true', help='Re-extract saved successful raw pages without any network requests')
    args = parser.parse_args()
    if args.offline:
        metadata = json.loads((ROOT / 'data/structured/page_metadata.json').read_text(encoding='utf-8'))
        guard = RobotsGuard((ROOT / 'data/discovery/robots.txt').read_text(encoding='utf-8'), BASE_URL + 'robots.txt')
        warnings = json.loads((ROOT / 'data/discovery/discovery_warnings.json').read_text(encoding='utf-8'))
    else:
        metadata, guard, warnings = collect()
    kb, links, duplicates, extraction_warnings = process(metadata, guard, warnings)
    generate_knowledge(kb)
    result = validate(kb, links, duplicates, extraction_warnings, guard)
    print(json.dumps({k:result[k] for k in ['total_sitemap_urls','successful_pages','failed_pages','skipped_pages','package_count','faq_count','conflicts','restricted_requests','validation_errors']}, indent=2))
    if result['validation_errors']:
        raise SystemExit(2)
    if result['failed_pages'] or result['empty_pages']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
