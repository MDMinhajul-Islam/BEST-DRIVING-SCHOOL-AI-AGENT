import re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from src.utils import tidy, digest, normalize
from src.classifier import page_category, persona_tags, service_category, regulatory

MONEY = re.compile(r'\$\s*\d[\d,]*(?:\.\d{1,2})?')
WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
         'eight': 8, 'ten': 10, 'fifteen': 15, 'thirty': 30}
ADDRESS = r'\b\d{1,6}\s+[A-Za-z0-9 .-]+?\s+(?:Pkwy|Parkway|Road|Rd|Street|St|Drive|Dr|Avenue|Ave|Boulevard|Blvd)\.?\s*(?:,?\s*(?:Suite|Ste|Unit|#)\s*[A-Za-z0-9-]+)?\s*,?\s*[A-Za-z .-]+,?\s+(?:Texas|TX)\s+\d{5}(?:-\d{4})?'


def source(meta, section=None, evidence=None):
    return {'url': meta['url'], 'title': meta['title'], 'page_category': meta['page_category'],
            'sitemap_last_modified': meta['sitemap_lastmod'], 'scraped_at': meta['scraped_at'],
            'section': section, 'evidence': evidence, 'content_hash': meta['content_hash']}


def money(text):
    match = MONEY.search(text or '')
    return match.group(0).replace(' ', '') if match else None


def hours(text, component):
    patterns = {
        'classroom': r'(\d+)\s*(?:hr|hours?)\s*(?:of\s+)?classroom',
        'driving': r'(\d+)\s*(?:hr|hours?)\s*(?:of\s+)?(?:driving|behind.the.wheel)',
        'observation': r'(\d+)\s*(?:hr|hours?)\s*(?:of\s+)?(?:in.car\s+)?observation',
    }
    match = re.search(patterns[component], text, re.I)
    return int(match.group(1)) if match else None


def canonical_package(name):
    value = tidy(name).lower()
    if value in ('road test', 'road test only'):
        return 'road-test-only'
    if value in ('practice + road test', 'practice session + road test'):
        return 'practice-and-road-test'
    return re.sub(r'[^a-z0-9]+', '-', value).strip('-')


def packages(soup, meta):
    main = soup.select_one('main') or soup
    items = []
    containers = main.select('[data-pk]')
    for container in containers:
        chips = container.select('[data-pk-chip]')
        heading = container.select_one('h1,h3,h2')
        family = tidy(heading.get_text(' ', strip=True)) if heading else None
        if not family:
            h = container.find_previous(['h1','h2','h3'])
            family = tidy(h.get_text(' ', strip=True)) if h else meta['title']
        candidates = chips or [container]
        for chip in candidates:
            label = container.select_one('[data-pk-label]')
            name = chip.get('data-value') or (tidy(label.get_text(' ', strip=True)) if label else family)
            price = money(chip.get('data-price')) if chips else money((container.select_one('[data-pk-price]') or container).get_text(' ', strip=True))
            was_el = container.select_one('[data-pk-was]')
            original = money(chip.get('data-was')) if chips else (money(was_el.get_text(' ', strip=True)) if was_el else None)
            meta_el = container.select_one('[data-pk-meta]')
            description = chip.get('data-meta') if chips else (tidy(meta_el.get_text(' ',strip=True)) if meta_el else None)
            note = chip.get('data-note') if chips else None
            badge = chip.get('data-badge') if chips else None
            if not chips:
                badge_el = container.select_one('[data-pk-badge]:not([hidden])')
                badge = tidy(badge_el.get_text(' ', strip=True)) if badge_el else None
            link = chip.get('data-link') if chips else None
            if not link and meta['page_category'] == 'course':
                link = meta['url']
                if chips and chip.get('data-enroll-chip'):
                    link += '?option=' + chip['data-enroll-chip']
            if not link:
                relevant = container.select_one('a[href*="/driving-courses/"]')
                if relevant:
                    link = urljoin(meta['url'], relevant['href'])
            identity_url = normalize(link) if link else None
            if not identity_url:
                identity_url = meta['url']
            total = re.fullmatch(r'(\d+)\s+hours?', name or '', re.I)
            component_text = description or ''
            class_hours = hours(component_text, 'classroom')
            drive_hours = hours(component_text, 'driving')
            observe_hours = hours(component_text, 'observation')
            included_hours = int(total.group(1)) if total else None
            if included_hours is None:
                named_hours = re.search(r'(\d+)[ -]hours?', name or '', re.I)
                included_hours = int(named_hours.group(1)) if named_hours else None
            # Do not add component hours into an unsupported total.
            sessions = re.search(r'(\d+|one|two|three|four|five) sessions? of (\d+|two) hours?', component_text, re.I)
            count = (WORDS.get(sessions.group(1).lower()) or int(sessions.group(1))) if sessions else None
            duration = (WORDS.get(sessions.group(2).lower()) or int(sessions.group(2))) if sessions else None
            evidence = {k: v for k,v in chip.attrs.items() if k.startswith('data-')} if chips else {'displayed_label': name, 'displayed_price': price, 'displayed_original_price': original, 'displayed_meta': description}
            category = service_category(identity_url + ' ' + (family or ''))
            items.append({'id': digest(identity_url + '|' + canonical_package(name))[:20],
                'name': name, 'course_name': family, 'category': category, 'target_customer': None,
                'age_requirement': None, 'description': description or None, 'included_hours': included_hours,
                'classroom_hours': class_hours, 'driving_hours': drive_hours, 'observation_hours': observe_hours,
                'number_of_sessions': count, 'session_duration': duration,
                'session_duration_unit': 'hours' if duration else None,
                'price': price, 'discount_price': price if original else None, 'original_price': original,
                'promotion': chip.get('data-save') or chip.get('data-badge') or None if chips else None,
                'marketing_labels': [tidy(badge)] if badge else [],
                'prerequisites': [tidy(note)] if note else None, 'required_documents': None,
                'eligibility': None, 'restrictions': None, 'next_steps': None,
                'booking_or_purchase_url': link, 'canonical_course_url': identity_url,
                'source_url': meta['url'], 'source_last_modified': meta['sitemap_lastmod'],
                'sources': [source(meta, family, evidence)],
                'persona_tags': persona_tags((family or '') + ' ' + name + ' ' + (note or '')),
                'requires_official_verification': bool(note and regulatory(note)),
                'review_status': 'pending_manual_review'})
    return items


def extract_faq(soup, meta):
    output = []
    for panel in soup.select('main [data-faq-panel]'):
        parent = panel.parent
        question_el = parent.select_one('[data-faq] h3')
        if question_el is None:
            question_el = parent.select_one('h3,summary')
        if question_el is None:
            continue
        question = tidy(question_el.get_text(' ', strip=True)).rstrip(' ▾')
        answer = tidy(panel.get_text(' ', strip=True))
        if not question or not answer or not question.endswith('?'):
            continue
        h2 = parent.find_previous('h2')
        section = tidy(h2.get_text(' ', strip=True)) if h2 else None
        output.append({'id': digest(question + '\n' + answer)[:20], 'question': question,
            'answer': answer, 'category': service_category((section or '') + ' ' + question),
            'persona_tags': persona_tags(question + ' ' + answer), 'source_url': meta['url'],
            'sources': [source(meta, section, {'question': question, 'answer': answer})],
            'requires_official_verification': regulatory(question + ' ' + answer),
            'review_status': 'pending_manual_review'})
    return output


def extract_page(html, meta, blocks):
    soup = BeautifulSoup(html, 'lxml')
    main = soup.select_one('main') or soup
    h1 = main.select_one('h1')
    title = tidy(h1.get_text(' ', strip=True)) if h1 else meta['title']
    result = {'packages': packages(soup, meta), 'faqs': extract_faq(soup, meta),
              'policies': [], 'contacts': [], 'locations': [], 'services': [], 'links': [],
              'licensing_guidance': [], 'price_claims': [], 'facts': []}
    # Contacts in repeated footer/header are harvested as facts with multiple sources,
    # then removed from cleaned body content.
    for anchor in soup.select('a[href^="tel:"],a[href^="mailto:"]'):
        kind = 'phone' if anchor['href'].startswith('tel:') else 'email'
        value = anchor['href'].split(':',1)[1]
        result['contacts'].append({'field': kind, 'value': value, 'source_url': meta['url'],
                                  'sources': [source(meta, 'Public contact link', str(anchor))]})
    footer = soup.select_one('footer')
    address_pattern = ADDRESS
    contact_text = tidy(footer.get_text(' ',strip=True)) if footer else tidy(main.get_text(' ',strip=True))
    address_match = re.search(address_pattern, contact_text, re.I)
    if address_match:
        result['contacts'].append({'field': 'address', 'value': address_match.group(0),
            'source_url': meta['url'], 'sources': [source(meta, 'Public contact address', address_match.group(0))]})
    for anchor in soup.select('a[href]'):
        href = anchor['href']
        if href.startswith(('#', 'javascript:', 'tel:', 'mailto:')):
            continue
        absolute = urljoin(meta['url'], href)
        if urlsplit(absolute).scheme not in ('http','https'):
            continue
        result['links'].append({'url': absolute, 'text': tidy(anchor.get_text(' ',strip=True)),
            'source_url': meta['url'], 'sources': [source(meta, 'Link', {'href': href, 'text': tidy(anchor.get_text(' ',strip=True))})]})
    for index, block in enumerate(blocks):
        if block['type'] == 'heading':
            continue
        text = block['text']
        section = ' > '.join(block['heading_path']) or title
        fact = {'id': digest(meta['url'] + '|' + str(index) + '|' + text)[:20], 'content': text,
            'block_type': block['type'], 'heading_path': block['heading_path'],
            'persona_tags': persona_tags(text + ' ' + section, meta['page_category']),
            'source_url': meta['url'], 'sources': [source(meta, section, text)],
            'requires_official_verification': regulatory(text), 'review_status': 'pending_manual_review'}
        if 'rows' in block:
            fact['rows'] = block['rows']
        result['facts'].append(fact)
        if regulatory(text):
            result['licensing_guidance'].append({**fact, 'information_type': 'licensing_guidance',
                'source_type': 'best_driving_school_website', 'requires_official_verification': True})
        if MONEY.search(text):
            result['price_claims'].append({**fact, 'detected_amounts': MONEY.findall(text),
                'binding_status': 'unbound_text_claim_requires_review'})
        if meta['page_category'] == 'policy' or re.search(r'refund|non.refundable|cancel|reschedul|service charge|late fee|no.show', text, re.I):
            result['policies'].append({**fact, 'policy_type': ('privacy' if 'privacy' in meta['url'] else 'terms')
                if meta['page_category'] == 'policy' else 'customer_policy_statement',
                'section': section, 'text': text, 'legal_interpretation': False})
        if re.search(r'(?:9\s*(?:am|a\.m\.)\s*[–-]\s*7\s*(?:pm|p\.m\.))|(?:9:00.*7:00)|helpline 24/7', text, re.I):
            result['contacts'].append({'field': 'hours_statement', 'value': text,
                'source_url': meta['url'], 'sources': [source(meta, section, text)]})
    description = main.select_one('.pp-answer, .bd-course__lead p, .bd-hero__body p')
    if meta['page_category'] == 'service':
        result['services'].append({'id': digest(meta['url'])[:20], 'name': title,
            'category': service_category(meta['url']),
            'description': tidy(description.get_text(' ',strip=True)) if description else None,
            'sections': result['facts'], 'source_url': meta['url'], 'sources': [source(meta, title, title)],
            'persona_tags': persona_tags(title), 'review_status': 'pending_manual_review'})
    if meta['page_category'] == 'course':
        needs = main.select_one('.pp-facts__col:nth-of-type(2)')
        need_text = tidy(needs.get_text(' ',strip=True)).removeprefix('What you need').strip() if needs else None
        included = [tidy(x.get_text(' ',strip=True)) for x in main.select('.pp-facts__col:first-child li')]
        lead = tidy(description.get_text(' ',strip=True)) if description else None
        for package in result['packages']:
            package['course_description'] = lead
            package['included_services'] = included or None
            detail_panel = next((p for p in main.select('[data-pk-panel]') if canonical_package(p['data-pk-panel']) == canonical_package(package['name'])), None)
            package['package_description'] = tidy(detail_panel.get_text(' ',strip=True)) if detail_panel else None
            if detail_panel:
                package['sources'].append(source(meta, 'Package details: ' + package['name'], package['package_description']))
            if need_text:
                package['prerequisites'] = list(dict.fromkeys((package['prerequisites'] or []) + [need_text]))
                package['sources'].append(source(meta, 'What you need', need_text))
                package['requires_official_verification'] = regulatory(need_text)
                if re.search(r'certificate|document', need_text, re.I):
                    package['required_documents'] = [need_text]
                age_match = re.search(r'(?:aged?\s+|drivers\s+)(\d+)(?:\s+and\s+|\s+or\s+)(over|older)', (lead or '') + ' ' + need_text, re.I)
                if age_match:
                    package['age_requirement'] = age_match.group(0)
                    package['target_customer'] = age_match.group(0)
            age_evidence = package['age_requirement']
            if age_evidence:
                package['sources'].append(source(meta, 'Course age statement', age_evidence))
            for component in ('classroom','driving','observation'):
                value = hours(' '.join(included), component)
                if package[component + '_hours'] is None and value is not None:
                    package[component + '_hours'] = value
            package['sources'].append(source(meta, "What's included", included))
            # Preserve policy statements separately; no inferred restrictions.
            package['pricing_conditions'] = [x for x in result['policies'] if 'service charge' in x['text'].lower()] or None
    if meta['page_category'] == 'location':
        city = urlsplit(meta['url']).path.removeprefix('/driving-school-').title()
        if city.lower() == 'mckinney':
            city = 'McKinney'
        office_faq = next((x for x in result['faqs'] if 'office' in x['question'].lower()), None)
        local_addresses = []
        for node in main.select('address'):
            local_addresses.append(tidy(node.get_text(' ',strip=True)))
        address = local_addresses[0] if local_addresses else None
        if city == 'Plano' and address is None:
            # The actual office address is shown on this page. Use its verbatim
            # span sequence, not an address inferred from the location URL.
            match = re.search(address_pattern, tidy(main.get_text(' ',strip=True)), re.I)
            address = match.group(0) if match else None
        relevant = [x for x in result['facts'] if city.lower() in x['content'].lower() or 'Plano' in x['content']]
        local_hours = [x for x in result['contacts'] if x['field'] == 'hours_statement']
        result['locations'].append({'location_name': city, 'address': address,
            'phone': next((x['value'] for x in result['contacts'] if x['field'] == 'phone'), None),
            'hours': [x['value'] for x in local_hours] or None,
            'services_available': [{'name': tidy(h.get_text(' ',strip=True)), 'sources': [source(meta, title, tidy(h.get_text(' ',strip=True)))]}
                for h in main.select('h3') if re.search(r'Teen Driving|Adult Driving|Parent.Taught|Third.Party Road', h.get_text(' ',strip=True), re.I)],
            'location_specific_notes': [office_faq] if office_faq else relevant,
            'source_url': meta['url'], 'sources': [source(meta, title, {'address': address, 'phone': next((x['value'] for x in result['contacts'] if x['field'] == 'phone'), None)})],
            'review_status': 'pending_manual_review'})
    return result
