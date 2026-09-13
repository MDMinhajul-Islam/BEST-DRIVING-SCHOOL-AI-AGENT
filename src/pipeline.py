import json
from config.settings import ROOT
from src.classifier import page_category
from src.cleaner import clean_html, markdown_blocks
from src.extractor import extract_page, source
from src.deduplicator import merge_sources, consolidate_packages, faq_conflicts
from src.utils import write_json, write_text, filename, now, digest, normalize


def process(metadata, guard, discovery_warnings):
    all_data = {k: [] for k in ['packages','faqs','policies','contacts','locations','services','links','licensing_guidance','price_claims','facts']}
    extraction_warnings = []
    for meta in metadata:
        meta['page_category'] = page_category(meta['url'], meta.get('title') or '')
        if meta['status'] != 'success':
            continue
        html = (ROOT / meta['raw_html']).read_bytes()
        blocks, warnings = clean_html(html)
        meta['cleaned_block_count'] = len(blocks)
        meta['cleaned_content_hash'] = digest(json.dumps(blocks, sort_keys=True, ensure_ascii=False))
        meta['cleaned_content_changed'] = (meta.get('previous_cleaned_hash') is not None and
            meta['previous_cleaned_hash'] != meta['cleaned_content_hash'])
        meta['extraction_warnings'] = warnings
        name = filename(meta['url'])
        write_json(ROOT / 'data/cleaned' / (name + '.json'), {'source': source(meta), 'blocks': blocks})
        write_text(ROOT / 'data/cleaned' / (name + '.md'), '<!-- Source: ' + meta['url'] + ' -->\n\n' + markdown_blocks(blocks))
        extracted = extract_page(html, meta, blocks)
        meta['detected_prices'] = len(extracted['packages']) + len(extracted['price_claims'])
        meta['faq_count'] = len(extracted['faqs'])
        for key in all_data:
            all_data[key].extend(extracted[key])
        extraction_warnings.extend({'url': meta['url'], 'warning': warning} for warning in warnings)
        if meta['page_category'] == 'course' and not extracted['packages']:
            extraction_warnings.append({'url': meta['url'], 'warning': 'No packages detected on course page; selector review required'})
        if not blocks:
            extraction_warnings.append({'url': meta['url'], 'warning': 'Empty cleaned content'})
    courses, conflicts = consolidate_packages(all_data['packages'])
    duplicates = {}
    for key, identity in [
        ('faqs', lambda x: (x['question'], x['answer'])),
        ('contacts', lambda x: (x['field'], x['value'])),
        ('policies', lambda x: (x['policy_type'], x['section'], x['text'])),
        ('facts', lambda x: x['content'] if len(x['content']) >= 60 else (x['source_url'],x['id'])),
        ('licensing_guidance', lambda x: x['content']),
        ('links', lambda x: (x['url'],x['text']))]:
        all_data[key], duplicates[key] = merge_sources(all_data[key], identity)
    conflicts.extend(faq_conflicts(all_data['faqs']))
    adult_terms = [x for x in all_data['policies'] if x['policy_type']=='terms' and 'eighteen (18)' in x['text'] and 'under' in x['text']]
    teen_services = [x for x in courses if x['category']=='teen']
    if adult_terms and teen_services:
        conflicts.append({'field': 'platform_age_policy_vs_teen_services',
            'entity_name': 'Terms age restrictions and teen services',
            'values': [{'value': x['text'], 'source_url': x['source_url'], 'sources': x['sources']} for x in adult_terms] +
                      [{'value': x['course_description'], 'source_url': x['source_url'], 'sources': x['sources']} for x in teen_services],
            'status': 'possible_conflict_requires_review',
            'note': 'Do not interpret website account terms as service eligibility. Ask the school to clarify parent/guardian enrollment applicability.'})
    broad_adult = [x for x in all_data['licensing_guidance'] if 'Adults applying for a first Texas license complete the six-hour' in x['content']]
    age_limited = [x for x in all_data['licensing_guidance'] if '25 or older' in x['content'] and 'six-hour' in x['content']]
    if broad_adult and age_limited:
        conflicts.append({'field': 'adult_education_applicability', 'entity_name': 'Adult education applicability wording',
            'values': [{'value': x['content'], 'source_url': x['source_url'], 'sources': x['sources']} for x in broad_adult + age_limited],
            'status': 'possible_conflict_requires_review',
            'note': 'The school corpus contains broad adult-course wording and age-limited wording. Do not resolve from model memory; official DPS/TDLR verification is required.'})
    for link in all_data['links']:
        reason = guard.reason(link['url'])
        link['crawl_status'] = 'discovered_but_not_crawled' if reason else 'public_link_not_followed'
        link['restriction_reason'] = reason
        link['is_sitemap_page'] = any(m['url'] == normalize(link['url']) for m in metadata)
    business = {'name': {'value': 'Best Driving School', 'sources': [source(m, 'Page title', m['title']) for m in metadata if m['status']=='success' and 'Best Driving School' in (m['title'] or '')]},
                'contacts': all_data['contacts'], 'business_hours': [x for x in all_data['contacts'] if x['field']=='hours_statement'],
                'office_notes': [x for x in all_data['faqs'] if 'office' in x['question'].lower()],
                'source_type': 'best_driving_school_website', 'review_status': 'pending_manual_review'}
    pricing = [{k: c.get(k) for k in ['id','name','course_name','category','price','discount_price','original_price','promotion','included_hours','description','included_services','pricing_conditions','source_url','source_last_modified','sources','observations','review_status']} for c in courses]
    services = {category: [x for x in all_data['services'] if x['category']==category] for category in ['adult','teen','parent_taught','road_test','other']}
    unknowns = [
        {'topic': 'Texas licensing requirements', 'status': 'REQUIRES OFFICIAL SOURCE', 'detail': 'School guidance is extracted but not independently verified against DPS/TDLR.'},
        {'topic': 'Live class schedule and appointment availability', 'status': 'REQUIRES API', 'detail': 'Embedded batches, dates and slot fields are excluded from static knowledge.'},
        {'topic': 'Bookings, enrollment records, payments and student accounts', 'status': 'REQUIRES AUTHENTICATED SYSTEM', 'detail': 'No account data or operational actions collected.'},
        {'topic': 'Refund, cancellation and rescheduling application', 'status': 'REQUIRES HUMAN REVIEW', 'detail': 'Extracted statements must be reviewed for service applicability and conflicts before automation.'},
        {'topic': 'Locations other than Plano', 'status': 'REQUIRES HUMAN REVIEW', 'detail': 'Service-area pages do not establish additional offices or guaranteed pickup points.'},
    ]
    missing = ['age_requirement','target_customer','included_hours','classroom_hours','driving_hours','observation_hours','number_of_sessions','session_duration','required_documents','eligibility','restrictions','next_steps']
    for course in courses:
        fields = [k for k in missing if course.get(k) is None]
        unknowns.append({'topic': course['name'], 'entity_id': course['id'], 'status': 'PARTIAL',
                         'missing_fields': fields, 'detail': 'Null means not explicitly extracted; do not infer a value.', 'source_urls': course['source_urls']})
    kb = {'schema_version': '1.0', 'generated_at': now(), 'review_status': 'pending_manual_review',
          'business': business, 'services': services, 'courses': courses, 'pricing': pricing,
          'locations': all_data['locations'], 'faqs': all_data['faqs'], 'policies': all_data['policies'],
          'licensing_guidance': all_data['licensing_guidance'], 'source_pages': metadata,
          'facts': all_data['facts'], 'unbound_price_claims': all_data['price_claims'],
          'conflicts': conflicts, 'unknowns': unknowns,
          'scope': {'retell_workflow_modified': False, 'operational_data_collected': False,
                    'requires_manual_review_before_upload': True}}
    for key, value in {'business': business, 'services': services, 'courses': courses, 'pricing': pricing,
                       'faq': kb['faqs'], 'policies': kb['policies'], 'locations': kb['locations'],
                       'links': all_data['links'], 'page_metadata': metadata, 'conflicts': conflicts,
                       'knowledge_base': kb}.items():
        write_json(ROOT / 'data/structured' / (key + '.json'), value)
    write_json(ROOT / 'reports/extraction_warnings.json', extraction_warnings)
    write_json(ROOT / 'reports/deduplication.json', duplicates)
    write_json(ROOT / 'reports/discovery_warnings.json', discovery_warnings)
    return kb, all_data['links'], duplicates, extraction_warnings
