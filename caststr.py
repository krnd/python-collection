import builtins
import typing
from typing import Annotated
from typing import Any
from typing import Any as _Ignore
from typing import (
    Final,
    Literal,
    Mapping,
    Sequence,
    Type,
    TypeAlias,
    TypeVar,
    Union,
    overload,
)


# ################################ METADATA ####################################


__pkgname__ = "caststr"
__version__ = "1.0"

__dependencies__ = ()


# ################################ GLOBALS #####################################


__all__ = (
    # fmt: off
    "NotResolved",
    "isnone", "isbool", "isfalse", "istrue",
    "resolve",
    # fmt: on
)


# ################################ TYPING ######################################


T = TypeVar("T")


# ################################ TYPES #######################################


_BuiltinType: TypeAlias = Union[
    None,
    bool,
    int,
    float,
    complex,
    str,
]

_ResolvedType: TypeAlias = Union[
    _BuiltinType,
    typing.Tuple[_BuiltinType, ...],
    typing.List[_BuiltinType],
]


# ###################### UNSET #############################


class _UnsetType(object):
    pass


_UNSET: Final = _UnsetType()


# ################################ CONSTANTS ###################################


NONE_MAPPED_VALUES: Final = ("none", "null", "invalid")
FALSE_MAPPED_VALUES: Final = ("false", "no", "off", "disable", "disabled")
TRUE_MAPPED_VALUES: Final = ("true", "yes", "on", "enable", "enabled")

INT_BASE_INDICATORS: Final = {"b": 2, "o": 8, "x": 16}

SEQUENCE_SEPARATOR: Final = ","
SEQUENCE_NEST_MAPPING: Final = {
    "(": ")",
    "[": "]",
    "{": "}",
}


# ################################ EXCEPTIONS ##################################


class NotResolved(Exception):
    pass


# ################################ INTERFACE ###################################


def isnone(
    s: str | None,
    /,
    *,
    none: bool = True,
    empty: bool = True,
) -> bool:
    if s is None:
        return none
    elif not s:
        return empty
    return s.lower() in NONE_MAPPED_VALUES


def isbool(
    s: str | None,
    /,
    *,
    none: bool = False,
    empty: bool = False,
) -> bool:
    if s is None:
        return none
    elif not s:
        return empty
    return (
        s.lower() in FALSE_MAPPED_VALUES
        or s.lower() in TRUE_MAPPED_VALUES
        # <format-newline>
    )


def isfalse(
    s: str | None,
    /,
    *,
    none: bool = False,
    empty: bool = False,
) -> bool:
    if s is None:
        return none
    elif not s:
        return empty
    return s.lower() in FALSE_MAPPED_VALUES


def istrue(
    s: str | None,
    /,
    *,
    none: bool = False,
    empty: bool = False,
) -> bool:
    if s is None:
        return none
    elif not s:
        return empty
    return s.lower() in TRUE_MAPPED_VALUES


@overload
def resolve(
    s: str,
    /,
) -> _ResolvedType: ...


@overload
def resolve(
    s: str,
    /,
    type: Type[T],
) -> T: ...


@overload
def resolve(
    s: str,
    /,
    type: Literal[None],
) -> Literal[None]: ...


@overload
def resolve(
    s: str,
    /,
    type: Annotated[_Ignore, "fallback"],
) -> Any: ...


def resolve(
    s: str,
    /,
    type: _Ignore = _UNSET,
) -> _Ignore:
    if isinstance(type, _UnsetType):
        return _resolve_detect(s)
    elif type is Any:
        return _resolve_detect(s)

    origin = typing.get_origin(type)
    if origin is None:
        value = _resolve_builtin(s, type)
    else:
        value = _resolve_nested(
            s,
            origin,
            type,
        )

    return value


# ################################ HELPERS #####################################


def _resolve_detect(
    s: str,
    /,
) -> _ResolvedType:
    if s.lower() in NONE_MAPPED_VALUES:
        return None

    if s.lower() in FALSE_MAPPED_VALUES:
        return False
    if s.lower() in TRUE_MAPPED_VALUES:
        return True

    intbase = INT_BASE_INDICATORS.get(s[1:2], 10)
    try:
        return int(s, intbase)
    except ValueError:
        pass

    try:
        return float(s)
    except ValueError:
        pass

    try:
        return complex(s)
    except ValueError:
        pass

    return str(s)


def _resolve_builtin(
    s: str,
    /,
    type: Union[
        Type[Any],
        Literal[None],
    ],
) -> _ResolvedType:
    if type is None:
        if s.lower() in NONE_MAPPED_VALUES:
            return None
        raise ValueError(f"invalid literal for none: {s!r}")

    elif type is str:
        return str(s)

    elif type is bool:
        if s.lower() in FALSE_MAPPED_VALUES:
            return False
        elif s.lower() in TRUE_MAPPED_VALUES:
            return True
        raise ValueError(f"invalid literal for bool: {s!r}")

    elif type is int:
        intbase = INT_BASE_INDICATORS.get(s[1:2], 10)
        return int(s, intbase)

    elif type is float:
        return float(s)

    elif type is complex:
        return complex(s)

    raise ValueError(f"invalid type hint: {type!r}")


def _resolve_nested(
    s: str,
    /,
    origin: Union[
        Type[Any],
        Annotated[Any, typing.Annotated],
    ],
    type: Union[
        Type[Any],
        Literal[None],
    ],
) -> _ResolvedType:
    if origin is typing.Annotated:
        (anntype, *_) = typing.get_args(type)
        return resolve(s, anntype)

    elif origin is typing.Union:
        for itemtype in typing.get_args(type):
            try:
                return resolve(s, itemtype)
            except ValueError:
                continue

    elif issubclass(origin, typing.List):
        (itemtype,) = typing.get_args(type)
        return list(
            resolve(itemstr, itemtype)
            for itemstr in _split_sequence(s)
            # <format-newline>
        )

    elif issubclass(origin, typing.Tuple):
        _hint = typing.get_args(type)
        if Ellipsis in _hint:
            (itemtype, _) = _hint
            return tuple(
                resolve(itemstr, itemtype)
                for itemstr in _split_sequence(s)
                # <format-newline>
            )
        else:
            return tuple(
                resolve(itemstr, itemtype)
                for (itemstr, itemtype) in builtins.zip(
                    _split_sequence(s),
                    _hint,
                )
                # <format-newline>
            )

    raise NotResolved()


def _split_sequence(
    s: str,
    /,
    *,
    sep: str = SEQUENCE_SEPARATOR,
    nest: Mapping[str, str] = SEQUENCE_NEST_MAPPING,
) -> Sequence[str]:
    items = list[str]()

    value = ""
    stack = ""
    for c in s:
        if c in nest:
            stack += nest[c]

        elif stack:
            if c == stack[-1]:
                stack = stack[:-1]

        elif c == sep:
            items.append(value.strip())

            value = ""
            continue

        value += c

    if value:
        items.append(value.strip())

    return items
