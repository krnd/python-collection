import builtins
import functools
from types import FunctionType
from typing import Any as _Ignore
from typing import (
    Callable,
    Concatenate,
    Generic,
    ParamSpec,
    Protocol,
    TypeVar,
    overload,
)


# ################################ PACKAGE #####################################


__sname__ = "decorator"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "decorator",
    "classdecorator",
    # fmt: on
)


# ################################ TYPING ######################################


P = ParamSpec("P")

TI = TypeVar("TI", contravariant=True)
TO = TypeVar("TO", covariant=True)


class _DecoratorWithoutArguments(Protocol, Generic[TI, TO]):

    def __call__(
        self,
        func: TI,
    ) -> TO: ...


class _DecoratorWithArguments(Protocol, Generic[TI, TO, P]):

    def __call__(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Callable[[TI], TO]: ...


# ################################ FUNCTIONS ###################################


@overload
def decorator(
    decorator: Callable[[TI], TO]
) -> _DecoratorWithoutArguments[TI, TO]: ...


@overload
def decorator(
    decorator: Callable[Concatenate[TI, P], TO]
) -> _DecoratorWithArguments[TI, TO, P]: ...


def decorator(decorator: _Ignore) -> _Ignore:
    @functools.wraps(decorator)
    def _decorator(
        *args: _Ignore,
        **kwargs: _Ignore,
    ) -> _Ignore:
        if args and isinstance(args[0], FunctionType):
            return decorator(*args, **kwargs)
        return lambda func: decorator(func, *args, **kwargs)

    return _decorator


@overload
def classdecorator(
    decorator: Callable[[TI], TO]
) -> _DecoratorWithoutArguments[TI, TO]: ...


@overload
def classdecorator(
    decorator: Callable[Concatenate[TI, P], TO]
) -> _DecoratorWithArguments[TI, TO, P]: ...


def classdecorator(decorator: _Ignore) -> _Ignore:
    @functools.wraps(decorator)
    def _classdecorator(
        *args: _Ignore,
        **kwargs: _Ignore,
    ) -> _Ignore:
        if args and isinstance(args[0], builtins.type):
            return decorator(*args, **kwargs)
        return lambda cls: decorator(cls, *args, **kwargs)

    return _classdecorator
