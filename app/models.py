from tortoise.models import Model
from tortoise import fields
from enum import Enum

# Enum definitions
class UserRole(str, Enum):
    ADMIN = "admin"
    GESTOR = "gestor"
    ATENDENTE = "atendente"

class AtendimentoStatus(str, Enum):
    AGUARDANDO = "aguardando"
    CHAMADO = "chamado"
    CANCELADO = "cancelado"
    ATENDIDO = "atendido"

class MessageType(str, Enum):
    ENTRADA = "entrada"
    CHAMADA = "chamada"
    CANCELAMENTO = "cancelamento"

# User model
class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    phone = fields.CharField(max_length=20, unique=True)
    role = fields.CharEnumField(enum_type=UserRole, default=UserRole.ATENDENTE)
    password_hash = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)

    atendimentos = fields.ReverseRelation["Atendimento"]
    queues_created = fields.ReverseRelation["Queue"]

# Queue model
class Queue(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    created_by = fields.ForeignKeyField('models.User', related_name='queues_created')
    active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    atendimentos = fields.ReverseRelation["Atendimento"]

# Atendimento (queue ticket) model
class Atendimento(Model):
    id = fields.IntField(pk=True)
    queue = fields.ForeignKeyField('models.Queue', related_name='atendimentos')
    phone = fields.CharField(max_length=20)
    status = fields.CharEnumField(enum_type=AtendimentoStatus, default=AtendimentoStatus.AGUARDANDO)
    atendente = fields.ForeignKeyField('models.User', null=True, related_name='atendimentos')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    logs = fields.ReverseRelation["MessageLog"]

# Message log for notifications
class MessageLog(Model):
    id = fields.IntField(pk=True)
    atendimento = fields.ForeignKeyField('models.Atendimento', related_name='logs')
    message_type = fields.CharEnumField(enum_type=MessageType)
    content = fields.TextField()
    sent_at = fields.DatetimeField(auto_now_add=True)
