from typing import Annotated

from pydantic import BaseModel, AfterValidator, computed_field, field_validator


class EventBase(BaseModel):
    """Events in a form's history"""
    code: str

    @field_validator("code", mode="before")
    @classmethod
    def set_code(cls, v: int | str):
        return str(v)

e = EventBase(code=1)
