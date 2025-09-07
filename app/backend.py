from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise
from models import User, Queue, Atendimento, MessageLog, AtendimentoStatus, MessageType
from pydantic import BaseModel
import yaml
import smtplib
from email.mime.text import MIMEText

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Helper function to send emails
def send_email(to_email: str, subject: str, content: str):
    smtp_config = config.get("smtp")
    if not smtp_config:
        print("SMTP configuration missing in config.yaml")
        return
    msg = MIMEText(content)
    msg["Subject"] = subject
    msg["From"] = smtp_config["from_email"]
    msg["To"] = to_email

    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            if smtp_config.get("use_tls"):
                server.starttls()
            if smtp_config.get("username") and smtp_config.get("password"):
                server.login(smtp_config["username"], smtp_config["password"])
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Get all queues and their pending atendimentos
    queues = await Queue.all().prefetch_related("atendimentos")
    queue_data = []
    for q in queues:
        atendimentos = await q.atendimentos.filter(status=AtendimentoStatus.AGUARDANDO)
        queue_data.append({"queue": q, "atendimentos": atendimentos})
    return templates.TemplateResponse("fila.html", {"request": request, "queues": queue_data})

# Add number to queue
@app.post("/add")
async def add_fila(queue_id: int = Form(...), phone: str = Form(...), background_tasks: BackgroundTasks = None):
    atendimento = await Atendimento.create(
        queue_id=queue_id,
        phone=phone,
        status=AtendimentoStatus.AGUARDANDO
    )
    # Optional email notification
    if "notification_email" in config:
        background_tasks.add_task(
            send_email,
            to_email=config["notification_email"],
            subject="Queue Update",
            content=f"New entry added to queue {queue_id}: {phone}"
        )
    return {"status": "added", "atendimento_id": atendimento.id}

# Call next in queue
@app.post("/next", response_class=HTMLResponse)
async def chamar_proximo(request: Request, queue_id: int = Form(...), atendente_id: int = Form(...), background_tasks: BackgroundTasks = None):
    atendimento = await Atendimento.filter(
        queue_id=queue_id,
        status=AtendimentoStatus.AGUARDANDO
    ).first()
    if atendimento:
        atendimento.status = AtendimentoStatus.CHAMADO
        atendimento.atendente_id = atendente_id
        await atendimento.save()
        # Optional email notification
        if "notification_email" in config:
            background_tasks.add_task(
                send_email,
                to_email=config["notification_email"],
                subject="Queue Update",
                content=f"Now serving: {atendimento.phone} in queue {queue_id}"
            )
        return templates.TemplateResponse("partial.html", {"request": request, "proximo": atendimento.phone})
    return HTMLResponse("<p>Fila vazia</p>")

# Tortoise ORM initialization
register_tortoise(
    app,
    db_url=config.get("database_url", "sqlite://db.sqlite3"),
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
