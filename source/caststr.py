import builtins
import typing
from types import EllipsisType, NoneType
from typing import Annotated
from typing import Any
from typing import Any as _Ignore
from typing import (
    Final,
    Iterable,
    Mapping,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    overload,
)


# ################################ PACKAGE #####################################


__sname__ = "caststr"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "isnone", "isbool", "isfalse", "istrue",
    "resolve",
    # fmt: on
)


# ###################### UNSET #############################


_UNSET: Final = object()


# ################################ TYPING ######################################


T = TypeVar("T")


# ################################ COSTANTS ####################################


NONE_MAPPED_VALUES: Final = ("none", "null", "invalid")
FALSE_MAPPED_VALUES: Final = ("false", "no", "off", "disable", "disabled")
TRUE_MAPPED_VALUES: Final = ("true", "yes", "on", "enable", "enabled")

INT_BASE_INDICATORS: Final = {"b": 2, "o": 8, "x": 16}

SEQUENCE_DELIMITERS: Final = ("()", "[]")
SEQUENCE_SEPARATOR: Final = ","

MAPPING_DELIMITERS: Final = ("{}",)
MAPPING_SEPARATOR: Final = ","
MAPPING_DIVIDER: Final = ":"

GROUPINGS: Final = {k: v for k, v in ("()", "[]", "{}", "''", '""')}


# ################################ FUNCTIONS ###################################


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


# ###################### RESOLVE ###########################


@overload
def resolve(
    s: str,
    /,
) -> Any: ...


@overload
def resolve(
    s: str,
    /,
    type: None,
) -> None: ...


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
    type: Any,
) -> Any: ...


def resolve(
    s: str,
    /,
    type: Any = _UNSET,
) -> _Ignore:
    return _resolve.call(s, type, _depth=0)


# ################################ INTERNALS ###################################


class _resolve:

    @staticmethod
    def call(
        s: str,
        /,
        type: _Ignore,
        *,
        _depth: int,
    ) -> _Ignore:
        if type is _UNSET:
            return _resolve.auto(s, _depth=_depth)
        elif type is Any:
            return _resolve.auto(s, _depth=_depth)

        origin = typing.get_origin(type)
        if origin is None:
            value = _resolve.primitive(s, type)
        else:
            value = _resolve.origin(s, origin, type, _depth=_depth)

        return value

    @staticmethod
    def auto(  # noqa: C901
        s: str,
        /,
        *,
        _depth: int,
    ) -> _Ignore:
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

        try:
            _mapping = _resolve.mapping(s)
        except ValueError:
            pass
        else:
            return dict(
                (
                    _resolve.auto(keystr, _depth=(_depth + 1)),
                    _resolve.auto(valuestr, _depth=(_depth + 1)),
                )
                for keystr, valuestr in _mapping
            )

        try:
            _sequence = _resolve.sequence(s, nodelim=(_depth == 0))
        except ValueError:
            pass
        else:
            return list(
                _resolve.auto(itemstr, _depth=(_depth + 1))
                for itemstr in _sequence  # <format-break>
            )

        return s

    @staticmethod
    def primitive(  # noqa: C901
        s: str,
        /,
        type: Any,
    ) -> _Ignore:
        if type is None:
            if s.lower() in NONE_MAPPED_VALUES:
                return None
            raise ValueError(f"invalid none: {s!r}")

        elif type is str:
            return str(s)

        elif type is bool:
            if s.lower() in FALSE_MAPPED_VALUES:
                return False
            elif s.lower() in TRUE_MAPPED_VALUES:
                return True
            raise ValueError(f"invalid bool: {s!r}")

        elif type is int:
            intbase = INT_BASE_INDICATORS.get(s[1:2], 10)
            return int(s, intbase)

        elif type is float:
            return float(s)

        elif type is complex:
            return complex(s)

        elif type is bytes:
            return bytes(s, encoding="utf-8")

        raise ValueError(f"invalid type: {type!r}")

    @staticmethod
    def origin(  # noqa: C901
        s: str,
        /,
        origin: Any,
        type: Any,
        *,
        _depth: int,
    ) -> _Ignore:
        if origin is typing.Annotated:
            (anntype, *_) = typing.get_args(type)
            return _resolve.call(s, anntype, _depth=(_depth + 1))

        elif origin is typing.Union:
            for itemtype in typing.get_args(type):
                try:
                    return _resolve.call(s, itemtype, _depth=(_depth + 1))
                except ValueError:
                    continue

        elif issubclass(origin, typing.Tuple):
            _itemtypes = typing.get_args(type)
            if Ellipsis in _itemtypes:
                (itemtype, _) = _itemtypes
                return tuple(
                    _resolve.call(itemstr, itemtype, _depth=(_depth + 1))
                    for itemstr in _resolve.sequence(s, nodelim=(_depth == 0))
                )
            else:
                return tuple(
                    _resolve.call(itemstr, itemtype, _depth=(_depth + 1))
                    for (itemstr, itemtype) in builtins.zip(
                        _resolve.sequence(s, nodelim=(_depth == 0)),
                        _itemtypes,
                        strict=True,
                    )
                )

        elif issubclass(origin, typing.List):
            (itemtype,) = typing.get_args(type)
            return list(
                _resolve.call(itemstr, itemtype, _depth=(_depth + 1))
                for itemstr in _resolve.sequence(s, nodelim=(_depth == 0))
            )

        elif issubclass(origin, typing.Dict):
            (keytype, valuetype) = typing.get_args(type)
            return dict(
                (
                    _resolve.call(keystr, keytype, _depth=(_depth + 1)),
                    _resolve.call(valuestr, valuetype, _depth=(_depth + 1)),
                )
                for keystr, valuestr in _resolve.mapping(s)
            )

        raise ValueError(s, origin, type)

    @staticmethod
    def sequence(
        s: str,
        /,
        *,
        nodelim: bool,
    ) -> Iterable[str]:
        sfirst, slast = s[0], s[-1]
        for ldelim, rdelim in SEQUENCE_DELIMITERS:
            if sfirst == ldelim and slast == rdelim:
                unpack = 1
                break
        else:
            if nodelim and slast == SEQUENCE_SEPARATOR:
                unpack = -1
            elif nodelim and SEQUENCE_SEPARATOR in s:
                unpack = 0
            else:
                raise ValueError(f"invalid sequence: {s!r}")
        return _split(
            s,
            SEQUENCE_SEPARATOR,
            grouping=GROUPINGS,
            unpack=unpack,
        )

    @staticmethod
    def mapping(
        s: str,
        /,
    ) -> Iterable[Tuple[str, str]]:
        sfirst, slast = s[0], s[-1]
        for ldelim, rdelim in MAPPING_DELIMITERS:
            if sfirst == ldelim and slast == rdelim:
                unpack = 1
                break
        else:
            raise ValueError(f"invalid mapping: {s!r}")
        return (
            _partition(itemstr, MAPPING_DIVIDER)
            for itemstr in _split(
                s,
                MAPPING_SEPARATOR,
                grouping=GROUPINGS,
                unpack=unpack,
            )
        )


# ################################ HELPERS #####################################


def _split(
    s: str,
    /,
    sep: Annotated[str, "char"],
    *,
    grouping: Mapping[str, str],
    unpack: int,
) -> Iterable[str]:
    stack, start = "", (0 if unpack < 0 else unpack)
    for index, c in enumerate(s):
        if index < start:
            continue
        elif stack and c == stack[-1]:
            stack = stack[:-1]
        elif c in grouping:
            stack += grouping[c]
        elif stack:
            pass
        elif c == sep:
            yield s[start:index]
            start = index + 1
    if stack:
        raise ValueError(f"invalid split: {s!r}")
    if unpack < 0:
        if _slast := s[start:unpack]:
            yield _slast
    else:
        yield s[start : (-unpack or None)]


def _partition(
    s: str,
    /,
    sep: Annotated[str, "char"],
) -> Tuple[str, str]:
    sleft, is_split, sright = s.partition(sep)
    if is_split:
        return sleft, sright
    raise ValueError(f"invalid partition: {s!r}")


# ################################ DEBUG #######################################


def print(obj: Any, /) -> None:
    def _print(obj: _Ignore, /, *, end: str = "\n") -> None:
        typename = (
            str.removesuffix(type(obj).__name__, "Type")
            if isinstance(obj, (NoneType, EllipsisType))
            else type(obj).__name__
        )
        builtins.print(
            f"<{typename}> {obj!r}",
            end=end,
        )

    if isinstance(obj, (str, bytes)):
        _print(obj)
    elif isinstance(obj, Mapping):
        for key, value in obj.items():
            _print(key, end="\n :: ")
            _print(value)
    elif isinstance(obj, Sequence):
        for item in obj:
            _print(item)
    else:
        _print(obj)
