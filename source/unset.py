from typing import TypeVar


# ################################ PACKAGE #####################################


__sname__ = "unset"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "UnsetType",
    "Unsetable",
    "UNSET",
    # fmt: on
)


# ################################ TYPING ######################################


T = TypeVar("T")


# ################################ UNSET #######################################


UnsetType = type("UnsetType", (), {})

Unsetable = T | UnsetType

UNSET = UnsetType()
