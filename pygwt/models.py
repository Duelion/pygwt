from abc import ABCMeta
from abc import abstractmethod
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, computed_field, model_serializer
from pygwt.utils import decoder


class BaseBuiltIn(BaseModel, metaclass=ABCMeta):
    """Base class for custom wrappers around primitive GWT types."""

    @model_serializer
    def serializer(self):
        return self.value

    @property
    @abstractmethod
    def value(self):
        pass


class Long(BaseBuiltIn):
    """Integer encoded as base64 by GWT."""
    raw: str

    @computed_field
    def value(self) -> float:
        return decoder(self.raw)


class Bool(BaseBuiltIn):
    """Boolean value encoded as ``0`` or ``1``."""
    raw: int

    @computed_field
    def value(self) -> bool:
        return bool(self.raw)


class Date(BaseBuiltIn):
    """Date string in ``dd/mm/yyyy`` or ``dd/mm/yyyy HH:MM:SS`` format."""
    raw: str

    @computed_field
    def value(self) -> date:
        pattern = "%d/%m/%Y" if len(self.raw) == 10 else "%d/%m/%Y %H:%M:%S"
        parsed = datetime.strptime(self.raw, pattern)
        return parsed.date()

class TimeStamp(BaseBuiltIn):
    """Epoch timestamp encoded as milliseconds or formatted string."""
    raw: str
    ignore: Any

    @computed_field
    def value(self) -> datetime:
        if "/" in self.raw:
            timestamp = datetime.strptime(self.raw, '%d/%m/%Y %H:%M:%S')
        else:
            value = decoder(self.raw)
            timestamp = datetime.fromtimestamp(value / 1000.0)
        return timestamp


class Xml(BaseBuiltIn):
    """XML string escaped with Java conventions."""
    raw: str

    @computed_field
    def value(self) -> str:
        xml = self.raw.encode().decode('unicode-escape')
        return xml

