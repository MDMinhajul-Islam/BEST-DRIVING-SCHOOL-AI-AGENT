from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://bestdrivingschool.us/'
USER_AGENT = 'BestDrivingSchoolKnowledgeCollector/1.0'
TIMEOUT = 30
DELAY = 0.5
RETRIES = 3
# Additional project scope exclusions even if robots.txt later permits them.
PRIVATE_PREFIXES = (
    '/_ignition', '/admin', '/api', '/classSchedule', '/courses', '/create',
    '/employee', '/enrollment', '/guest', '/home', '/login', '/order',
    '/password', '/product', '/products', '/queries', '/student', '/teacher',
    '/update', '/upload', '/view',
)
