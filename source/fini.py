import json
from configparser import BasicInterpolation, ConfigParser
from dataclasses import dataclass
from typing import Any, Final, Generic, Mapping, Type, TypedDict, TypeVar

import jsonschema


# ################################ PACKAGE #####################################


__sname__ = "fini"
__version__ = "1.0"
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
    decl: TSCHEMA

    parser: Type[TPARSER] | None
    args: Mapping[str, Any] | None


# ################################ CONSTANTS ###################################


DEFAULT_PARSER_TYPE: Final = ConfigParser

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


# ################################ FUNCTIONS ###################################


def schema(
    path: str,
    /,
    type: Type[TSCHEMA],
    *,
    parser: Type[TPARSER] | None = None,
    **args: Any,
) -> IniSchema[TSCHEMA, TPARSER]:
    schema: IniSchema[TSCHEMA, TPARSER]

    with open(path, "r", encoding="utf-8") as file:
        s = file.read()

    decl = json.loads(s)  # type: ignore

    schema = IniSchema(decl, parser, (args or None))

    return schema


def load(
    path: str,
    /,
    schema: IniSchema[TSCHEMA, TPARSER],
    *,
    validate: bool = True,
) -> TSCHEMA:
    data: TSCHEMA

    parser_type = schema.parser or DEFAULT_PARSER_TYPE
    parser_args = schema.args or DEFAULT_PARSER_ARGS
    parser = parser_type(**parser_args)

    with open(path, "r", encoding="utf-8") as file:
        parser.read_file(file)

    data = _parserdict(parser)  # type: ignore

    if validate:
        jsonschema.validate(data, schema.decl)

    return data


def loadp(
    path: str,
    /,
    schema: IniSchema[TSCHEMA, TPARSER],
    *,
    validate: bool = True,
) -> TPARSER:
    vdata: TSCHEMA

    parser_type = schema.parser or DEFAULT_PARSER_TYPE
    parser_args = schema.args or DEFAULT_PARSER_ARGS
    parser = parser_type(**parser_args)

    with open(path, "r", encoding="utf-8") as file:
        parser.read_file(file)

    if validate:
        vdata = _parserdict(parser)  # type: ignore

        jsonschema.validate(vdata, schema.decl)

    return parser  # type: ignore


# ################################ HELPERS #####################################


def _parserdict(source: ConfigParser, /) -> dict[str, Any]:
    return {
        section: dict(source.items(section))
        for section in source.sections()
        # <format-newline>
    }
