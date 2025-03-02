import builtins
from typing import Callable, Iterable, Sequence, TypeAlias, TypeVar


# ################################ PACKAGE #####################################


__sname__ = "sequence"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = ()


# ################################ TYPING ######################################


T = TypeVar("T")
T0 = TypeVar("T0")


# ################################ TYPES ######################################


_SequenceCallable: TypeAlias = Callable[
    [Iterable[T]],
    Sequence[T],
]


# ################################ FUNCTIONS ###################################


def rpad(
    sequence: Sequence[T],
    /,
    length: int,
    fill: T | T0,
    *,
    type: _SequenceCallable[T | T0] | None = None,
    trim: bool = False,
) -> Sequence[T | T0]:
    sequence_type = (
        type
        or builtins.type(sequence)
        # <format-break>
    )
    return sequence_type(
        _rpaditerator(
            sequence,
            length,
            fill,
            trim=trim,
        )  # pyright: ignore[reportCallIssue]
    )


def _rpaditerator(
    sequence: Sequence[T],
    /,
    length: int,
    fill: T0,
    *,
    trim: bool,
) -> Iterable[T | T0]:
    count = 0
    for value in sequence:
        if count < length or not trim:
            yield value
        elif trim:
            break
        count += 1
    if count < length:
        for _ in range(length - count):
            yield fill


def lpad(
    sequence: Sequence[T],
    /,
    length: int,
    fill: T | T0,
    *,
    type: _SequenceCallable[T | T0] | None = None,
    trim: bool = False,
) -> Sequence[T | T0]:
    sequence_type = (
        type
        or builtins.type(sequence)
        # <format-break>
    )
    return sequence_type(
        _lpaditerator(
            sequence,
            length,
            fill,
            trim=trim,
        )  # pyright: ignore[reportCallIssue]
    )


def _lpaditerator(
    sequence: Sequence[T],
    /,
    length: int,
    fill: T0,
    *,
    trim: bool,
) -> Iterable[T | T0]:
    count = (
        (length - len(sequence))
        if len(sequence) < length
        else 0
        # <format-break>
    )
    if count > 0:
        for _ in range(count):
            yield fill
    for value in sequence:
        if count < length or not trim:
            yield value
        elif trim:
            break
        count += 1
