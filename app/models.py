from tortoise.models import Model
from tortoise import fields
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    gestor = "gestor"
    atendente = "atendente"

class AtendimentoStatus(str, Enum):
    aguardando = "aguardando"
    chamado = "chamado"
    cancelado = "cancelado"
    atendido = "atendido"

class MessageType(str, Enum):
    entrada = "entrada"
    chamada = "chamada"
    cancelamento = "cancelamento"

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    phone = fields.CharField(max_length=20)
    role = fields.CharEnumField(enum_type=UserRole)
    password_hash = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)

class Queue(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    created_by = fields.ForeignKeyField('models.User')
    active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

class Atendimento(Model):
    id = fields.IntField(pk=True)
    queue = fields.ForeignKeyField('models.Queue', related_name='atendimentos')
    phone = fields.CharField(max_length=20)
    status = fields.CharEnumField(enum_type=AtendimentoStatus)
    atendente = fields.ForeignKeyField('models.User', null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

class MessageLog(Model):
    id = fields.IntField(pk=True)
    atendimento = fields.ForeignKeyField('models.Atendimento', related_name='logs')
    message_type = fields.CharEnumField(enum_type=MessageType)
    content = fields.TextField()
    sent_at = fields.DatetimeField(auto_now_add=True)