import re
from typing import Any

from pydantic import BaseModel

from pygwt import models
from pygwt.utils import gwt_spliter, get_pydantic_fields, separate_annotation

# -------------------------------------------------------------------------- #
#                    DECODIFICADOR DE RESPUESTAS GWT-RPC                     #
# -------------------------------------------------------------------------- #

"""
Utiliza los modelos definidos en gwt_models.py para recursivamente decodificar las respuestas GWT-RPC.

GWT (Google Web Toolkit): es un generador de javascript, convierte código java a javascript. Usado para crear AJAX.
GWT-RPC (Remote Procedure Call): permite enviar objetos java por HTTP, serializandolos con un formato especifico.
"""

# ----------------------  Ejemplo respuestas GWT-RPC  ---------------------- #
"""
Usare la siguiente seccion para documentar como se decodifica una respuesta GWT-RCP.

Respuesta en bruto: 
//OK[-8,-8,4,24,23,22,-8,'xV3',5,21,20,'mtMu9',5,'xV3',5,'X4A$',5,19,0,18,'GrnIrm',5,17,'A',5,0,3,3,16,15,14,1,3,13,12,
11,10,9,8,0,7,'PPYxC',5,6,'EkeqE',5,4,2021,3,2,1,1,["java.util.Vector/3057315478",
"cl.sii.sdi.sifm.commons.to.consulta.FolioPeriodoFormularioTO/3253336399","java.lang.Integer/3438268394","2",
"java.lang.Long/4227064769","SINOBS","DRCP","Vigente","AMBOS","29",
"F29 - Declaración Mensual y Pago Simultáneo de Impuestos","Declaración Mensual y Pago Simultáneo de Impuestos","MES",
"DPS","G1515000gym","MPD_PLANT","16/04/2021","669642240","CLP","2021-04-19 18:42:20.0","N","OPVPHHA","M03","CRCIVA"],0,7]


Respuesta separada en partes:
#Estatus de respuesta, //EX en caso de error (status)
//OK
# Data de respuesta
[
    # Instrucciones (codes) para leer tabla
    -3,-8,4,24,23,22,-8,'xV3',5,21,20,'mtMu9',5,'xV3',5,'X4A$',5,19,0,18,'GrnIrm',5,17,'A',5,0,3,3,16,15,14,1,3,13,12,11,10,9,8,0,7,'PPYxC',5,6,'EkeqE',5,4,2021,3,2,1,1,
        [
            # Tabla (table) de referencia que es ledia dependiendo de los codigos anteriores
            "java.util.Vector/3057315478","cl.sii.sdi.sifm.commons.to.consulta.FolioPeriodoFormularioTO/3253336399",
            "java.lang.Integer/3438268394","2","java.lang.Long/4227064769","SINOBS","DRCP","Vigente","AMBOS","29",
            "F29 - Declaración Mensual y Pago Simultáneo de Impuestos","Declaración Mensual y Pago Simultáneo de Impuestos","MES",
            "DPS","G1515000gym","MPD_PLANT","16/04/2021","669642240","CLP","2021-04-19 18:42:20.0","N","OPVPHHA","M03","CRCIVA"
        ]
    # Si hay flags en la respuesta (no es relevante por lo que he visto)
    ,0
    # Version del protocolo GWT (no es relevante por lo que he visto)
    ,7
]

Instrucciones:
    1- La data de respuesta se debe leer de atraz en adelante. en este caso es 7, 0, tabla, 1, 1, 2, 3, ... , -3.
    2- La tabla es una referencia, con la cual se decodifican las instrucciones.
    3- Las instrucciones tienen los siguientes significados:
        0: None
        0<x<len(tabla): indice del valor en la tabla de referencia (parte desde 1).
        texto: valor numerico codificado en Base64
        0>x: referencia a que el objeto ya fue decodificado anteriormente, en el lugar abs(x) del historial.
    4- Cuando el item leido de la tabla es un objeto java, los siguientes codigos definen los argumentos que lo componen,
    solo es posible saber el numero de argumentos conociendo la composicion del objeto.

Ejemplo (partiendo desde las instrucciones):
    1 (ref): "java.util.Vector/3057315478"
    1 (int): 1 item en el vector. No es referencia solo por que conosemos que anterior fue un vector.
    2 (ref): "cl.sii.sdi.sifm.commons.to.consulta.FolioPeriodoFormularioTO/3253336399". Objeto java de 37 argumentos.
        #inicio argumentos
        3 (ref): "java.lang.Integer/3438268394". Un solo argumento, su valor es el siguiente codigo.
            2021 (int)  # Argumento 1 de 37
        4 (ref): "2" #  Argumento 2 de 37
        5 (ref): "java.lang.Long/4227064769". Un solo argumento.
            'EkeqE' (string): Codificado en base64=76671620  # Argumento 3 de 37

    ...

    -3 (ref historial): 2021. Al ser negativo nos dice que es el objeto java numero 3 que decodificamos [Vector, FolioPeriodoFormularioTO, Integer (2021)]

"""


class GwtParser:
    gwt_models = {"Vector": list, "ArrayList": list,
                  "Integer": int, "Double": float, "String": str, "Boolean": bool,
                  "Exception": str,
                  "Long": models.Long, "Timestamp": models.TimeStamp}

    def __init__(self, response, gwt_models=None):
        status, codes, table = gwt_spliter(response)
        self.codes = codes
        self.table = table
        self.history = []
        if gwt_models is not None:
            self.gwt_models.update(gwt_models)

    def get_code_value(self, code):
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

    def parse_model_type(self, value):
        if not isinstance(value, str):
            return Any
        elif ";/" in value:  # significa que es una ArrayList del objeto que describe
            return list

        objects = re.findall(r"\.(\w+);?/\d*$", value)
        if objects:
            found = objects[0]
            name = "Exception" if "Exception" in found else found
        else:
            name = value
        model = self.gwt_models.get(name, Any)
        if objects and model is Any:
            raise KeyError(f"Falta modelo {name}")
        return model

    def parse(self, model=None, place_holder=None):
        if not self.table:
            return
        code = self.codes.pop()
        value = self.get_code_value(code)
        if isinstance(code, int) and code < 0:
            return value
        parsed_model = self.parse_model_type(value)
        container, model = separate_annotation(model)
        model = container if container else model
        if parsed_model is not Any:
            if model is Any or model is None:
                model = parsed_model
            if model is not parsed_model:
                value = code
                parsed_model = Any
            if not issubclass(parsed_model, BaseModel) and parsed_model is not list and parsed_model is not Any:
                value = self.codes.pop()
                if parsed_model is str:
                    value = self.get_code_value(value)

        if parsed_model is not Any:
            place_holder = len(self.history)
            self.history.append(f"placeholder_{model}")
        if value is None:
            return None
        if model is list:
            length = self.codes.pop()
            result = self.parse_list(length)
        elif issubclass(model, BaseModel):
            if parsed_model is Any:
                self.codes.append(code)
            fields = get_pydantic_fields(model)
            payload = {}
            for field, annotation in fields.items():
                value = self.parse(annotation)
                payload[field] = value
            result = model(**payload)
        else:
            result = model(value) if model is not Any and value is not None else value
        if place_holder is not None:
            self.history[place_holder] = result
        return result

    def parse_list(self, length):
        results = []
        for _ in range(length):
            code = self.codes[-1]
            value = self.get_code_value(code)
            model = self.parse_model_type(value)
            result = self.parse(model=model)
            results.append(result)
        return results
