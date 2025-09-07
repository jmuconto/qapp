from models import Atendimento, AtendimentoStatus

async def create_atendimento(queue_id: int, phone: str):
    return await Atendimento.create(queue_id=queue_id, phone=phone, status=AtendimentoStatus.AGUARDANDO)

async def get_next_atendimento(queue_id: int):
    return await Atendimento.filter(queue_id=queue_id, status=AtendimentoStatus.AGUARDANDO).first()
