"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from appboot.asgi import fastapi_register_exception, get_asgi_application

os.environ.setdefault('APP_BOOT_SETTINGS_MODULE', 'mysite.settings')

application = get_asgi_application()
fastapi_register_exception(application)
