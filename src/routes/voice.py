"""Isolated server-to-server Retell token broker; no booking dependencies."""
import os
import secrets
import time
from collections import deque
import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def create_app(env=None, transport=None):
    env = os.environ if env is None else env
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    attempts = deque()
    lock = asyncio.Lock()

    def reply(body, status=200):
        return JSONResponse(body, status_code=status, headers={'Cache-Control': 'no-store'})

    @app.get('/api/health')
    async def health():
        return reply({'status': 'ok', 'service': 'best-driving-school-voice-broker'})

    @app.post('/api/retell/web-call')
    async def create_call(request: Request):
        secret = env.get('VOICE_PROXY_SECRET', '')
        supplied = request.headers.get('X-Voice-Proxy-Secret', '')
        if len(secret) < 32 or not secrets.compare_digest(secret.encode(), supplied.encode()):
            return reply({'error': 'unauthorized'}, 401)
        key, agent = env.get('RETELL_API_KEY'), env.get('RETELL_AGENT_ID')
        if not key or not agent:
            return reply({'error': 'service_unavailable'}, 503)
        # Global per-process spending guard; deploy one worker behind edge rate limits.
        async with lock:
            now = time.monotonic()
            while attempts and attempts[0] < now - 60:
                attempts.popleft()
            if len(attempts) >= 10:
                return reply({'error': 'rate_limited'}, 429)
            attempts.append(now)
        try:
            async with httpx.AsyncClient(timeout=15, transport=transport) as client:
                response = await client.post('https://api.retellai.com/v2/create-web-call',
                    headers={'Authorization': f'Bearer {key}'}, json={'agent_id': agent})
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict) or not isinstance(data.get('access_token'), str) or not data['access_token']:
                    raise ValueError('Invalid response')
                return reply({'access_token': data['access_token'], 'call_id': data.get('call_id')})
        except (httpx.HTTPError, ValueError, TypeError):
            return reply({'error': 'service_unavailable'}, 503)
    return app
