"""
URL configuration for mysite project.

Examples:
    from app import router1, router2
    routers = [router1, router2]
"""
from fastapi import APIRouter
from polls.views import router

root_router = APIRouter()
root_router.include_router(router, prefix='/polls', tags=['polls'])
