from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from pydantic import BaseModel

from pygwt import models
from pygwt.utils import gwt_splitter, get_pydantic_fields, separate_annotation

# -------------------------------------------------------------------------- #
#                          GWT-RPC RESPONSE DECODER                          #
# -------------------------------------------------------------------------- #

"""Utilities for decoding GWT-RPC responses.

The parser reads a reversed sequence of integers and strings that encode Java
objects. A ``gwt_models`` mapping translates Java class names to Python types
so objects can be reconstructed while parsing.

GWT (Google Web Toolkit) compiles Java code into JavaScript to build AJAX
applications. GWT-RPC (Remote Procedure Call) serializes Java objects so they
can be transmitted via HTTP. The parser relies on custom Pydantic models to
recreate those Java objects in Python.

The following example illustrates how to decode a response:

Raw response::

    //OK[-8,-8,4,24,23,22,-8,'xV3',5,21,20,'mtMu9',5,'xV3',5,'X4A$',5,19,0,
    18,'GrnIrm',5,17,'A',5,0,3,3,16,15,14,1,3,13,12,11,10,9,8,0,7,'PPYxC',5,
    6,'EkeqE',5,4,2021,3,2,1,1,["java.util.Vector/3057315478",
    "cl.sii.sdi.sifm.commons.to.consulta.FolioPeriodoFormularioTO/3253336399",
    "java.lang.Integer/3438268394","2","java.lang.Long/4227064769","SINOBS",
    "DRCP","Vigente","AMBOS","29",
    "F29 - Declaración Mensual y Pago Simultáneo de Impuestos",
    "Declaración Mensual y Pago Simultáneo de Impuestos","MES","DPS",
    "G1515000gym","MPD_PLANT","16/04/2021","669642240","CLP",
    "2021-04-19 18:42:20.0","N","OPVPHHA","M03","CRCIVA"],0,7]

Separated parts::

    # Response status, ``//EX`` indicates an error
    //OK
    # Response data
    [
        # Instructions (codes) for reading the table
        -3,-8,4,24,23,22,-8,'xV3',5,21,20,'mtMu9',5,'xV3',5,'X4A$',5,19,0,
        18,'GrnIrm',5,17,'A',5,0,3,3,16,15,14,1,3,13,12,11,10,9,8,0,7,'PPYxC',
        5,6,'EkeqE',5,4,2021,3,2,1,1,
            [
                # Reference table interpreted using the previous codes
                "java.util.Vector/3057315478",
                "cl.sii.sdi.sifm.commons.to.consulta.FolioPeriodoFormularioTO/3253336399",
                "java.lang.Integer/3438268394","2","java.lang.Long/4227064769",
                "SINOBS","DRCP","Vigente","AMBOS","29",
                "F29 - Declaración Mensual y Pago Simultáneo de Impuestos",
                "Declaración Mensual y Pago Simultáneo de Impuestos","MES",
                "DPS","G1515000gym","MPD_PLANT","16/04/2021","669642240",
                "CLP","2021-04-19 18:42:20.0","N","OPVPHHA","M03","CRCIVA"
            ]
        # Flags returned by the service (often unused)
        ,0
        # GWT protocol version
        ,7
    ]

Instructions summary:

    1. Read the codes from the end backwards. In the example they are
       ``7, 0, table, 1, 1, 2, 3, ... , -3``.
    2. The reference table provides values for the numeric codes.
    3. Codes mean:
        ``0`` -> ``None``
        ``0 < x <= len(table)`` -> index of the value in ``table`` (1-based)
        ``text`` -> integer encoded with :func:`utils.encoder`
        ``x < 0`` -> reference to a previously parsed object, at ``history[abs(x)-1]``
    4. If the table item represents a Java object, subsequent codes describe its
       fields; the object definition dictates how many codes to consume.

Example using the instruction sequence::

    1 (ref): "java.util.Vector/3057315478"
    1 (int): a vector with one element
    2 (ref): "cl.sii.sdi.sifm.commons.to.consulta.FolioPeriodoFormularioTO/3253336399"
        3 (ref): "java.lang.Integer/3438268394"
            2021 (int)
        4 (ref): "2"
        5 (ref): "java.lang.Long/4227064769"
            'EkeqE' (string) -> 76671620
    ...
    -3 (history ref): value of the third decoded object
"""


class Stage(Enum):
    START = auto()
    LIST = auto()
    OBJ = auto()


@dataclass
class Frame:
    """Represents the state of a partial parse operation."""

    stage: Stage
    model: Any | None = None
    parent: "Frame" | None = None
    key: str | None = None
    placeholder: int | None = None
    length: int | None = None
    index: int = 0
    model_class: type | None = None
    fields: list[tuple[str, Any]] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)
    results: list[Any] = field(default_factory=list)


class GwtParser:
    gwt_models = {
        "Vector": list,
        "ArrayList": list,
        "Integer": int,
        "Double": float,
        "String": str,
        "Boolean": bool,
        "Exception": str,
        "Long": models.Long,
        "Timestamp": models.TimeStamp,
    }

    def __init__(self, response, gwt_models=None):
        status, codes, table = gwt_splitter(response)
        self.codes = codes
        self.table = table
        self.history = []
        if gwt_models is not None:
            self.gwt_models.update(gwt_models)

    def get_code_value(self, code: Any) -> Any:
        """Translate a raw *code* from ``self.codes`` into its Python value."""
        match code:
            case str():
                value = code
            case _ if code > len(self.table):
                value = code
            case _ if code < 0:
                value = self.history[abs(code) - 1]
            case 0:
                value = None
            case _:
                value = self.table[code - 1]
        return value

    def parse_model_type(self, value: Any) -> type | Any:
        """Return the Python type referenced by *value* from ``self.table``."""
        if not isinstance(value, str):
            return Any
        elif ";/" in value:  # indicates an ArrayList of the described object
            return list

        matches = re.findall(r"\.(\w+);?/\d*$", value)
        if matches:
            match = matches[0]
            model_name = "Exception" if "Exception" in match else match
        else:
            model_name = value
        model = self.gwt_models.get(model_name, Any)
        if matches and model is Any:
            raise KeyError(f"Missing model {model_name}")
        return model

    def _finalize(self, frame: Frame, result: Any, stack: deque[Frame], root: list) -> None:
        """Store ``result`` and update ``stack`` for the completed ``frame``."""

        stack.pop()
        if frame.placeholder is not None:
            self.history[frame.placeholder] = result
        parent = frame.parent
        if parent is None:
            root[0] = result
        elif parent.stage is Stage.LIST:
            parent.results.append(result)
        else:
            parent.payload[frame.key] = result

    def parse(self, model: Any | None = None) -> Any:
        """Decode the next value from ``self.codes`` using an optional annotation."""
        if not self.table:
            return None

        stack = deque([Frame(stage=Stage.START, model=model)])
        root = [None]

        while stack:
            frame = stack[-1]

            if frame.stage is Stage.START:
                code = self.codes.pop()
                value = self.get_code_value(code)

                if isinstance(code, int) and code < 0:
                    self._finalize(frame, value, stack, root)
                    continue

                parsed_model = self.parse_model_type(value)
                container, model = separate_annotation(frame.model)
                model = container if container else model

                if parsed_model is not Any:
                    if model is Any or model is None:
                        model = parsed_model
                    if model is not parsed_model:
                        value = code
                        parsed_model = Any
                    if (
                        not issubclass(parsed_model, BaseModel)
                        and parsed_model is not list
                        and parsed_model is not Any
                    ):
                        value = self.codes.pop()
                        if parsed_model is str:
                            value = self.get_code_value(value)

                if parsed_model is not Any:
                    frame.placeholder = len(self.history)
                    self.history.append(f"placeholder_{model}")

                if value is None:
                    self._finalize(frame, None, stack, root)
                    continue

                if model is list:
                    length = self.codes.pop()
                    frame.stage = Stage.LIST
                    frame.length = length
                    frame.results = []
                    frame.index = 0
                elif isinstance(model, type) and issubclass(model, BaseModel):
                    if parsed_model is Any:
                        self.codes.append(code)
                    fields = get_pydantic_fields(model)
                    frame.stage = Stage.OBJ
                    frame.fields = list(fields.items())
                    frame.payload = {}
                    frame.index = 0
                    frame.model_class = model
                else:
                    result = model(value) if model is not Any and value is not None else value
                    self._finalize(frame, result, stack, root)
                    continue

            elif frame.stage is Stage.LIST:
                if frame.index >= frame.length:
                    self._finalize(frame, frame.results, stack, root)
                    continue
                else:
                    code = self.codes[-1]
                    value = self.get_code_value(code)
                    model = self.parse_model_type(value)
                    frame.index += 1
                    stack.append(Frame(stage=Stage.START, model=model, parent=frame))
                    continue

            elif frame.stage is Stage.OBJ:
                if frame.index >= len(frame.fields):
                    obj = frame.model_class(**frame.payload)
                    self._finalize(frame, obj, stack, root)
                    continue
                else:
                    field, annotation = frame.fields[frame.index]
                    frame.index += 1
                    stack.append(Frame(stage=Stage.START, model=annotation, parent=frame, key=field))
                    continue

        return root[0]
