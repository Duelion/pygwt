from typing import Annotated

from pydantic import BaseModel, AfterValidator, computed_field, field_validator


class EventoBase(BaseModel):
    """Eventos en el historial de un formulario"""
    codigo: str

    @field_validator("codigo", mode="before")
    @classmethod
    def set_codigo(cls, v: int | str):
        return str(v)

e = EventoBase(codigo=1)