import unittest
from src.robots import RobotsGuard
from src.sitemap import parse_sitemap
from src.utils import normalize


class DiscoveryTests(unittest.TestCase):
    def test_longest_robots_rule(self):
        guard = RobotsGuard('User-agent: *\nAllow: /\nDisallow: /secret/\nAllow: /secret/public$', 'https://bestdrivingschool.us/robots.txt')
        self.assertFalse(guard.allowed('https://bestdrivingschool.us/secret/private'))
        self.assertTrue(guard.allowed('https://bestdrivingschool.us/secret/public'))
        self.assertFalse(guard.allowed('https://bestdrivingschool.us/secret/public/other'))

    def test_scope_and_encoded_private_paths(self):
        guard = RobotsGuard('User-agent: *\nAllow: /', '')
        for path in ['/api/test', '/enrollment/x', '/student/profile', '/product/index', '/%61dmin/x', '/foo/../teacher/x', '/login']:
            self.assertFalse(guard.allowed('https://bestdrivingschool.us' + path))
        self.assertFalse(guard.allowed('https://external.example/'))
        self.assertEqual(normalize('https://bestdrivingschool.us/faqs/?x=1#foo'), 'https://bestdrivingschool.us/faqs')

    def test_sitemap_namespace_and_index(self):
        kind, entries = parse_sitemap('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://bestdrivingschool.us/faqs</loc><lastmod>2026-09-01</lastmod></url></urlset>')
        self.assertEqual(kind, 'urlset')
        self.assertEqual(entries[0]['lastmod'], '2026-09-01')
        self.assertEqual(parse_sitemap('<sitemapindex><sitemap><loc>https://bestdrivingschool.us/child.xml</loc></sitemap></sitemapindex>')[0], 'sitemapindex')


if __name__ == '__main__':
    unittest.main()
