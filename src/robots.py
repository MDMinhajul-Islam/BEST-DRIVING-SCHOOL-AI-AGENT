import re
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from config.settings import PRIVATE_PREFIXES, USER_AGENT
from src.utils import normalize


class RobotsGuard:
    """Fail closed on unavailable robots; scope exclusions supplement robots."""

    def __init__(self, text, url):
        self.parser = RobotFileParser(url)
        self.parser.parse(text.splitlines())
        # RobotFileParser uses first-match rules; add longest-match handling for
        # wildcard rules so the live site's Allow: / cannot mask Disallow entries.
        self.groups = []
        agents, rules = [], []
        saw_directive = False
        for raw in text.splitlines() + ['User-agent: __end__']:
            line = raw.split('#', 1)[0].strip()
            if ':' not in line:
                continue
            key, value = (x.strip() for x in line.split(':', 1))
            key = key.lower()
            if key == 'user-agent':
                if saw_directive:
                    self.groups.append((agents, rules))
                    agents, rules = [], []
                    saw_directive = False
                agents.append(value.lower())
            elif key in ('allow', 'disallow', 'crawl-delay') and agents:
                saw_directive = True
                if key in ('allow', 'disallow') and value:
                    rules.append((key, value))
        self.text = text

    def reason(self, url):
        normalized = normalize(url, keep_query=True)
        if not normalized:
            return 'out_of_scope_or_invalid_url'
        path = urlsplit(normalized).path
        if any(path.lower() == p.lower() or path.lower().startswith(p.lower() + '/')
               for p in PRIVATE_PREFIXES):
            return 'project_private_route_exclusion'
        ua = USER_AGENT.lower()
        matched = [(agents, rules) for agents, rules in self.groups
                   if any(a != '*' and a in ua for a in agents)]
        if matched:
            longest = max(len(a) for agents, _ in matched for a in agents if a != '*' and a in ua)
            matched = [(agents, rules) for agents, rules in matched if any(len(a)==longest and a in ua for a in agents)]
        if not matched:
            matched = [(a, r) for a, r in self.groups if '*' in a]
        target = path + ('?' + urlsplit(normalized).query if urlsplit(normalized).query else '')
        candidates = []
        for _, rules in matched:
            for kind, pattern in rules:
                end = pattern.endswith('$')
                literal = pattern[:-1] if end else pattern
                regex = '^' + re.escape(literal).replace(r'\*', '.*') + ('$' if end else '')
                if re.search(regex, target):
                    candidates.append((len(literal.replace('*', '')), kind == 'allow'))
        if candidates and not max(candidates)[1]:
            return 'robots_disallow'
        return None

    def allowed(self, url):
        return self.reason(url) is None

    def delay(self):
        return self.parser.crawl_delay(USER_AGENT) or self.parser.crawl_delay('*') or 0
