import json
from dataclasses import dataclass
from typing import Generic, Type, TypedDict, TypeVar, overload

import jsonschema
import yaml


# ################################ PACKAGE #####################################


__sname__ = "fyaml"
__version__ = "1.1"
__description__ = ...

__requires__ = ("jsonschema", "yaml")


__all__ = (
    # fmt: off
    "YamlSchema",
    # fmt: on
)


# ################################ TYPING ######################################


TSCHEMA = TypeVar(
    "TSCHEMA",
    bound=TypedDict,  # pyright: ignore[reportInvalidTypeForm]
)


# ################################ TYPES #######################################


@dataclass(eq=False, frozen=True, slots=True)
class YamlSchema(Generic[TSCHEMA]):
    decl: TSCHEMA


# ################################ FUNCTIONS ###################################


def schema(
    path: str,
    /,
    type: Type[TSCHEMA],
) -> YamlSchema[TSCHEMA]:
    schema: YamlSchema[TSCHEMA]

    with open(path, "r", encoding="utf-8") as file:
        s = file.read()

    decl = json.loads(s)  # type: ignore

    schema = YamlSchema(decl)

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
    schema: YamlSchema[TSCHEMA],
    *,
    validate: bool = ...,
) -> TSCHEMA: ...


def load(
    path: str,
    /,
    schema: YamlSchema[TSCHEMA] | Type[TSCHEMA],
    *,
    validate: bool = True,
) -> TSCHEMA:
    data: TSCHEMA

    with open(path, "r", encoding="utf-8") as file:
        s = file.read()

    data = yaml.load(s)  # type: ignore

    if validate and isinstance(schema, YamlSchema):
        jsonschema.validate(data, schema.decl)

    return data
