"""Límite de tamaño del cuerpo HTTP para reducir riesgo de agotamiento de memoria."""
from __future__ import annotations

from starlette.responses import JSONResponse


class MaxRequestBodySizeMiddleware:
    def __init__(self, app, max_bytes: int = 256 * 1024) -> None:
        if max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        messages = []
        total_bytes = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] == "http.request":
                total_bytes += len(message.get("body", b""))
                if total_bytes > self.max_bytes:
                    response = JSONResponse(
                        status_code=413,
                        content={"detail": "El cuerpo de la solicitud supera el límite permitido."},
                    )
                    await response(scope, receive, send)
                    return
                messages.append(message)
                if not message.get("more_body", False):
                    break
            else:
                messages.append(message)

        async def replay_receive():
            if messages:
                return messages.pop(0)
            return await receive()

        await self.app(scope, replay_receive, send)
