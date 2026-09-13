from urllib.parse import urlsplit
import re


def page_category(url, title=''):
    path = urlsplit(url).path
    if path == '/':
        return 'homepage'
    if path.startswith('/services/'):
        return 'service'
    if path.startswith('/driving-courses/'):
        return 'course'
    if path.startswith('/driving-school-'):
        return 'location'
    if path in ('/faqs', '/faq'):
        return 'faq'
    if re.search(r'privacy|terms|policy', path, re.I):
        return 'policy'
    if 'frequently asked' in title.lower():
        return 'faq'
    return 'other'


def service_category(text):
    value = text.lower()
    if re.search(r'parent.?taught|log.driving|ptde', value):
        return 'parent_taught'
    if re.search(r'road.test|third.party|3rd.party', value):
        return 'road_test'
    if re.search(r'teen|7 & 7|24 hr classroom', value):
        return 'teen'
    if re.search(r'adult|6.hour|6 hours|six.hour', value):
        return 'adult'
    return 'other'


def persona_tags(text, category=None):
    tags = set()
    lower = text.lower()
    for pattern, tag in [(r'adult|18.over|18\+', 'adult_sales'),
                         (r'teen|parent.taught|ptde|classroom|observation', 'teen_sales'),
                         (r'road.test|driving.skills.test', 'road_test_sales'),
                         (r'book|schedul|appointment|cancel', 'booking'),
                         (r'certificate|refund|payment|account|access|enroll', 'student_support')]:
        if re.search(pattern, lower):
            tags.add(tag)
    if regulatory(lower):
        tags.add('license_guide')
    if category in ('homepage', 'location', 'policy') or not tags:
        tags.add('global')
    return sorted(tags)


def regulatory(text):
    direct = re.search(r'\bDPS\b|\bTDLR\b|\bITTD\b|\bITAD\b|\bPTDE\b|DE.?964|ADE.?1317|learner|permit|Texas.*(?:requir|licen)|Impact Texas|supervised.*hours', text, re.I)
    education_rule = (re.search(r'driver education|six.hour|6.hour', text, re.I) and
                      re.search(r'must|requir|applicant|generally|mandatory|age[sd]?\s+\d|first Texas', text, re.I))
    return bool(direct or education_rule)
