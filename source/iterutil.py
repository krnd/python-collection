from typing import Callable, Iterable, TypeVar, overload


# ################################ PACKAGE #####################################


__sname__ = "iterutil"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = ()


# ###################### UNSET #############################


_UnsetType = type("_UnsetType", (), {})

_UNSET = _UnsetType()


# ################################ TYPING ######################################


T = TypeVar("T")
TD = TypeVar("TD")


# ################################ FUNCTIONS ###################################


@overload
def first(
    source: Iterable[T],
    /,
) -> T: ...


@overload
def first(
    source: Iterable[T],
    /,
    *,
    default: TD,
) -> T | TD: ...


@overload
def first(
    source: Iterable[T],
    /,
    predicate: Callable[[T], bool],
) -> T: ...


@overload
def first(
    source: Iterable[T],
    /,
    predicate: Callable[[T], bool],
    *,
    default: TD,
) -> T | TD: ...


def first(
    source: Iterable[T],
    /,
    predicate: Callable[[T], bool] | None = None,
    *,
    default: TD | _UnsetType = _UNSET,
) -> T | TD:
    if predicate is not None:
        _iter = iter(item for item in iter(source) if predicate(item))
    else:
        _iter = iter(source)
    return (
        next(_iter)  # type: ignore
        if default is _UNSET
        else next(_iter, default)
    )
