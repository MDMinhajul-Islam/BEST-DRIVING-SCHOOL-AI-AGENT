import json
import re
from collections import Counter
from config.settings import ROOT
from src.utils import write_json, write_text


def validate(kb, links, duplicates, warnings, guard):
    errors = []
    successful = {x['url'] for x in kb['source_pages'] if x['status']=='success'}
    source_count = 0

    def walk(node, path='$'):
        nonlocal source_count
        if isinstance(node, dict):
            # Phase B reference uses a filename under `sources`, not a business
            # evidence array. Keep the business-source checks strict elsewhere.
            if 'sources' in node and path != '$.regulatory_reference':
                if not isinstance(node['sources'], list):
                    errors.append(path + ': sources must be an array')
                    return
                if not node['sources']:
                    errors.append(path + ': missing sources')
                for s in node['sources']:
                    if not isinstance(s, dict):
                        errors.append(path + ': source must be an object')
                        continue
                    source_count += 1
                    for field in ['url','title','page_category','sitemap_last_modified','scraped_at','section','evidence','content_hash']:
                        if field not in s:
                            errors.append(path + ': source missing ' + field)
                    if s.get('url') not in successful:
                        errors.append(path + ': source not a successful sitemap page')
            if node.get('information_type') == 'licensing_guidance' and node.get('requires_official_verification') is not True:
                errors.append(path + ': unflagged licensing statement')
            for key,value in node.items():
                if key != 'sources':
                    walk(value, path + '.' + key)
        elif isinstance(node,list):
            for index, value in enumerate(node):
                walk(value, path + '[' + str(index) + ']')
    walk(kb)
    audit = json.loads((ROOT / 'data/discovery/request_audit.json').read_text(encoding='utf-8'))
    restricted_requests = [x for x in audit if not x['url'].endswith('/robots.txt') and not guard.allowed(x['url'])]
    if restricted_requests:
        errors.append('Restricted URL was requested')
    for course in kb['courses']:
        if course['price'] is not None and not re.fullmatch(r'\$\d[\d,]*(?:\.\d{1,2})?', course['price']):
            errors.append('Malformed price for ' + course['name'])
        if course['price'] is not None and not any(x['price'] == course['price'] for x in course['observations']):
            errors.append('Price has no matching source observation: ' + course['name'])
    ids = [x['id'] for x in kb['courses']]
    if len(ids) != len(set(ids)):
        errors.append('Duplicate package IDs')
    pages = kb['source_pages']
    categories = Counter(x['page_category'] for x in pages if x['status']=='success')
    missing_categories = sorted(set(['homepage','faq','policy','service','course','location']) - set(categories))
    restricted_links = [x for x in links if x['restriction_reason'] and x['restriction_reason'] != 'out_of_scope_or_invalid_url']
    metrics = {'total_sitemap_urls': len(pages), 'successful_pages': len(successful),
        'failed_pages': sum(x['status']=='failed' for x in pages),
        'skipped_pages': sum(x['status']=='skipped' for x in pages),
        'redirected_pages': sum(bool(x.get('redirects')) for x in pages),
        'empty_pages': sum(x['status']=='success' and not x.get('cleaned_block_count') for x in pages),
        'pages_with_prices': sum(bool(x.get('detected_prices')) for x in pages),
        'pages_with_faqs': sum(bool(x.get('faq_count')) for x in pages),
        'location_pages': categories['location'], 'categories': dict(categories),
        'package_count': len(kb['courses']), 'faq_count': len(kb['faqs']),
        'policy_statement_count': len(kb['policies']), 'licensing_statement_count': len(kb['licensing_guidance']),
        'duplicate_records_merged': duplicates, 'conflicts': len(kb['conflicts']),
        'unbound_price_claims': len(kb['unbound_price_claims']),
        'restricted_links_discovered_not_crawled': len(restricted_links),
        'restricted_requests': len(restricted_requests), 'missing_categories': missing_categories,
        'extraction_warnings': warnings, 'source_references_validated': source_count,
        'validation_errors': errors,
        'changed_raw_pages': [{'url': x['url'], 'old_hash': x.get('previous_hash'), 'new_hash': x['content_hash']} for x in pages if x.get('content_changed')]}
    metrics['changed_cleaned_pages'] = [{'url': x['url'], 'old_hash': x.get('previous_cleaned_hash'), 'new_hash': x['cleaned_content_hash']} for x in pages if x.get('cleaned_content_changed')]
    write_json(ROOT / 'reports/validation.json', metrics)
    text = '# Data quality report\n\nAutomatically generated. Schema/source checks do not certify semantic completeness or business correctness. Manual review is required before Retell upload.\n\n| Check | Result |\n| --- | --- |\n'
    for key,value in metrics.items():
        if not isinstance(value,(dict,list)):
            text += f'| {key.replace("_"," ")} | {value} |\n'
    text += '\n## Page category coverage\n\n' + '\n'.join(f'- {k}: {v}' for k,v in categories.items())
    text += '\n\nMissing expected categories: ' + (', '.join(missing_categories) or 'None')
    text += '\n\n## Exact duplicate observations\n\n' + '\n'.join(f'- {k}: {v} merged, sources retained' for k,v in duplicates.items())
    text += '\n\nOnly exact repetitions are consolidated; no fuzzy removal of similar subject matter. Package observations retain all page-specific evidence.\n'
    text += '\n## Conflicts and narrative pricing\n\n'
    for conflict in kb['conflicts']:
        text += '- ' + conflict.get('entity_name', conflict.get('question','')) + ': ' + conflict['field'] + ' — ' + conflict['status'] + '\n'
    text += f"\n{len(kb['unbound_price_claims'])} narrative price claims remain unbound. These include FAQ answers, ranges, per-hour rates and promotional wording. They are preserved with evidence, but not automatically assigned as package prices. See `knowledge_base.json` and manual review findings.\n"
    text += '\n## Missing fields\n\nNull is retained for information not explicitly extracted; no inferred ages, total component sums, zero classroom hours, session counts or prerequisite guarantees. Details are in `knowledge/retell_support/unresolved_information.md`.\n'
    text += '\n## Request audit\n\n' + f'{len(restricted_links)} restricted links discovered but not crawled. {len(restricted_requests)} restricted requests. Out-of-domain links are recorded but never followed. Only allowed sitemap HTML pages are downloaded.\n'
    text += '\n## Extraction warnings and validation errors\n\n' + ('\n'.join('- '+str(x) for x in warnings + errors) or 'None')
    text += '\n\n## Failed/skipped pages\n\n' + ('\n'.join('- '+x['url']+': '+str(x['error']) for x in pages if x['status']!='success') or 'None')
    text += '\n\n## Changed pages\n\n' + ('\n'.join('- '+x['url']+'\n  old_hash: '+str(x['old_hash'])+'\n  new_hash: '+x['new_hash'] for x in metrics['changed_raw_pages']) or 'No changed raw hashes relative to the preceding collection.') + '\n'
    text += '\nRaw changes can include generated form tokens. Cleaned public content changes: ' + str(len(metrics['changed_cleaned_pages'])) + '.\n'
    text += '\n'.join('- '+x['url']+'\n  old_cleaned_hash: '+str(x['old_hash'])+'\n  new_cleaned_hash: '+x['new_hash'] for x in metrics['changed_cleaned_pages']) + '\n'
    write_text(ROOT / 'reports/data_quality_report.md', text)
    generate_coverage(kb)
    return metrics


def generate_coverage(kb):
    categories = kb['services']
    rows = [
        ('Business information','FOUND' if kb['business']['contacts'] else 'NOT FOUND','business.json; missing public email is not invented'),
        ('Adult services','FOUND' if categories['adult'] else 'NOT FOUND','adult_services.md'),
        ('Teen services','FOUND' if categories['teen'] else 'NOT FOUND','teen_services.md'),
        ('Road test','FOUND' if categories['road_test'] else 'NOT FOUND','road_test.md'),
        ('Parent taught','FOUND' if categories['parent_taught'] else 'NOT FOUND','parent_taught.md'),
        ('Pricing','REQUIRES HUMAN REVIEW' if kb['conflicts'] else 'FOUND','Sourced selector prices; narrative claims require review'),
        ('FAQ','FOUND' if kb['faqs'] else 'NOT FOUND','Exact Q&A; differing answers are retained'),
        ('Locations','PARTIAL','Four service-area pages; no invented Allen/Frisco/McKinney offices'),
        ('Terms','FOUND' if any(x['policy_type']=='terms' for x in kb['policies']) else 'NOT FOUND','Full cleaned terms statements'),
        ('Privacy','FOUND' if any(x['policy_type']=='privacy' for x in kb['policies']) else 'NOT FOUND','Full cleaned privacy statements'),
        ('Refund/cancellation rules','REQUIRES HUMAN REVIEW' if any(re.search(r'\brefunds?\b|\bcancellation\b|\brescheduling\b', x['text'], re.I) for x in kb['policies']) else 'NOT FOUND','The 3% non-refundable processing charge is not a complete refund/cancellation policy'),
        ('Scheduling policy','PARTIAL','Static instructions only; exact rules may need school clarification'),
        ('Licensing guidance','REQUIRES OFFICIAL SOURCE','School claims extracted and flagged; DPS/TDLR verification not done'),
        ('Booking availability','REQUIRES API','No live slots or embedded batch capacity in knowledge base'),
        ('Student account information','REQUIRES AUTHENTICATED SYSTEM','No private account data collected'),
        ('Payments, enrollment and booking actions','REQUIRES API','Separate authorized backend integration')]
    text = '# Knowledge coverage\n\nStatuses describe public extraction coverage, not production approval.\n\n| Topic | Status | Evidence / limitation |\n| --- | --- | --- |\n'
    text += '\n'.join(f'| {topic} | {status} | {note} |' for topic,status,note in rows)
    write_text(ROOT / 'reports/knowledge_coverage.md', text + '\n')
