# app/routers/queue.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
from typing import List
from app.models import Queue, User
from app.schemas import QueueRead, QueueCreate
from app.auth import get_current_user
from app.utils import send_email, logger

router = APIRouter()

# -----------------------
# Create a new queue
# -----------------------
@router.post("/", response_model=QueueRead)
async def create_queue(
    name: str = Form(...),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """
    Create a new queue. Only authenticated users can create queues.
    """
    queue = await Queue.create(name=name, created_by=current_user)
    # Optional: send notification email to admin
    if "notification_email" in background_tasks.app.state.config:
        email = background_tasks.app.state.config["notification_email"]
        background_tasks.add_task(
            send_email,
            to_email=email,
            subject="New Queue Created",
            content=f"Queue '{name}' created by {current_user.name}"
        )
    return QueueRead.from_orm(queue)

# -----------------------
# List all queues
# -----------------------
@router.get("/", response_model=List[QueueRead])
async def list_queues():
    """
    Return a list of all queues.
    """
    queues = await Queue.all().prefetch_related("atendimentos")
    return [QueueRead.from_orm(q) for q in queues]

# -----------------------
# Get queue by ID
# -----------------------
@router.get("/{queue_id}", response_model=QueueRead)
async def get_queue(queue_id: int):
    """
    Get a single queue by ID.
    """
    queue = await Queue.get_or_none(id=queue_id).prefetch_related("atendimentos")
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    return QueueRead.from_orm(queue)

# -----------------------
# Update queue
# -----------------------
@router.put("/{queue_id}", response_model=QueueRead)
async def update_queue(
    queue_id: int,
    name: str = Form(...),
    active: bool = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Update queue name and active status. Only the creator or admin can update.
    """
    queue = await Queue.get_or_none(id=queue_id)
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    if queue.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    queue.name = name
    queue.active = active
    await queue.save()
    return QueueRead.from_orm(queue)

# -----------------------
# Delete queue
# -----------------------
@router.delete("/{queue_id}")
async def delete_queue(queue_id: int, current_user: User = Depends(get_current_user)):
    """
    Delete a queue. Only the creator or admin can delete.
    """
    queue = await Queue.get_or_none(id=queue_id)
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    if queue.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    await queue.delete()
    return {"status": "deleted", "queue_id": queue_id}
