from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise
import yaml

# Import routers
from app.routers import queue, atendimentos, users
from app.utils import send_email

app = FastAPI(title="qApp – Queue Management SaaS via Email")
templates = Jinja2Templates(directory="app/templates")

# Load config
with open("app/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Include routers
app.include_router(queue.router, prefix="/queue", tags=["queue"])
app.include_router(atendimentos.router, prefix="/atendimentos", tags=["atendimentos"])
app.include_router(users.router, prefix="/users", tags=["users"])

# Dashboard route
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Render main dashboard with all queues and pending atendimentos.
    """
    from app.models import Queue, Atendimento, AtendimentoStatus
    queues = await Queue.all().prefetch_related("atendimentos")
    queue_data = []
    for q in queues:
        pending = await q.atendimentos.filter(status=AtendimentoStatus.AGUARDANDO)
        queue_data.append({"queue": q, "pending": pending})
    return templates.TemplateResponse("fila.html", {"request": request, "queues": queue_data})

# Example background email task
@app.post("/notify/{email}")
async def notify(email: str, message: str, background_tasks: BackgroundTasks):
    """
    Send a test notification via email in the background.
    """
    background_tasks.add_task(send_email, to_email=email, subject="qApp Notification", content=message)
    return {"status": "email scheduled"}

# Tortoise ORM setup
register_tortoise(
    app,
    db_url=config.get("database_url", "sqlite://db.sqlite3"),
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
