import asyncio
from typing import Any, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketState

from app.core.events import dispatcher
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from sqlalchemy import select

router = APIRouter()

async def get_user_from_token(token: str, db: AsyncSession) -> User:
    """Helper to get user from token for websocket auth."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject malformed"
        )
    stmt = select(User).where(User.id == user_id, User.is_active.is_(True))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or inactive"
        )
    return user

@router.websocket("/firehose")
async def firehose_ws(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Real-time WebSocket event firehose."""
    await websocket.accept()

    try:
        user = await get_user_from_token(token, db)
    except HTTPException as e:
        await websocket.close(code=1008, reason=e.detail)
        return

    # Queue to forward events from the dispatcher to the websocket
    queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

    async def event_callback(payload: Dict[str, Any]):
        await queue.put(payload)

    topic = f"user_{user.id}"
    dispatcher.subscribe(topic, event_callback)

    try:
        async def send_events():
            try:
                while True:
                    payload = await queue.get()
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_json(payload)
                    else:
                        break
            except Exception:
                pass

        send_task = asyncio.create_task(send_events())

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            send_task.cancel()

    finally:
        dispatcher.unsubscribe(topic, event_callback)
