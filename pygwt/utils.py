import json
import re
from types import GenericAlias, UnionType
from typing import get_args, get_origin

from pydantic import BaseModel


# Alphabet used by GWT for its custom base64 encoding.
# Defining it once avoids repeating the long literal in ``encoder`` and
# ``decoder`` and allows us to pre-compute an efficient lookup table.
GWT_KEY_STRING = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789$_"
GWT_KEY_MAP = {char: index for index, char in enumerate(GWT_KEY_STRING)}


def encoder(integer: int) -> str:
    """Encode *integer* using the base64 alphabet employed by GWT.

    Raises:
        ValueError: If ``integer`` is negative.
    """

    integer = int(integer)
    if integer < 0:
        raise ValueError("encoder expects a non-negative integer")
    if integer == 0:
        return GWT_KEY_STRING[0]

    result = ""
    while integer > 0:
        integer, remainder = divmod(integer, 64)  # divide by 64 to obtain the quotient
        result = GWT_KEY_STRING[remainder] + result  # encode the remainder
    return result


def decoder(string: str) -> int:
    """Decode a base64 *string* produced by :func:`encoder`.

    Raises:
        ValueError: If ``string`` is empty or contains characters outside the
            GWT alphabet.
    """

    if not string:
        raise ValueError("decoder expects a non-empty string")

    result = 0
    # process from least significant digit
    for position, letter in enumerate(reversed(string)):
        # ``GWT_KEY_MAP`` provides O(1) lookups versus ``str.index`` (O(n)).
        try:
            value = GWT_KEY_MAP[letter]
        except KeyError as exc:
            raise ValueError(f"invalid base64 character: {letter}") from exc
        result += value * (64 ** position)  # convert base64 to base10
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
