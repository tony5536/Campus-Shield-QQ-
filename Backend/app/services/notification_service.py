import asyncio
import json
from typing import Set

from fastapi import WebSocket

class NotificationManager:
    """
    Simple in-memory WebSocket manager. Suitable for single-process dev.
    Production: use Redis/WS broker or pubsub.
    """
    _sockets: Set[WebSocket] = set()

    @classmethod
    async def connect(cls, ws: WebSocket):
        await ws.accept()
        cls._sockets.add(ws)

    @classmethod
    async def disconnect(cls, ws: WebSocket):
        if ws in cls._sockets:
            cls._sockets.remove(ws)

    @classmethod
    async def broadcast(cls, message: dict):
        if not cls._sockets:
            return
        text = json.dumps(message)
        await asyncio.gather(*[ws.send_text(text) for ws in list(cls._sockets)])

    @classmethod
    def broadcast_now(cls, message: dict):
        """
        Fire-and-forget broadcast helper when called from sync code.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(cls.broadcast(message))
            else:
                loop.run_until_complete(cls.broadcast(message))
        except RuntimeError:
            # fallback: create new loop
            import asyncio as _asyncio
            _asyncio.run(cls.broadcast(message))

    @classmethod
    async def shutdown(cls):
        for ws in list(cls._sockets):
            try:
                await ws.close()
            except Exception:
                pass
        cls._sockets.clear()