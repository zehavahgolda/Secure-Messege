"""
main.py — Application entry point.

╔══════════════════════════════════════════════════════════════╗
║  THIS FILE IS COMPLETE — you do not need to change anything. ║
╚══════════════════════════════════════════════════════════════╝

This file does three things only:
  1. Creates the FastAPI app
  2. Sets up logging
  3. Registers the router from routes.py

All actual route logic lives in routes.py.
This separation is the standard pattern in production FastAPI projects.

HOW TO RUN:
  uvicorn server.main:app --reload

  Then open: http://localhost:8000/docs
"""

import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from .models import create_tables, get_db
from .routes import router
from .broadcaster import broadcaster
from .auth import require_auth_header_or_query


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logging.getLogger(__name__).info("starting application")
    create_tables()
    yield
    logging.getLogger(__name__).info("stopping application")


app = FastAPI(
    title="Secure Messenger — Stage 1",
    description="Authenticated, encrypted REST API for private messaging",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


# ---------------------------------------------------------------------------
# SSE Stream Endpoint — Real-time messaging
# ---------------------------------------------------------------------------
@app.get("/stream")
async def stream(
    db: Session = Depends(get_db),
    username: str = Depends(require_auth_header_or_query),
) -> EventSourceResponse:
    """
    Server-Sent Events (SSE) endpoint.
    
    Client connects and holds the connection open.
    When any message is published via broadcaster, this endpoint sends it.
    """
    
    async def event_generator() -> AsyncIterator[dict[str, str]]:
        # Subscribe to the broadcaster
        queue = await broadcaster.subscribe()
        logging.getLogger(__name__).info("sse connected user=%s", username)
        try:
            while True:
                # Wait for a message to be published
                message = await queue.get()
                # Send it to the client as SSE as JSON text
                yield {
                    "event": "message",
                    "data": json.dumps(message),
                }
        finally:
            # Clean up when client disconnects
            await broadcaster.unsubscribe(queue)
            logging.getLogger(__name__).info("sse disconnected user=%s", username)
    
    return EventSourceResponse(event_generator())
