import json
import sys
from dataclasses import dataclass
from typing import Generic, Type, TypedDict, TypeVar

import jsonschema


if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


# ################################ METADATA ####################################


__pkgname__ = "ftoml"
__version__ = "1.0"

__dependencies__ = (
    ("tomli",)
    if sys.version_info < (3, 11)
    else ()
    # <format-newline>
) + ("jsonschema",)


# ################################ GLOBALS #####################################


__all__ = (
    # fmt: off
    "TomlSchema",
    "schema",
    "load",
    # fmt: on
)


# ################################ TYPING ######################################


TSCHEMA = TypeVar(
    "TSCHEMA",
    bound=TypedDict,  # pyright: ignore[reportInvalidTypeForm]
)


# ################################ TYPES #######################################


@dataclass(frozen=True, slots=True)
class TomlSchema(Generic[TSCHEMA]):
    decl: TSCHEMA


# ################################ INTERFACE ###################################


def schema(
    path: str,
    /,
    type: Type[TSCHEMA],
) -> TomlSchema[TSCHEMA]:
    schema: TomlSchema[TSCHEMA]

    with open(path, "r", encoding="utf-8") as file:
        s = file.read()

    decl = json.loads(s)

    schema = TomlSchema(decl)

    return schema


def load(
    path: str,
    /,
    schema: TomlSchema[TSCHEMA],
    *,
    validate: bool = True,
) -> TSCHEMA:
    data: TSCHEMA

    with open(path, "r", encoding="utf-8") as file:
        s = file.read()

    data = tomllib.loads(s)  # type: ignore

    if validate:
        jsonschema.validate(data, schema.decl)

    return data
