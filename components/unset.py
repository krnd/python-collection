from typing import Any, Final, TypeAlias, TypeIs, TypeVar, cast


# ################################ COMPONENT ###################################


__component__ = "unset"
__version__ = "1.5"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "UnsetType", "UNSET", "Unset", "MayUnset",
    "isunset", "on_unset",
    # fmt: on
)


# ################################ TYPING ######################################


T = TypeVar("T")

TONCE = TypeVar("TONCE")


# ################################ UNSET #######################################


class _UnsetType(type):

    def __invert__(self) -> "UnsetType":
        """Returns the unset value."""
        return UNSET


class UnsetType(object, metaclass=_UnsetType):
    """Type of the unset value."""

    pass


UNSET: Final = UnsetType()
"""Value to use if unset."""


# ###################### CONVENIENCE #######################


Unset: TypeAlias = UnsetType
"""
The `Unset` attribute is a convenience alias to simplify the usage of the
`UnsetType` and `UNSET` attributes.

It can be used as follows:
```
def function(arg: Type | Unset = ~Unset):
    arg = arg if not isunset(arg) else VALUE
    # or
    arg = on_unset(arg, VALUE)
```
"""


MayUnset: TypeAlias = T | UnsetType
"""
The `MayUnset` attribute is a convenience alias for the union of a generic type
and the `UnsetType`.

It can be used as follows:
```
def function(arg: MayUnset[Type] = ~Unset):
    arg = arg if not isunset(arg) else VALUE
    # or
    arg = on_unset(arg, VALUE)
```
"""


# ################################ FUNCTIONS ###################################


def isunset(obj: Any, /) -> TypeIs[UnsetType]:
    """Returns true if the object is unset."""
    return obj is UNSET


def on_unset(obj: T | UnsetType, value: TONCE, /) -> T | TONCE:
    """Returns either the object itself or the specified value if the object is
    unset."""
    return value if obj is UNSET else cast(T, obj)
