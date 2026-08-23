import json
from dataclasses import dataclass
from typing import Any, Generic, Mapping, TypedDict, TypeVar, overload

import jsonschema


# ################################ COMPONENT ###################################


__component__ = "fjson"
__version__ = "1.2"
__description__ = ...

__requires__ = ("jsonschema",)


__all__ = (
    # fmt: off
    "JsonSchema",
    # fmt: on
)


# ################################ TYPING ######################################


TSCHEMA = TypeVar(
    "TSCHEMA",
    bound=TypedDict,  # pyright: ignore[reportInvalidTypeForm]
)


# ################################ TYPES #######################################


@dataclass(eq=False, frozen=True, slots=True)
class JsonSchema(Generic[TSCHEMA]):
    """A JSON schema."""

    decl: Mapping[str, Any]
    """Declaration of the underlying JSON Schema."""


# ################################ FUNCTIONS ###################################


def schema(
    path: str,
    /,
    type: type[TSCHEMA],
) -> JsonSchema[TSCHEMA]:
    """
    Loads a JSON schema from a file (JSON Schema).

    :param path:
        Path of the JSON Schema file.
    :param type:
        Type describing the data validated by the schema.
    """
    schema: JsonSchema[TSCHEMA]

    with open(path, "r", encoding="utf-8") as file:
        decl = json.load(file)

    schema = JsonSchema(decl)

    return schema


@overload
def load(
    path: str,
    /,
    schema: type[TSCHEMA],
) -> TSCHEMA: ...


@overload
def load(
    path: str,
    /,
    schema: JsonSchema[TSCHEMA],
    *,
    validate: bool = ...,
) -> TSCHEMA: ...


def load(
    path: str,
    /,
    schema: JsonSchema[TSCHEMA] | type[TSCHEMA],
    *,
    validate: bool = True,
) -> TSCHEMA:
    """
    Loads data from a JSON file.

    :param path:
        Path of the JSON file.
    :param schema:
        Schema to validate the data against,
        or the type of the data to load.
    :param validate:
        Whether the data is validated against the schema.
    """
    data: TSCHEMA

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if validate and isinstance(schema, JsonSchema):
        jsonschema.validate(data, schema.decl)

    return data
