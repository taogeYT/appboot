"""
URL configuration for mysite project.

Examples:
    from app import router1, router2
    routers = [router1, router2]
"""
from chat.views import router as chat
from fastapi import APIRouter
from polls.views import router as polls

root_router = APIRouter()
root_router.include_router(polls, prefix='/polls', tags=['polls'])
root_router.include_router(chat, prefix='/api', tags=['chat'])
