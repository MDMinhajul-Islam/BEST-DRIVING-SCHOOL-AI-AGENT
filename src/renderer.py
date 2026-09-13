from config.settings import ROOT
from src.utils import write_text


def sources(record):
    return ' · '.join(f"[{s['title'] or s['url']}]({s['url']})" for s in record.get('sources', []) if s['url'])


def fact_markdown(records):
    lines = []
    for record in records:
        section = record.get('section') or ' > '.join(record.get('heading_path', []))
        lines.append('### ' + (section or record.get('name') or 'Statement'))
        lines.append(record.get('text') or record.get('content') or record.get('description') or 'NOT FOUND')
        if record.get('requires_official_verification'):
            lines.append('**School statement — REQUIRES OFFICIAL SOURCE verification.**')
        lines.append('Source: ' + sources(record))
    return '\n\n'.join(lines)


def generate_knowledge(kb):
    prefix = '> Collected public website content. Manual review is required before Retell upload. Licensing statements require official Texas verification. Null fields mean NOT FOUND. Static content does not establish availability.\n\n'
    def save(name, title, content):
        write_text(ROOT / 'knowledge' / name, '# ' + title + '\n\n' + prefix + content + '\n')
    business = kb['business']
    content = 'Business: ' + business['name']['value'] + '\n\n'
    for record in business['contacts']:
        content += f"- **{record['field']}**: {record['value']}\n  Source: {sources(record)}\n"
    content += '\n## Office information\n\n' + '\n\n'.join(x['answer'] + '\n\nSource: ' + sources(x) for x in business['office_notes'])
    save('business_overview.md', 'Business overview', content)
    for category, name, title in [('adult','adult_services.md','Adult services'),('teen','teen_services.md','Teen services'),('road_test','road_test.md','Road test'),('parent_taught','parent_taught.md','Parent-taught services')]:
        relevant = kb['services'].get(category, [])
        content = ''
        for item in relevant:
            content += '## ' + item['name'] + '\n\n' + (item['description'] or 'NOT FOUND') + '\n\nSource: ' + sources(item) + '\n\n' + fact_markdown(item['sections']) + '\n\n'
        content += '\n## Related packages\n\n' + '\n'.join(f"- {c['name']}: {c['price'] or 'REQUIRES HUMAN REVIEW'} — [course]({c['canonical_course_url']})" for c in kb['courses'] if c['category']==category)
        save(name, title, content or 'NOT FOUND')
    content = '| Category | Course | Package | Current price | Original price |\n| --- | --- | --- | --- | --- |\n'
    for course in kb['courses']:
        content += f"| {course['category']} | {course['course_name']} | {course['name']} | {course['price'] or 'REQUIRES HUMAN REVIEW'} | {course['original_price'] or 'NOT FOUND'} |\n"
    for course in kb['courses']:
        content += '\n## ' + course['course_name'] + ' — ' + course['name'] + '\n\n'
        for field in ['description','course_description','package_description','price','original_price','promotion','included_hours','classroom_hours','driving_hours','observation_hours','number_of_sessions','session_duration','age_requirement','prerequisites','required_documents','included_services','eligibility','restrictions','next_steps','booking_or_purchase_url']:
            value = course.get(field)
            content += f"- **{field}**: {value if value is not None else 'NOT FOUND'}\n"
        content += '\nSource: ' + sources(course) + '\n'
        if course.get('requires_official_verification'):
            content += '\nPrerequisite/licensing wording requires official verification.\n'
    save('courses_and_pricing.md', 'Courses and pricing', content)
    save('faq.md', 'Frequently asked questions', '\n\n'.join('## ' + x['question'] + '\n\n' + x['answer'] + ('\n\n**REQUIRES OFFICIAL SOURCE verification.**' if x['requires_official_verification'] else '') + '\n\nSource: ' + sources(x) for x in kb['faqs']))
    save('policies.md', 'Public policies and customer-policy statements', fact_markdown(kb['policies']))
    content = ''
    for location in kb['locations']:
        content += '## ' + location['location_name'] + '\n\n'
        for field in ['address','phone','hours']:
            content += f"- **{field}**: {location.get(field) or 'NOT FOUND'}\n"
        content += '\nSource: ' + sources(location) + '\n\n'
        content += '\n\n'.join(x.get('answer') or x.get('content','') for x in location['location_specific_notes'])
        content += '\n\n### Services\n\n' + '\n'.join('- ' + x['name'] + ' — ' + sources(x) for x in location['services_available']) + '\n\n'
    save('locations.md', 'Locations and service areas', content)
    content = '| Source | Category | Sitemap lastmod | Scraped at | Status |\n| --- | --- | --- | --- | --- |\n'
    for meta in kb['source_pages']:
        content += f"| [{meta['title'] or meta['url']}]({meta['url']}) | {meta['page_category']} | {meta['sitemap_lastmod'] or 'NOT FOUND'} | {meta['scraped_at']} | {meta['status']} |\n"
    save('source_index.md', 'Source index', content)
    if not kb.get('regulatory_reference'):
        write_text(ROOT / 'knowledge/regulatory/README.md', '# Official Texas research — pending\n\nNo official regulatory facts have been collected in this phase. Review the flagged school statements in `data/structured/knowledge_base.json` against current DPS and TDLR primary sources before use. Sitemap lastmod is the site publisher’s metadata, not independent verification.\n')
    generate_retell_support(kb)


def generate_retell_support(kb):
    folder = ROOT / 'knowledge/retell_support'
    rows = [
        ('general_license_guidance','license_guide','School licensing statements; official verification pending'),
        ('adult_course','adult_sales','Adult six-hour online course; driving lessons are separate'),
        ('adult_driving_lesson','adult_sales','Adult private driving sessions and package options'),
        ('teen_driver_education','teen_sales','Teen classroom + driving + observation package'),
        ('teen_driving_only','teen_sales','Behind-the-wheel-only package; retain published requirements'),
        ('parent_taught','teen_sales','Parent-taught logged practice packages'),
        ('road_test','road_test_sales','Test-only and practice + test packages'),
        ('booking','booking','Static prerequisites and locations; live backend required'),
        ('reschedule','booking','Verified appointment and policy; backend required'),
        ('cancellation','booking','Service-specific policy review and backend required'),
        ('existing_student_support','student_support','FAQ and policies; private issues require verified system or human'),
        ('pricing_question','relevant sales persona','Use sourced package observations; conflicting prices must be reviewed'),
        ('location_question','global','Distinguish Plano office from surrounding service areas'),
        ('unknown','manual fallback design','Clarification or human assistance'),
    ]
    text = '# Router intent reference\n\nData organization for manual workflow design; this is not a production router prompt. Caller meaning, age and licensing stage will be considered in the later workflow.\n\n| Intent | Knowledge tag | Reference |\n| --- | --- | --- |\n'
    text += '\n'.join(f'| {intent} | {tag} | {note} |' for intent,tag,note in rows)
    text += '\n\nSources: ../source_index.md; ../../data/structured/courses.json and faq.json. Do not infer age from a caller asking for practice; do not interpret booking links as open slots.\n'
    write_text(folder / 'router_intent_reference.md', text)
    mapping = [
        ('Texas License Guide','license_guide',['regulatory/README.md','../data/structured/knowledge_base.json'],'School statements are provisional; current DPS/TDLR verification is required.'),
        ('Adult Sales Specialist','adult_sales',['adult_services.md','courses_and_pricing.md','locations.md'],'Separate online education from in-car lessons. Teen packages apply only after an intent change.'),
        ('Teen Sales Specialist','teen_sales',['teen_services.md','parent_taught.md','courses_and_pricing.md'],'Keep full education, driving-only and parent-taught practice distinct. Do not substitute adult packages.'),
        ('Road Test Sales Specialist','road_test_sales',['road_test.md','courses_and_pricing.md'],'Readiness and prerequisite wording require review. Passing/eligibility cannot be guaranteed.'),
        ('Booking Specialist','booking',['policies.md','locations.md','../docs/operational_data_requirements.md'],'Static knowledge supports qualification only. Check, create, find, reschedule and cancel require backend success.'),
        ('Existing Student Support','student_support',['faq.md','policies.md','business_overview.md'],'Account, course access, certificate and payment issues require identity verification or human assistance.'),
    ]
    text = '# Persona knowledge map\n\nGlobal business identity, contacts and locations may be shared across nodes. This document does not create nodes or prompts.\n'
    for name,tag,files,note in mapping:
        text += f'\n## {name}\n\nTag: `{tag}`\n\nReferences: ' + ', '.join('`'+f+'`' for f in files) + '\n\n' + note + '\n'
    text += '\n## Extraction tag caveat\n\nTags use deterministic text rules and are discovery aids. Review mixed-topic chunks before assigning them to a persona. Prefer individual structured records over uploading every page indiscriminately.\n'
    write_text(folder / 'persona_knowledge_map.md', text)
    variables = [
        ('caller_name','string','caller','Name provided in conversation'),('student_name','string','caller','May differ from caller'),
        ('age','integer or null','caller','Use explicit student age; no inference from package'),('student_or_parent','enum or null','caller','student, parent, other'),
        ('intent','enum','conversation','Use router intent groups'),('license_status','string or null','caller','Retain exact stated status'),
        ('permit_status','string or null','caller','Verify prerequisites when required'),('experience_level','string or null','caller','Readiness and learning needs'),
        ('recommended_service','service ID or null','conversation','Grounded service catalog'),('selected_package','package ID or null','conversation','Reference courses.json stable ID'),
        ('preferred_location','string or null','caller','Service area does not guarantee pickup'),('preferred_date','ISO date or null','caller','Resolve relative dates during live call'),
        ('preferred_time','string or null','caller','Preference, not availability'),('appointment_id','string or null','verified backend','Never generated by model'),
        ('support_issue','string or null','caller','Minimal issue summary'),('verification_status','enum','verified backend','unverified, verified, failed'),
        ('last_tool_result','object or null','backend','Success, conflict or failure'),('previous_intent','enum or null','conversation','Return after temporary intent switch'),
        ('knowledge_snapshot','string','configuration','Record reviewed source version'),('school_timezone','string','reviewed backend configuration','Scheduling timezone must be agreed with school')]
    text = '# Recommended shared variables\n\nProposal for manual Retell setup; nothing is implemented in Retell. Caller statements are not verified account facts. Preserve answered fields and ask again only to resolve contradiction or confirm critical actions.\n\n| Variable | Type | Source | Use |\n| --- | --- | --- | --- |\n'
    text += '\n'.join(f'| `{name}` | {kind} | {origin} | {use} |' for name,kind,origin,use in variables)
    text += '\n\nMinimize personal data and define retention during the operational integration phase. No passwords, payment card data or authentication tokens should be conversation variables.\n'
    existing = folder / 'recommended_shared_variables.md'
    if kb.get('regulatory_reference') and existing.exists():
        marker = '\n## Phase B proposed updates\n'
        previous = existing.read_text(encoding='utf-8')
        if marker in previous:
            text += marker + previous.split(marker, 1)[1]
    write_text(existing, text)
    text = '# Knowledge source map\n\n| Data | Source | Readiness |\n| --- | --- | --- |\n| Services, packages, prices | Public school sitemap pages | Extracted; manual review required |\n| FAQ and policy text | Public school pages | Preserved; review applicability and conflicts |\n| Locations and contacts | Public school content | Distinguish office from service areas |\n| Texas licensing requirements | DPS/TDLR official sources | Not collected; verification pending |\n| Availability, bookings | Approved school scheduling backend | REQUIRES API |\n| Enrollment, accounts, payments | Authenticated school system | REQUIRES AUTHENTICATED SYSTEM |\n\nEach structured record has `sources` with URL, title, page category, sitemap lastmod, scrape time, heading/section and evidence where practical. Package `observations` preserve page-specific values. Raw HTML and request audit are under `data/`. A sitemap date is not a freshness guarantee.\n\nSee [source index](../source_index.md), [quality report](../../reports/data_quality_report.md) and [coverage](../../reports/knowledge_coverage.md).\n'
    existing = folder / 'knowledge_source_map.md'
    if kb.get('regulatory_reference') and existing.exists():
        marker = '\n## Phase B authority separation\n'
        previous = existing.read_text(encoding='utf-8')
        if marker in previous:
            text += marker + previous.split(marker, 1)[1]
    write_text(existing, text)
    text = '# Unresolved information\n\n'
    for item in kb['unknowns']:
        text += f"- **{item['topic']} — {item['status']}**: {item['detail']}"
        if item.get('missing_fields'):
            text += ' Missing: ' + ', '.join(item['missing_fields'])
        text += '\n'
    text += f"\nDetected conflicts/possible conflicts: {len(kb['conflicts'])}. See [conflicts.json](../../data/structured/conflicts.json). Narrative prices are retained separately as unbound claims and must not be treated as package prices without review.\n"
    text += '\nNo complete service-specific refund, cancellation or rescheduling policy was found in the reviewed snapshot. A non-refundable processing charge does not settle these policies. See [manual review findings](../../reports/manual_review_findings.md).\n'
    write_text(folder / 'unresolved_information.md', text)
