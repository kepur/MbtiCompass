from fastapi import APIRouter, WebSocket
from app.models.user_model import User
from app.models.base import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select



