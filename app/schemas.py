from pydantic import BaseModel
from typing import Optional

class AtendimentoCreate(BaseModel):
    queue_id: int
    phone: str

class AtendimentoRead(BaseModel):
    id: int
    queue_id: int
    phone: str
    status: str
    atendente_id: Optional[int]

    class Config:
        orm_mode = True
