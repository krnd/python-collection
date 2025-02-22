import builtins
from typing import Any, Callable, Final, Iterable, Mapping, Tuple, TypeAlias


# ################################ PACKAGE #####################################


__sname__ = "mapping"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = ()


# ################################ TYPING ######################################


_MappingCallable: TypeAlias = Callable[
    [Iterable[Tuple[str, Any]]],
    Mapping[str, Any],
]

_JoinCallable: TypeAlias = Callable[[str, str], str]


# ################################ FINALS ######################################


DEFAULT_FLATTEN_JOIN: Final = "."


# ################################ FUNCTIONS ###################################


# ###################### FLATTEN ###########################


def flatten(
    mapping: Mapping[str, Any],
    /,
    start: str | None = None,
    *,
    join: _JoinCallable | str = DEFAULT_FLATTEN_JOIN,
    type: _MappingCallable | None = None,
) -> Mapping[str, Any]:
    mapping_type = (
        type
        or builtins.type(mapping)
        # <format-break>
    )
    return mapping_type(
        _flatteniterator(
            mapping,
            start,
            join=join,
        )  # pyright: ignore[reportCallIssue]
    )


def _flatteniterator(
    mapping: Mapping[str, Any],
    /,
    basekey: str | None,
    *,
    join: _JoinCallable | str,
) -> Iterable[Tuple[str, Any]]:
    for key, value in mapping.items():

        if basekey is None:
            flatkey = key
        elif isinstance(join, str):
            flatkey = basekey + join + key
        else:
            flatkey = join(basekey, key)

        if isinstance(value, Mapping):
            yield from _flatteniterator(
                value,
                flatkey,
                join=join,
            )
        else:
            yield (flatkey, value)
