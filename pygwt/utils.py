import json
import re
from types import GenericAlias, UnionType
from typing import get_args, get_origin

from pydantic import BaseModel


def encoder(integer: int) -> str:
    """Encode *integer* using the base64 alphabet employed by GWT."""
    key_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789$_"
    result = ""
    integer = int(integer)
    if integer == 0:
        return key_string[0]
    while integer > 0:
        integer, remainder = divmod(integer, 64)  # divide by 64 to obtain the quotient
        result = key_string[remainder] + result  # encode the remainder
    return result


def decoder(string: str) -> int:
    """Decode a base64 *string* produced by :func:`encoder`."""
    key_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789$_"
    result = 0
    string = reversed(string)  # reverse to process from least significant digit
    for position, letter in enumerate(string):
        result += key_string.index(letter) * (64 ** position)  # convert base64 to base10
    return result


def separate_annotation(annotation: GenericAlias):
    """Return the container and contained types from a type annotation."""

    container = get_origin(annotation)
    if container:
        contained = get_args(annotation)[0]
    else:
        contained = annotation
    container = None if container is UnionType else container
    return container, contained


def gwt_splitter(text: str) -> tuple[str, list, list]:
    """Parse the raw HTTP response from GWT and return ``(status, codes, table)``."""

    status, payload = text[:4], text[4:]
    payload = payload.replace(r"\"", r"\'")
    payload = payload.encode("latin1", "ignore").decode("unicode_escape")
    head, tail = payload.split(",[")
    head = re.sub(r"'([\w$]+?)'", r'"\1"', head)
    tail = tail.replace("\"+\"", "")  # remove concatenations inside quoted strings
    payload = f"{head},[{tail}"
    payload = json.loads(payload, strict=False)
    *codes, table, _flag, _protocol = payload
    return status, codes, table


def get_pydantic_fields(model: type(BaseModel)):
    """Return a mapping of field names to their resolved annotations."""

    result = {}
    for field, info in model.model_fields.items():
        container, contained = separate_annotation(info.annotation)
        annotation = container[contained] if container else contained
        result[field] = annotation
    return result
