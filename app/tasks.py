# app/tasks.py
from fastapi import BackgroundTasks
from app.utils import send_email, logger
from app.models import Atendimento, AtendimentoStatus
from tortoise.expressions import Q
from datetime import datetime, timedelta
import asyncio

async def notify_new_entry(atendimento_id: int, background_tasks: BackgroundTasks):
    """
    Send an email notification when a new Atendimento is added to the queue.
    """
    from app.models import Atendimento
    atendimento = await Atendimento.get(id=atendimento_id)
    email = atendimento.phone  # Replace with actual email field if available

    subject = "qApp Queue Notification"
    content = f"You have been added to the queue: {atendimento.id} in queue {atendimento.queue_id}"
    background_tasks.add_task(send_email, to_email=email, subject=subject, content=content)
    logger.info(f"Scheduled new entry email for Atendimento {atendimento_id}")


async def notify_called(atendimento_id: int, background_tasks: BackgroundTasks):
    """
    Send an email notification when an Atendimento is called.
    """
    atendimento = await Atendimento.get(id=atendimento_id)
    email = atendimento.phone  # Replace with actual email field if available

    subject = "qApp Queue Update"
    content = f"You are now being served: Atendimento {atendimento.id} in queue {atendimento.queue_id}"
    background_tasks.add_task(send_email, to_email=email, subject=subject, content=content)
    logger.info(f"Scheduled called email for Atendimento {atendimento_id}")


async def cleanup_old_atendimentos(days: int = 7):
    """
    Periodically clean up Atendimento entries older than `days` and mark them as cancelled if still pending.
    """
    threshold = datetime.utcnow() - timedelta(days=days)
    old_atendimentos = await Atendimento.filter(
        Q(status=AtendimentoStatus.AGUARDANDO) & Q(created_at__lt=threshold)
    )
    for atendimento in old_atendimentos:
        atendimento.status = AtendimentoStatus.CANCELADO
        await atendimento.save()
        logger.info(f"Cancelled old Atendimento {atendimento.id}")


async def periodic_email_reminder(interval_seconds: int = 3600):
    """
    Periodically send reminders for pending atendimentos.
    """
    while True:
        pending_atendimentos = await Atendimento.filter(status=AtendimentoStatus.AGUARDANDO)
        for atendimento in pending_atendimentos:
            email = atendimento.phone  # Replace with actual email
            subject = "qApp Queue Reminder"
            content = f"Reminder: You are still in the queue. Atendimento {atendimento.id}"
            await send_email(email, subject, content)
        await asyncio.sleep(interval_seconds)


def schedule_background_task(background_tasks: BackgroundTasks, func, *args, **kwargs):
    """
    Helper to schedule any async function as a background task.
    """
    background_tasks.add_task(asyncio.create_task, func(*args, **kwargs))
