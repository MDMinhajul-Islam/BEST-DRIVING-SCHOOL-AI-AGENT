import json
from src.utils import digest, tidy


def merge_sources(records, key):
    merged = {}
    duplicates = 0
    for item in records:
        identity = key(item)
        if identity not in merged:
            merged[identity] = item.copy()
            merged[identity]['sources'] = list(item.get('sources', []))
            continue
        duplicates += 1
        target = merged[identity]
        seen = {json.dumps(s, sort_keys=True, ensure_ascii=False) for s in target['sources']}
        for evidence in item.get('sources', []):
            encoded = json.dumps(evidence, sort_keys=True, ensure_ascii=False)
            if encoded not in seen:
                target['sources'].append(evidence)
                seen.add(encoded)
        if 'persona_tags' in item:
            target['persona_tags'] = sorted(set(target.get('persona_tags', [])) | set(item['persona_tags']))
        target['requires_official_verification'] = target.get('requires_official_verification', False) or item.get('requires_official_verification', False)
    return list(merged.values()), duplicates


def consolidate_packages(records):
    groups = {}
    for item in records:
        groups.setdefault(item['id'], []).append(item)
    output, conflicts = [], []
    for identity, items in groups.items():
        # Prefer richest course-page fields for descriptive display, while
        # collecting all source observations. Conflicting fields become null.
        ordered = sorted(items, key=lambda x: not any(s['page_category'] == 'course' for s in x['sources']))
        target = ordered[0].copy()
        target['sources'] = []
        target['observations'] = items
        target['source_urls'] = sorted({x['source_url'] for x in items})
        for item in ordered:
            for field in ('prerequisites', 'required_documents', 'included_services', 'pricing_conditions'):
                if item.get(field):
                    target[field] = list(target.get(field) or [])
                    for value in item[field]:
                        if value not in target[field]:
                            target[field].append(value)
            for evidence in item['sources']:
                if evidence not in target['sources']:
                    target['sources'].append(evidence)
        for field in ('price', 'original_price', 'classroom_hours', 'driving_hours', 'observation_hours', 'included_hours', 'number_of_sessions', 'session_duration', 'age_requirement'):
            values = {}
            for item in items:
                value = item.get(field)
                if value is not None:
                    values.setdefault(str(value), []).append({'value': value, 'source_url': item['source_url'], 'sources': item['sources']})
            if len(values) > 1:
                conflicts.append({'entity_id': identity, 'entity_name': target['name'], 'field': field,
                    'values': [v for observations in values.values() for v in observations],
                    'status': 'conflict_requires_review'})
                target[field] = None
                target['review_status'] = 'conflict_requires_review'
            elif values:
                target[field] = next(iter(values.values()))[0]['value']
        if target['review_status'] == 'conflict_requires_review':
            target['discount_price'] = None
        target['requires_official_verification'] = any(x['requires_official_verification'] for x in items)
        output.append(target)
    return output, conflicts


def faq_conflicts(records):
    groups = {}
    for record in records:
        groups.setdefault(tidy(record['question']).casefold(), []).append(record)
    conflicts = []
    for question, answers in groups.items():
        if len({x['answer'] for x in answers}) > 1:
            conflicts.append({'field': 'faq_answer', 'question': answers[0]['question'],
                'values': [{'value': x['answer'], 'source_url': x['source_url']} for x in answers],
                'status': 'possible_conflict_requires_review'})
    return conflicts
