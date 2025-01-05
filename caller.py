import inspect
from inspect import FrameInfo
from types import FrameType
from typing import Any, Dict, Literal, NamedTuple, TypedDict, Unpack, overload


# ################################ METADATA ####################################


__pkgname__ = "caller"
__version__ = "1.0"

__dependencies__ = ()


# Getting a variable from the caller's globals. What is a frame object?
# https://stackoverflow.com/questions/44107877/getting-a-variable-from-the-callers-globals-what-is-a-frame-object


# ################################ GLOBALS #####################################


__all__ = (
    # fmt: off
    "frameinfo", "frame",
    "globals", "locals",
    # fmt: on
)


# ################################ TYPING ######################################


class _FArgs(TypedDict, total=False):
    depth: int


class _FileLocation(NamedTuple):
    name: str
    line: int


# ################################ INTERFACE ###################################


def frameinfo(**fargs: Unpack[_FArgs]) -> FrameInfo:
    return _f(fargs, _info=True)


def frame(**fargs: Unpack[_FArgs]) -> FrameType:
    return _f(fargs, _info=True).frame


def file(**fargs: Unpack[_FArgs]) -> _FileLocation:
    f = _f(fargs, _info=True)
    return _FileLocation(f.filename, f.lineno)


def filename(**fargs: Unpack[_FArgs]) -> str:
    return _f(fargs, _info=True).filename


@overload
def globals(
    **fargs: Unpack[_FArgs],
) -> Dict[str, Any]: ...


@overload
def globals(
    s: str,
    /,
    **fargs: Unpack[_FArgs],
) -> Any: ...


def globals(
    s: str | None = None,
    /,
    **fargs: Unpack[_FArgs],
) -> Dict[str, Any] | Any:
    _globals = _f(fargs).f_globals
    return _globals if s is None else _globals[s]


@overload
def locals(
    **fargs: Unpack[_FArgs],
) -> Dict[str, Any]: ...


@overload
def locals(
    s: str,
    /,
    **fargs: Unpack[_FArgs],
) -> Any: ...


def locals(
    s: str | None = None,
    /,
    **fargs: Unpack[_FArgs],
) -> Dict[str, Any] | Any:
    _locals = _f(fargs).f_locals
    return _locals if s is None else _locals[s]


# ################################ HELPERS #####################################


@overload
def _f(args: _FArgs) -> FrameType: ...


@overload
def _f(args: _FArgs, *, _info: Literal[True]) -> FrameInfo: ...


def _f(args: _FArgs, *, _info: bool = False) -> FrameType | FrameInfo:
    _stack = inspect.stack()

    _depth = args.get("depth", 0)

    _frameinfo = _stack[_depth + 1]

    return _frameinfo if _info else _frameinfo.frame
