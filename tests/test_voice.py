"""Offline tests; never register a paid Retell call."""
import unittest
import httpx
from fastapi.testclient import TestClient
from src.routes.voice import create_app

class VoiceTests(unittest.TestCase):
    def setUp(self):
        self.env={'VOICE_PROXY_SECRET':'x'*32,'RETELL_API_KEY':'private-key','RETELL_AGENT_ID':'agent-test'}
        self.headers={'X-Voice-Proxy-Secret':'x'*32}
    def client(self, handler):
        return TestClient(create_app(self.env, httpx.MockTransport(handler)))
    def test_auth_required(self):
        with self.client(lambda r: self.fail('Must not contact Retell')) as c:
            self.assertEqual(c.post('/api/retell/web-call').status_code,401)
            self.assertEqual(c.get('/api/health').json(), {
                'status': 'ok', 'service': 'best-driving-school-voice-broker'})
    def test_incorrect_proxy_secret_rejected(self):
        with self.client(lambda r: self.fail('Must not contact Retell')) as c:
            self.assertEqual(c.post('/api/retell/web-call', headers={
                'X-Voice-Proxy-Secret': 'wrong-secret'}).status_code, 401)
    def test_missing_credentials_disabled(self):
        self.env.pop('RETELL_API_KEY')
        with self.client(lambda r: self.fail('Must not contact Retell')) as c:
            self.assertEqual(c.post('/api/retell/web-call',headers=self.headers).status_code,503)
    def test_missing_agent_disabled(self):
        self.env.pop('RETELL_AGENT_ID')
        with self.client(lambda r: self.fail('Must not contact Retell')) as c:
            self.assertEqual(c.post('/api/retell/web-call',headers=self.headers).status_code,503)
    def test_only_temporary_fields_returned(self):
        def handler(r):
            self.assertEqual(r.headers['authorization'],'Bearer private-key')
            self.assertEqual(r.read(),b'{"agent_id":"agent-test"}')
            return httpx.Response(201,json={'access_token':'temporary','call_id':'call-test','private_field':'hidden'})
        with self.client(handler) as c:
            r=c.post('/api/retell/web-call',headers=self.headers)
            self.assertEqual(r.json(),{'access_token':'temporary','call_id':'call-test'})
            self.assertEqual(r.headers['cache-control'],'no-store')
    def test_upstream_failure_sanitized(self):
        with self.client(lambda r:httpx.Response(500,text='private-key traceback')) as c:
            r=c.post('/api/retell/web-call',headers=self.headers)
            self.assertEqual(r.status_code,503)
            self.assertNotIn('private-key',r.text)
    def test_invalid_token_rejected(self):
        with self.client(lambda r:httpx.Response(201,json={'access_token':None})) as c:
            self.assertEqual(c.post('/api/retell/web-call',headers=self.headers).status_code,503)
    def test_rate_limit(self):
        with self.client(lambda r:httpx.Response(201,json={'access_token':'temporary'})) as c:
            for _ in range(10):self.assertEqual(c.post('/api/retell/web-call',headers=self.headers).status_code,200)
            self.assertEqual(c.post('/api/retell/web-call',headers=self.headers).status_code,429)
