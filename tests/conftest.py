import pathlib
from typing import Any

import pytest
from pydantic import BaseModel

from pygwt import models
from pygwt.parser import GwtParser


def gwt_files():
    current = pathlib.Path(__file__).parent
    examples = current / "gwt_examples"
    files = examples.rglob("*.txt")
    return files

@pytest.fixture(params=gwt_files())
def gwt_file(request):
    return request.param

@pytest.fixture
def target_file():
    """Return the sample GWT file used for parsing tests."""
    current = pathlib.Path(__file__).parent
    file = current / "gwt_examples" / "f29" / "new_test_1.txt"
    return file



@pytest.fixture(scope="session")
def gwt_models():
    gwt_models = {
        "EventosDeclaracionTO": EventosDeclaracionTO,
        "AplicacionesTO": AplicacionesTO,
        "FolioPeriodoFormularioTO": FolioPeriodoFormularioTO,
        "DeclaracionCnEstados": DeclaracionCnEstados,
        "ObservacionesCruceTO": ObservacionesCruceTO,
        "BorradorCnFecha": BorradorCnFecha,
        "EventoFormInterno": EventoFormInterno,
        "DatosDeclaracionAnulada": DatosDeclaracionAnulada,
        "SidAtencion": SidAtencion,
        "SidTipoAccion": SidTipoAccion,
        "DatosNotificacion": DatosNotificacion,
        "FormularioInterno": FormularioInterno
    }
    return gwt_models

class AplicacionesTO(BaseModel):
    codigo: int
    unknown_01: Any
    unknown_02: Any
    unknown_03: Any
    unknown_04: Any
    unknown_05: Any
    unknown_06: Any


class EventosDeclaracionTO(BaseModel):
    codigo: str
    descripcion: str
    tipo: str
    folio_noprobado: models.Long
    unknown_04: Any
    corr: models.Long
    unknown_06: Any
    fecha: models.Date
    periodo: models.Long
    unknown_09: Any
    unknown_10: Any
    numero: Any
    unknown_12: Any
    unknown_13: Any
    unknown_14: Any
    unknown_15: Any
    unknown_16: Any
    unknown_17: Any
    unknown_18: int
    unknown_19: int
    AplicacionesTO: AplicacionesTO | None


class FolioPeriodoFormularioTO(BaseModel):
    year: int
    unknown_01: Any
    unknown_02: Any
    situacion: str | None
    interno_a: models.Long
    unknown_05: Any
    unknown_06: Any
    estado: str
    unknown_08: Any
    unknown_09: Any
    unknown_10: Any
    unknown_11: Any
    unknown_12: Any
    unknown_13: Any
    unknown_14: Any
    unknown_15: Any
    mdp: str
    unknown_17: Any
    unknown_18: Any
    unknown_19: Any
    fecha: models.Date
    folio: models.Long
    unknown_22: Any
    unknown_23: Any
    unknown_24: Any
    unknown_25: Any
    unknown_26: Any
    interno_b: models.Long | None
    unknown_28: Any
    observado: str | None
    periodo: models.Long | None
    unknown_31: Any
    codigo_estado: str | None
    unknown_33: Any
    unknown_34: Any
    unknown_35: Any
    unknown_36: Any
    unknown_37: Any

class DeclaracionCnEstados(BaseModel):
    unknown_00: Any
    unknown_01: Any
    unknown_02: Any
    unknown_03: Any
    unknown_04: Any
    unknown_05: Any
    unknown_06: models.TimeStamp | None
    fecha: models.Date | None
    unknown_08: Any
    periodo: models.TimeStamp | None
    rut: int | None
    unknown_11: Any
    unknown_12: Any
    unknown_13: Any
    unknown_14: Any
    unknown_15: Any
    xml: models.Xml | None
    html: str | None
    code_a: int | None
    unknown_19: int | None
    situacion: str | None
    unknown_21: Any
    estado: str | None
    unknown_23: Any
    folio: models.Long | None
    unknown_25: Any
    unknown_26: int | None
    monto: float | None
    unknown_28: Any
    unknown_29: Any
    unknown_30: Any
    unknown_31: Any

class ObservacionesCruceTO(BaseModel):
    unknown_00: Any
    corr: models.Long
    codigo: str
    descripcion: str
    unknown_04: Any
    unknown_05: Any
    otros: str
    unknown_07: Any
    unknown_08: Any
    codigo_estado: str

class BorradorCnFecha(BaseModel):
    unknown_00: int
    unknown_01: Any
    fecha: models.TimeStamp
    unknown_03: Any
    unknown_04: Any
    unknown_05: Any
    periodo: models.TimeStamp
    rut: int
    unknown_08: Any
    unknown_09: Any
    xml: models.Xml

class EventoFormInterno(BaseModel):
    codigo: models.Long
    descripcion: str
    unknown_02: Any
    unknown_03: Any
    unknown_04: Any
    unknown_05: Any
    unknown_06: Any
    unknown_07: Any
    unknown_08: Any
    unknown_09: Any
    unknown_10: Any
    unknown_11: Any
    fecha: models.TimeStamp
    unknown_13: Any
    unknown_14: Any
    unknown_15: Any
    unknown_16: Any
    unknown_17: Any
    unknown_18: Any
    unknown_19: Any
    unknown_20: Any
    unknown_21: Any
    unknown_22: Any

class DatosDeclaracionAnulada(BaseModel):
    unknown_00: models.Long
    folio: models.Long
    periodo: int
    rut: int
    descripcion: str
    unknown_05: int
    unknown_06: Any

class SidAtencion(BaseModel):
    unknown_00: str
    unknown_01: models.Long
    unknown_02: Any
    unknown_03: Any
    unknown_04: Any
    unknown_05: models.TimeStamp
    unknown_06: models.TimeStamp
    unknown_07: str
    unknown_08: models.Long
    unknown_09: models.Long
    unknown_10: models.Long
    unknown_11: str
    unknown_12: int
    unknown_13: models.TimeStamp
    unknown_14: models.Long
    unknown_15: int

class SidTipoAccion(BaseModel):
    unknown_00: str
    unknown_02: int
    unknown_03: str
    atencion: SidAtencion

class DatosNotificacion(BaseModel):
    accion: list[SidTipoAccion]

class FormularioInterno(BaseModel):
    unknown_00: str | None
    unknown_01: Any
    unknown_02: Any
    datos_notificacion: DatosNotificacion | None
    declaracion: DeclaracionCnEstados
    unknown_05: Any
    unknown_06: Any
    unknown_07: Any
    unknown_08: Any
    unknown_09: Any
    unknown_10: Any
    unknown_11: Any
    unknown_12: Any
    unknown_13: Any
    unknown_14: Any
    unknown_15: Any
    unknown_16: Any
    unknown_17: Any
    unknown_18: Any
    unknown_19: Any
    unknown_20: Any
    unknown_21: Any
    unknown_22: Any
    unknown_23: Any
    unknown_24: Any
    unknown_25: Any
    unknown_26: Any
    unknown_27: Any
    unknown_28: Any
    unknown_29: Any
    unknown_30: Any
    unknown_31: Any
    unknown_32: Any
    unknown_33: Any
    eventos: list[EventoFormInterno] | None
    unknown_35: Any
    unknown_36: Any
    unknown_37: Any
    unknown_38: Any
    unknown_39: Any
    unknown_40: Any
    unknown_41: Any
    unknown_42: Any
    datos_declaracion_anulada: list[DatosDeclaracionAnulada] | None
    unknown_44: list[int]
    unknown_45: list[int]
    unknown_46: Any
    unknown_47: Any
    unknown_48: Any
    unknown_49: Any
    unknown_50: Any
    unknown_51: Any
    unknown_52: bool
    unknown_53: Any
    unknown_54: Any
    unknown_55: Any
    unknown_56: int | None
    unknown_57: Any
    unknown_58: Any
    unknown_59: Any
    unknown_60: Any
    unknown_61: Any
    unknown_62: Any
    unknown_63: Any
    unknown_64: Any
    unknown_65: Any
    unknown_66: str | None
    unknown_67: str | None
