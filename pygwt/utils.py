import json
import re
from types import GenericAlias, UnionType
from typing import get_args, get_origin

from pydantic import BaseModel


def encoder(integer: int) -> str:
    """
    Codifica condigos del servicio utrilizados en los modulos mensuales a strings base64,
    viene de que el SII usa GWT (Google Web Toolkit)
    """
    key_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789$_"
    result = ""
    integer = int(integer)
    if integer == 0:
        return key_string[0]
    while integer > 0:
        integer, resto = divmod(integer, 64)  # se divide por 64 el numero original, o el "cociente" del loop anterior.
        result = key_string[resto] + result  # el "resto" de la division es codificado.
    return result


def decoder(string: str) -> int:
    """
    Decodifica condigos del servicio utrilizados en los modulos mensuales a numeros enteros,
    viene de que SII usa GWT (Google Web Toolkit)
    """
    key_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789$_"
    result = 0
    string = reversed(string)  # Invierte el codigo para poder partir con la primera unidad
    for position, letter in enumerate(string):
        result += key_string.index(letter) * (64 ** position)  # transforma base 64 a base 10
    return result


def separate_annotation(annotation: GenericAlias):
    container = get_origin(annotation)
    if container:
        contained = get_args(annotation)[0]
    else:
        contained = annotation
    container = None if container is UnionType else container
    return container, contained


def gwt_spliter(text: str) -> tuple[str, list, list]:
    """Modifica el pseudo json de la respuesta del HTTP para poder ser usado como json normal"""
    status, data = text[:4], text[4:]
    data = data.replace(r"\"", r"\'")
    data = data.encode('latin1', 'ignore').decode('unicode_escape')
    head, tail = data.split(",[")
    head = re.sub(r"'([\w$]+?)'", r'"\1"', head)
    tail = tail.replace('"+"', '')  # Por alguna razon ciertas plabras las concatenan dentro de la string, por lo que hay que borrar los "+"
    data = f"{head},[{tail}"
    data = json.loads(data, strict=False)
    *codes, table, flag, protocolo = data
    return status, codes, table


def get_pydantic_fields(model: type(BaseModel)):
    result = {}
    for field, info in model.model_fields.items():
        container, contained = separate_annotation(info.annotation)
        annotation = container[contained] if container else contained
        result[field] = annotation
    return result
