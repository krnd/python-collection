import json
import tomllib
from dataclasses import dataclass
from typing import Generic, Type, TypedDict, TypeVar, overload

import jsonschema


# ################################ PACKAGE #####################################


__sname__ = "ftoml"
__version__ = "1.1"
__description__ = ...

__requires__ = ("jsonschema",)


__all__ = (
    # fmt: off
    "TomlSchema",
    # fmt: on
)


# ################################ TYPING ######################################


TSCHEMA = TypeVar(
    "TSCHEMA",
    bound=TypedDict,  # pyright: ignore[reportInvalidTypeForm]
)


# ################################ TYPES #######################################


@dataclass(eq=False, frozen=True, slots=True)
class TomlSchema(Generic[TSCHEMA]):
    decl: TSCHEMA


# ################################ FUNCTIONS ###################################


def schema(
    path: str,
    /,
    type: Type[TSCHEMA],
) -> TomlSchema[TSCHEMA]:
    schema: TomlSchema[TSCHEMA]

    with open(path, "r", encoding="utf-8") as file:
        s = file.read()

    decl = json.loads(s)  # type: ignore

    schema = TomlSchema(decl)

    return schema


@overload
def load(
    path: str,
    /,
    schema: Type[TSCHEMA],
) -> TSCHEMA: ...


@overload
def load(
    path: str,
    /,
    schema: TomlSchema[TSCHEMA],
    *,
    validate: bool = ...,
) -> TSCHEMA: ...


def load(
    path: str,
    /,
    schema: TomlSchema[TSCHEMA] | Type[TSCHEMA],
    *,
    validate: bool = True,
) -> TSCHEMA:
    data: TSCHEMA

    with open(path, "r", encoding="utf-8") as file:
        s = file.read()

    data = tomllib.loads(s)  # type: ignore

    if validate and isinstance(schema, TomlSchema):
        jsonschema.validate(data, schema.decl)

    return data
