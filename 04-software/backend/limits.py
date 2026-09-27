"""Bound uploads and admit one compute request per API process, without a queue."""
import asyncio
import threading

from starlette.responses import JSONResponse

from config import COMPUTE_PATHS, MAX_REQUEST_BYTES


class RequestLimitsMiddleware:
    def __init__(self, app):
        self.app = app
        self.slot = threading.BoundedSemaphore(1)

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)

        async def reject(code, detail, headers=None):
            await JSONResponse({'detail': detail}, status_code=code, headers=headers)(scope, receive, send)

        compute = scope['method'] == 'POST' and scope['path'].rstrip('/') in COMPUTE_PATHS
        max_bytes = MAX_REQUEST_BYTES if compute else 64_000
        acquired = compute and self.slot.acquire(blocking=False)
        if compute and not acquired:
            return await reject(429, 'solver is busy; retry shortly', {'Retry-After': '2'})
        try:
            headers = dict(scope['headers'])
            try:
                length = int(headers.get(b'content-length', b'0'))
                if length < 0:
                    raise ValueError
            except ValueError:
                return await reject(400, 'invalid Content-Length')
            if length > max_bytes:
                return await reject(413, 'request body exceeds the configured size limit')

            chunks, size = [], 0
            deadline = asyncio.get_running_loop().time() + 30
            while True:
                try:
                    message = await asyncio.wait_for(receive(), max(0, deadline - asyncio.get_running_loop().time()))
                except asyncio.TimeoutError:
                    return await reject(408, 'request body took too long to upload')
                if message['type'] == 'http.disconnect':
                    return
                chunk = message.get('body', b'')
                size += len(chunk)
                if size > max_bytes:
                    return await reject(413, 'request body exceeds the configured size limit')
                chunks.append(chunk)
                if not message.get('more_body', False):
                    break
            body = b''.join(chunks)
            chunks.clear()
            delivered = False

            async def replay():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {'type': 'http.request', 'body': body, 'more_body': False}
                return await receive()

            await self.app(scope, replay, send)
        finally:
            if acquired:
                self.slot.release()
