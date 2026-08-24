import builtins
from typing import Any


# ################################ COMPONENT ###################################


__component__ = "builtinsutil"
__version__ = "2.0"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "typename",
    # ### RAWATTR
    "hasrawattr", "getrawattr",
    "setrawattr", "delrawattr",
    # fmt: on
)


# ################################ GLOBALS #####################################


_UNSET = object()


# ################################ FUNCTIONS ###################################


def typename(obj: Any, /, *, qual: bool = False) -> str:
    """
    Returns the type name of an object,
    or of the object itself if it already is a type.

    :param qual:
        Get the module-qualified name.
    """
    objtype = (
        obj  # <format-break>
        if isinstance(obj, builtins.type)
        else builtins.type(obj)
    )
    if qual:
        return f"{objtype.__module__}.{objtype.__qualname__}"
    else:
        return objtype.__name__


# ###################### RAWATTR ###########################


def hasrawattr(obj: Any, name: str, /) -> bool:
    """
    Returns whether an object really has an attribute,
    ignoring any attribute hooks it defines.
    """
    try:
        if isinstance(obj, builtins.type):
            builtins.type.__getattribute__(obj, name)
        else:
            builtins.object.__getattribute__(obj, name)
        return True
    except AttributeError:
        return False


def getrawattr(obj: Any, name: str, default: Any = _UNSET, /) -> Any:
    """
    Returns an attribute of an object,
    ignoring any attribute hooks it defines.
    """
    try:
        if isinstance(obj, builtins.type):
            return builtins.type.__getattribute__(obj, name)
        else:
            return builtins.object.__getattribute__(obj, name)
    except AttributeError:
        if default is not _UNSET:
            return default
        raise


def setrawattr(obj: Any, name: str, value: Any, /) -> None:
    """
    Sets an attribute of an object,
    ignoring any attribute hooks it defines.
    """
    if isinstance(obj, builtins.type):
        builtins.type.__setattr__(obj, name, value)
    else:
        builtins.object.__setattr__(obj, name, value)


def delrawattr(obj: Any, name: str, /) -> None:
    """
    Deletes an attribute of an object,
    ignoring any attribute hooks it defines.
    """
    if isinstance(obj, builtins.type):
        builtins.type.__delattr__(obj, name)
    else:
        builtins.object.__delattr__(obj, name)
