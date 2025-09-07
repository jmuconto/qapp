# app/routers/atendimentos.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
from typing import List
from app.models import Atendimento, Queue, AtendimentoStatus, User
from app.schemas import AtendimentoRead, AtendimentoCreate
from app.auth import get_current_user
from app.tasks import notify_new_entry, notify_called
from app.utils import logger

router = APIRouter()

# -----------------------
# Add new atendimento (queue ticket)
# -----------------------
@router.post("/", response_model=AtendimentoRead)
async def add_atendimento(
    queue_id: int = Form(...),
    phone: str = Form(...),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """
    Add a new Atendimento to a queue.
    """
    queue = await Queue.get_or_none(id=queue_id)
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    
    atendimento = await Atendimento.create(
        queue_id=queue.id,
        phone=phone,
        status=AtendimentoStatus.AGUARDANDO
    )

    # Schedule email notification
    if background_tasks:
        background_tasks.add_task(notify_new_entry, atendimento.id, background_tasks)

    return AtendimentoRead.from_orm(atendimento)


# -----------------------
# Get all atendimentos
# -----------------------
@router.get("/", response_model=List[AtendimentoRead])
async def list_atendimentos():
    """
    Return all atendimentos.
    """
    atendimentos = await Atendimento.all().prefetch_related("queue", "atendente")
    return [AtendimentoRead.from_orm(a) for a in atendimentos]


# -----------------------
# Call next atendimento in queue
# -----------------------
@router.post("/next", response_model=AtendimentoRead)
async def call_next(
    queue_id: int = Form(...),
    atendente_id: int = Form(...),
    background_tasks: BackgroundTasks = None
):
    """
    Call the next Atendimento in a queue and assign an attendant.
    """
    atendimento = await Atendimento.filter(
        queue_id=queue_id,
        status=AtendimentoStatus.AGUARDANDO
    ).first()
    
    if not atendimento:
        raise HTTPException(status_code=404, detail="No pending atendimentos")

    atendimento.status = AtendimentoStatus.CHAMADO
    atendimento.atendente_id = atendente_id
    await atendimento.save()

    # Schedule email notification
    if background_tasks:
        background_tasks.add_task(notify_called, atendimento.id, background_tasks)

    return AtendimentoRead.from_orm(atendimento)


# -----------------------
# Cancel atendimento
# -----------------------
@router.post("/cancel/{atendimento_id}", response_model=AtendimentoRead)
async def cancel_atendimento(
    atendimento_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an atendimento. Only the attendant or admin can cancel.
    """
    atendimento = await Atendimento.get_or_none(id=atendimento_id)
    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento not found")
    
    if atendimento.atendente_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to cancel")
    
    atendimento.status = AtendimentoStatus.CANCELADO
    await atendimento.save()
    return AtendimentoRead.from_orm(atendimento)


# -----------------------
# Get queue stats
# -----------------------
@router.get("/stats/{queue_id}")
async def queue_stats(queue_id: int):
    """
    Return statistics for a queue.
    """
    atendimentos = await Atendimento.filter(queue_id=queue_id)
    total = len(atendimentos)
    stats = {
        "total": total,
        "aguardando": sum(1 for a in atendimentos if a.status == AtendimentoStatus.AGUARDANDO),
        "chamado": sum(1 for a in atendimentos if a.status == AtendimentoStatus.CHAMADO),
        "cancelado": sum(1 for a in atendimentos if a.status == AtendimentoStatus.CANCELADO),
        "atendido": sum(1 for a in atendimentos if a.status == AtendimentoStatus.ATENDIDO),
    }
    return stats
