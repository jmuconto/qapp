# app/routers/__init__.py

# Make this directory a Python package

from . import users
from . import queue
from . import atendimentos

# Optional: expose routers for easier import in main.py
users_router = users.router
queue_router = queue.router
atendimentos_router = atendimentos.router
