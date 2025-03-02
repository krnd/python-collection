import inspect
from inspect import FrameInfo
from types import EllipsisType, FrameType
from typing import (
    Annotated,
    Any,
    Dict,
    NamedTuple,
    TypedDict,
    Union,
    Unpack,
    overload,
)


# ################################ PACKAGE #####################################


__sname__ = "caller"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = ()


# ################################ TYPING ######################################


class _fArgs(TypedDict, total=False):
    depth: int


class _FileLocation(NamedTuple):
    name: str
    line: int


# ################################ FUNCTIONS ###################################


def frameinfo(**fargs: Unpack[_fArgs]) -> FrameInfo:
    return _f(fargs, ...)


def frame(**fargs: Unpack[_fArgs]) -> FrameType:
    return _f(fargs, ...).frame


def function(**fargs: Unpack[_fArgs]) -> str:
    return _f(fargs, ...).function


def file(**fargs: Unpack[_fArgs]) -> _FileLocation:
    f = _f(fargs, ...)
    return _FileLocation(f.filename, f.lineno)


def filename(**fargs: Unpack[_fArgs]) -> str:
    return _f(fargs, ...).filename


# ###################### FRAME #############################


@overload
def globals(
    **fargs: Unpack[_fArgs],
) -> Dict[str, Any]: ...


@overload
def globals(
    s: str,
    /,
    **fargs: Unpack[_fArgs],
) -> Any: ...


def globals(
    s: str | None = None,
    /,
    **fargs: Unpack[_fArgs],
) -> Dict[str, Any] | Any:
    _globals = _f(fargs).f_globals
    return _globals if s is None else _globals[s]


@overload
def locals(
    **fargs: Unpack[_fArgs],
) -> Dict[str, Any]: ...


@overload
def locals(
    s: str,
    /,
    **fargs: Unpack[_fArgs],
) -> Any: ...


def locals(
    s: str | None = None,
    /,
    **fargs: Unpack[_fArgs],
) -> Dict[str, Any] | Any:
    _locals = _f(fargs).f_locals
    return _locals if s is None else _locals[s]


# ################################ HELPERS #####################################


@overload
def _f(args: _fArgs) -> FrameType: ...


@overload
def _f(args: _fArgs, _info: EllipsisType) -> FrameInfo: ...


def _f(
    args: _fArgs,
    _info: EllipsisType | None = None,
) -> Union[
    Annotated[FrameType, ...],
    Annotated[FrameInfo, "_info"],
]:
    _stack = inspect.stack()
    _depth = args.get("depth", 0)
    _frameinfo = _stack[_depth + 1]
    return _frameinfo if _info else _frameinfo.frame
