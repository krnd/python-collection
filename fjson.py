import json
from dataclasses import dataclass
from typing import Generic, Type, TypedDict, TypeVar

import jsonschema


# ################################ METADATA ####################################


__pkgname__ = "fjson"
__version__ = "1.0"

__dependencies__ = ("jsonschema",)


# ################################ GLOBALS #####################################


__all__ = (
    # fmt: off
    "JsonSchema",
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
class JsonSchema(Generic[TSCHEMA]):
    decl: TSCHEMA


# ################################ INTERFACE ###################################


def schema(
    path: str,
    /,
    type: Type[TSCHEMA],
) -> JsonSchema[TSCHEMA]:
    schema: JsonSchema[TSCHEMA]

    with open(path, "r", encoding="utf-8") as file:
        s = file.read()

    decl = json.loads(s)

    schema = JsonSchema(decl)

    return schema


def load(
    path: str,
    /,
    schema: JsonSchema[TSCHEMA],
    *,
    validate: bool = True,
) -> TSCHEMA:
    data: TSCHEMA

    with open(path, "r", encoding="utf-8") as file:
        s = file.read()

    data = json.loads(s)  # type: ignore

    if validate:
        jsonschema.validate(data, schema.decl)

    return data
