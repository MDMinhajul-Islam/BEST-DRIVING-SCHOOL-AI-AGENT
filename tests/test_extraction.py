import unittest
from unittest.mock import Mock
from src.cleaner import clean_html, markdown_blocks
from src.extractor import extract_page, extract_faq, packages
from src.deduplicator import consolidate_packages
from src.robots import RobotsGuard
from src.scraper import Fetcher
from src.classifier import regulatory
from bs4 import BeautifulSoup


def metadata(url='https://bestdrivingschool.us/driving-courses/adult-driving-sessions'):
    return {'url': url, 'title': 'Adult lessons', 'page_category': 'course',
            'sitemap_lastmod': None, 'scraped_at': '2026-09-13T00:00:00+00:00', 'content_hash': 'fixture'}


HTML = '''<html><head><title>Adult lessons</title></head><body><nav>Repeated menu</nav><main>
<div data-pk><h1>Adult Driving Lessons</h1><p>Private lessons for drivers 18 and over.</p>
<button data-pk-chip data-enroll-chip="11" data-value="4 hours" data-price="$246" data-was="$270"
data-meta="$61.50 per hour · two sessions of two hours">4 hours</button>
<button data-pk-chip data-enroll-chip="12" data-value="6 hours" data-price="$328"
data-meta="three sessions of two hours">6 hours</button>
<span data-pk-price>$246</span><span data-pk-label>4 hours</span>
<div data-pk-panel="4 hours" hidden><p>Beginner training in two driving sessions.</p></div>
<div class="pp-facts"><div class="pp-facts__col"><h2>What's included</h2><ul><li>Dual-control vehicle</li></ul></div>
<div class="pp-facts__col"><h2>What you need</h2><p>A valid Texas learner permit or driver license.</p></div></div></div>
<section id="batches"><h2>Upcoming classroom batches</h2><p>Only 2 spots left</p></section>
<section id="enroll"><form><input name="student_name" value="never extract"><select><option>12:00 open</option></select></form></section>
<h2>Documents</h2><table><tr><th>Item</th><th>Rule</th></tr><tr><td>Permit</td><td>Bring original</td></tr></table>
<article class="bd-faq__item"><button data-faq><h3>Does this include online education?</h3></button>
<div data-faq-panel hidden><p>No. Online education is booked separately.</p></div></article>
<article><button data-faq>Details</button><div data-faq-panel><p>Extra inclusions.</p></div></article>
</main><footer>Repeated footer</footer></body></html>'''


class ExtractionTests(unittest.TestCase):
    def test_age_limited_education_statements_are_flagged(self):
        self.assertTrue(regulatory('First-time applicants ages 18 through 24 generally must complete a six-hour adult driver education course. Adults age 25 or older are generally not required to take it.'))

    def test_cleaning_preserves_packages_hidden_answers_and_table(self):
        blocks, warnings = clean_html(HTML)
        output = markdown_blocks(blocks)
        for text in ['$246', '$270', '$328', 'Package details: 4 hours',
                     'Online education is booked separately.', '| Permit | Bring original |']:
            self.assertIn(text, output)
        for text in ['never extract','12:00 open','Only 2 spots left','Repeated menu','Repeated footer']:
            self.assertNotIn(text, output)
        self.assertEqual(warnings, [])

    def test_options_not_just_selected_price_and_no_inference(self):
        blocks, _ = clean_html(HTML)
        data = extract_page(HTML, metadata(), blocks)
        self.assertEqual([(x['name'],x['price']) for x in data['packages']], [('4 hours','$246'),('6 hours','$328')])
        four = data['packages'][0]
        self.assertEqual(four['original_price'], '$270')
        self.assertEqual(four['number_of_sessions'], 2)
        self.assertEqual(four['session_duration'], 2)
        self.assertIsNone(four['observation_hours'])
        self.assertTrue(four['requires_official_verification'])
        self.assertIn('Beginner training', four['package_description'])
        self.assertEqual(len(data['faqs']), 1)

    def test_price_conflict_is_not_silently_chosen(self):
        original = packages(BeautifulSoup(HTML, 'lxml'), metadata())[0]
        other = dict(original, price='$999', source_url='https://bestdrivingschool.us/services/driving-lessons-for-adults')
        output, conflicts = consolidate_packages([original,other])
        self.assertIsNone(output[0]['price'])
        self.assertEqual(conflicts[0]['field'], 'price')
        self.assertEqual(len(output[0]['observations']), 2)
        self.assertEqual(output[0]['review_status'], 'conflict_requires_review')

    def test_blocked_redirect_never_requests_destination(self):
        fetcher = Fetcher()
        fetcher.delay = 0
        fetcher.guard = RobotsGuard('User-agent: *\nAllow: /', '')
        response = Mock(status_code=302, headers={'Location':'/enrollment/private'})
        fetcher.session.get = Mock(return_value=response)
        with self.assertRaisesRegex(ValueError, 'Restricted redirect'):
            fetcher.get('https://bestdrivingschool.us/faqs')
        self.assertEqual(fetcher.session.get.call_count, 1)

    def test_specific_empty_disallow_group(self):
        guard = RobotsGuard('User-agent: BestDrivingSchoolKnowledgeCollector\nDisallow:\n\nUser-agent: *\nDisallow: /faqs', '')
        self.assertTrue(guard.allowed('https://bestdrivingschool.us/faqs'))


if __name__ == '__main__':
    unittest.main()
