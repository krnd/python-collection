import json
from configparser import BasicInterpolation, ConfigParser
from dataclasses import dataclass
from typing import Any, Final, Generic, Mapping, TypedDict, TypeVar, overload

import jsonschema


# ################################ COMPONENT ###################################


__component__ = "fini"
__version__ = "1.2"
__description__ = ...

__requires__ = ("jsonschema",)


__all__ = (
    # fmt: off
    "IniSchema",
    # fmt: on
)


# ################################ TYPING ######################################


TSCHEMA = TypeVar(
    "TSCHEMA",
    bound=TypedDict,  # pyright: ignore[reportInvalidTypeForm]
)

TPARSER = TypeVar(
    "TPARSER",
    bound=ConfigParser,
)


# ################################ TYPES #######################################


@dataclass(eq=False, frozen=True, slots=True)
class IniSchema(Generic[TSCHEMA, TPARSER]):
    """An INI schema."""

    decl: Mapping[str, Any]
    """Declaration of the underlying JSON Schema."""

    parser: type[TPARSER] | None
    """Parser type to read the data with."""
    args: Mapping[str, Any] | None
    """Arguments for instantiating the parser."""


# ################################ CONSTANTS ###################################


DEFAULT_PARSER_TYPE: Final = ConfigParser
"""Default parser type to read data with."""

# fmt:off
DEFAULT_PARSER_ARGS: Final = dict[str, Any](
    defaults=None,                       # None
    dict_type=dict,                      # dict
    allow_no_value=True,                 # False
    delimiters=("=",),                   # ("=", ":")
    comment_prefixes=("#", ";"),         # ("#", ";")
    inline_comment_prefixes=("#",),      # None
    strict=True,                         # True
    empty_lines_in_values=False,         # True
    default_section="DEFAULT",           # configparser.DEFAULTSECT
    interpolation=BasicInterpolation(),  # BasicInterpolation()
    converters=dict(),                   # {}
)
# fmt:on
""""Default arguments for instantiating a parser."""


# ################################ FUNCTIONS ###################################


def schema(
    path: str,
    /,
    type: type[TSCHEMA],
    *,
    parser: type[TPARSER] | None = None,
    **args: Any,
) -> IniSchema[TSCHEMA, TPARSER]:
    """
    Loads a INI schema from a file (JSON Schema).

    :param path:
        Path of the JSON Schema file.
    :param type:
        Type describing the data validated by the schema.
    :param parser:
        Parser type to read the data with.
    :param args:
        Arguments for instantiating the parser.
    """
    schema: IniSchema[TSCHEMA, TPARSER]

    with open(path, "r", encoding="utf-8") as file:
        decl = json.load(file)

    schema = IniSchema(decl, parser, (args or None))

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
    schema: IniSchema[TSCHEMA, TPARSER],
    *,
    validate: bool = ...,
) -> TSCHEMA: ...


def load(
    path: str,
    /,
    schema: IniSchema[TSCHEMA, TPARSER] | type[TSCHEMA],
    *,
    validate: bool = True,
) -> TSCHEMA:
    """
    Loads data from an INI file.

    :param path:
        Path of the INI file.
    :param schema:
        Schema to validate the data against,
        or the type of the data to load.
    :param validate:
        Whether the data is validated against the schema.
    """
    data: TSCHEMA

    if isinstance(schema, IniSchema):
        parser_type = schema.parser or DEFAULT_PARSER_TYPE
        parser_args = schema.args or DEFAULT_PARSER_ARGS
    else:
        parser_type = DEFAULT_PARSER_TYPE
        parser_args = DEFAULT_PARSER_ARGS

    parser = parser_type(**parser_args)

    with open(path, "r", encoding="utf-8") as file:
        parser.read_file(file)

    data = _parserdict(parser)  # type: ignore

    if validate and isinstance(schema, IniSchema):
        jsonschema.validate(data, schema.decl)

    return data


@overload
def loadp(
    path: str,
    /,
    schema: type[TSCHEMA],
) -> ConfigParser: ...


@overload
def loadp(
    path: str,
    /,
    schema: IniSchema[TSCHEMA, TPARSER],
    *,
    validate: bool = ...,
) -> TPARSER: ...


def loadp(
    path: str,
    /,
    schema: IniSchema[TSCHEMA, TPARSER] | type[TSCHEMA],
    *,
    validate: bool = True,
) -> TPARSER:
    """
    Loads data from an INI file.

    :param path:
        Path of the INI file.
    :param schema:
        Schema to validate the data against,
        or the type of the data to load.
    :param validate:
        Whether the data is validated against the schema.

    :return:
        Returns the underlying `ConfigParser` instead of the data.
    """
    data: TSCHEMA

    if isinstance(schema, IniSchema):
        parser_type = schema.parser or DEFAULT_PARSER_TYPE
        parser_args = schema.args or DEFAULT_PARSER_ARGS
    else:
        parser_type = DEFAULT_PARSER_TYPE
        parser_args = DEFAULT_PARSER_ARGS

    parser = parser_type(**parser_args)

    with open(path, "r", encoding="utf-8") as file:
        parser.read_file(file)

    if validate and isinstance(schema, IniSchema):
        data = _parserdict(parser)  # type: ignore

        jsonschema.validate(data, schema.decl)

    return parser  # type: ignore


# ################################ HELPERS #####################################


def _parserdict(source: ConfigParser, /) -> dict[str, Any]:
    return {
        section: dict(source.items(section))
        for section in source.sections()
        # <format-break>
    }
