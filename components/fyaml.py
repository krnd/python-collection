import json
from dataclasses import dataclass
from typing import Any, Generic, Mapping, TypedDict, TypeVar, overload

import jsonschema
import yaml


# ################################ COMPONENT ###################################


__component__ = "fyaml"
__version__ = "1.2"
__description__ = ...

__requires__ = ("jsonschema", "PyYAML")


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
    """A YAML schema."""

    decl: Mapping[str, Any]
    """Declaration of the underlying JSON Schema."""


# ################################ FUNCTIONS ###################################


def schema(
    path: str,
    /,
    type: type[TSCHEMA],
) -> YamlSchema[TSCHEMA]:
    """
    Loads a YAML schema from a file (JSON Schema).

    :param path:
        Path of the JSON Schema file.
    :param type:
        Type describing the data validated by the schema.
    """
    schema: YamlSchema[TSCHEMA]

    with open(path, "r", encoding="utf-8") as file:
        decl = json.load(file)

    schema = YamlSchema(decl)

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
    schema: YamlSchema[TSCHEMA],
    *,
    validate: bool = ...,
) -> TSCHEMA: ...


def load(
    path: str,
    /,
    schema: YamlSchema[TSCHEMA] | type[TSCHEMA],
    *,
    validate: bool = True,
) -> TSCHEMA:
    """
    Loads data from a YAML file.

    :param path:
        Path of the YAML file.
    :param schema:
        Schema to validate the data against,
        or the type of the data to load.
    :param validate:
        Whether the data is validated against the schema.
    """
    data: TSCHEMA

    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)  # type: ignore

    if validate and isinstance(schema, YamlSchema):
        jsonschema.validate(data, schema.decl)

    return data
