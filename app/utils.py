# app/utils.py
import smtplib
from email.mime.text import MIMEText
from typing import Optional
import yaml
import logging
import re

# Load config
with open("app/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qapp_utils")


def send_email(to_email: str, subject: str, content: str):
    """
    Send an email using SMTP configuration from config.yaml
    """
    smtp_config = config.get("smtp")
    if not smtp_config:
        logger.error("SMTP configuration missing in config.yaml")
        return

    msg = MIMEText(content)
    msg["Subject"] = subject
    msg["From"] = smtp_config.get("from_email", "noreply@qapp.com")
    msg["To"] = to_email

    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            if smtp_config.get("use_tls", False):
                server.starttls()
            username = smtp_config.get("username")
            password = smtp_config.get("password")
            if username and password:
                server.login(username, password)
            server.send_message(msg)
        logger.info(f"Email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")


def format_phone(phone: str) -> str:
    """
    Standardize phone numbers: remove spaces, parentheses, dashes.
    """
    phone_clean = re.sub(r"[^\d+]", "", phone)
    return phone_clean


def queue_statistics(atendimentos: list) -> dict:
    """
    Generate simple queue statistics from a list of Atendimento objects/dicts.
    """
    stats = {
        "total": len(atendimentos),
        "aguardando": sum(1 for a in atendimentos if a.status == "aguardando"),
        "chamado": sum(1 for a in atendimentos if a.status == "chamado"),
        "cancelado": sum(1 for a in atendimentos if a.status == "cancelado"),
        "atendido": sum(1 for a in atendimentos if a.status == "atendido"),
    }
    return stats


def log_message(atendimento_id: int, message_type: str, content: str):
    """
    Helper to log messages for a ticket. To be expanded for DB integration.
    """
    from app.models import MessageLog, Atendimento

    try:
        atendimento = Atendimento.get(id=atendimento_id)
        MessageLog.create(
            atendimento=atendimento,
            message_type=message_type,
            content=content
        )
        logger.info(f"Message logged for Atendimento {atendimento_id}")
    except Exception as e:
        logger.error(f"Failed to log message for Atendimento {atendimento_id}: {e}")
