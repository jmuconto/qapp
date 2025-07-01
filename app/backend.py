from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import yaml

app = FastAPI()
templates = Jinja2Templates(directory="templates")

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

fila = []

class SMSWebhook(BaseModel):
    From: str
    Body: str

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("fila.html", {"request": request, "fila": fila})

@app.post("/add")
def add_fila(numero: str = Form(...)):
    fila.append(numero)
    return {"status": "added"}

@app.post("/next", response_class=HTMLResponse)
def chamar_proximo(request: Request):
    if fila:
        proximo = fila.pop(0)
        return templates.TemplateResponse("partial.html", {"request": request, "proximo": proximo})
    return HTMLResponse("<p>Fila vazia</p>")