import json
import tomllib
from dataclasses import dataclass
from typing import Any, Generic, Mapping, TypedDict, TypeVar, overload

import jsonschema


# ################################ COMPONENT ###################################


__component__ = "ftoml"
__version__ = "1.2"
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
    """A TOML schema."""

    decl: Mapping[str, Any]
    """Declaration of the underlying JSON Schema."""


# ################################ FUNCTIONS ###################################


def schema(
    path: str,
    /,
    type: type[TSCHEMA],
) -> TomlSchema[TSCHEMA]:
    """
    Loads a TOML schema from a file (JSON Schema).

    :param path:
        Path of the JSON Schema file.
    :param type:
        Type describing the data validated by the schema.
    """
    schema: TomlSchema[TSCHEMA]

    with open(path, "r", encoding="utf-8") as file:
        decl = json.load(file)

    schema = TomlSchema(decl)

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
    schema: TomlSchema[TSCHEMA],
    *,
    validate: bool = ...,
) -> TSCHEMA: ...


def load(
    path: str,
    /,
    schema: TomlSchema[TSCHEMA] | type[TSCHEMA],
    *,
    validate: bool = True,
) -> TSCHEMA:
    """
    Loads data from a TOML file.

    :param path:
        Path of the TOML file.
    :param schema:
        Schema to validate the data against,
        or the type of the data to load.
    :param validate:
        Whether the data is validated against the schema.
    """
    data: TSCHEMA

    with open(path, "rb") as file:
        data = tomllib.load(file)  # type: ignore

    if validate and isinstance(schema, TomlSchema):
        jsonschema.validate(data, schema.decl)

    return data
