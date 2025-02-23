from typing import Any, Final, TypeAlias, TypeIs


# ################################ PACKAGE #####################################


__sname__ = "unset"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "UnsetType",
    "Unset",
    # fmt: on
)


# ###################### USAGE #############################
"""

    from unset import Unset, isunset

    def function(arg: Type | Unset = ~Unset):
        arg = arg if not isunset(arg) else VALUE

"""


# ################################ UNSET #######################################


class _UnsetType(type):

    def __invert__(self) -> "UnsetType":
        return UNSET

    @staticmethod
    def is_(obj: Any, /) -> TypeIs["UnsetType"]:
        return obj is UNSET


class UnsetType(object, metaclass=_UnsetType):

    pass


UNSET: Final = UnsetType()


# ###################### ALIASES ###########################


Unset: TypeAlias = UnsetType

isunset: Final = UnsetType.is_
