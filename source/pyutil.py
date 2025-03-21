import builtins
import importlib
from typing import Annotated, Any, Callable, Literal, Tuple, Union, overload


# ################################ PACKAGE #####################################


__sname__ = "pyutil"
__version__ = "1.1"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    # ########### BUILTINS #############
    "typename",
    # ########### LOCALS ###############
    "haslocal", "getlocal",
    "setlocal", "dellocal",
    # ########### GLOBALS ##############
    "hasglobal", "getglobal",
    "setglobal", "delglobal",
    # ########### OBJATTR ##############
    "hasobjattr", "getobjattr",
    "setobjattr", "delobjattr",
    # ########### DUNDER ###############
    "dunder", "dunderlizer",
    "hasdunder", "getdunder",
    "setdunder", "deldunder",
    # fmt: on
)


# ###################### UNSET #############################


_UnsetType = type("_UnsetType", (), {})

_UNSET = _UnsetType()


# ################################ FUNCTIONS ###################################


# ###################### RESOLVE ###########################


@overload
def resolve(
    objpath: str,
    /,
    *,
    namespace: str | None = ...,
) -> Annotated[Any, "object"]: ...


@overload
def resolve(
    objpath: str,
    /,
    *,
    namespace: str | None = ...,
    partial: Literal[False],
) -> Annotated[Any, "object"]: ...


@overload
def resolve(
    objpath: str,
    /,
    *,
    namespace: str | None = ...,
    partial: Literal[True],
) -> Tuple[Annotated[Any, "object"], str]: ...


@overload
def resolve(
    objpath: str,
    /,
    *,
    namespace: str | None = ...,
    partial: int,
) -> Tuple[Annotated[Any, "object"], str]: ...


def resolve(
    objpath: str,
    /,
    *,
    namespace: str | None = None,
    partial: bool | int = False,
) -> Union[
    Annotated[Any, "object"],
    Tuple[Annotated[Any, "object"], str],
]:
    if partial is False:
        partial, minsteps = False, 0
    elif partial is True:
        partial, minsteps = True, 0
    else:
        partial, minsteps = True, partial

    object = (
        importlib.import_module(namespace)
        if namespace is not None
        else builtins
        # <format-break>
    )

    pathitems = objpath.split(".")
    for step, name in enumerate(pathitems):
        try:
            object = getattr(object, name)
        except AttributeError:
            if partial and step >= minsteps:
                return (object, str.join(".", pathitems[step:]))
            raise

    return (
        (object, objpath)
        if partial
        else object
        # <format-break>
    )


# ################################ BUILTINS ####################################


def typename(obj: Any, /, *, qual: bool = False) -> str:
    objtype = (
        obj  # <format-break>
        if isinstance(obj, builtins.type)
        else builtins.type(obj)
    )
    if qual:
        name = getattr(objtype, "__name__")
        module = getattr(objtype, "__module__")
        qualname = getattr(objtype, "__qualname__", None)
        return f"{module}.{qualname or name}"
    else:
        return getattr(objtype, "__name__")


# ###################### LOCALS ###########################


def haslocal(name: str, /) -> bool:
    _locals = locals()
    return name in _locals


def getlocal(name: str, default: Any = _UNSET, /) -> Any:
    _locals = locals()
    if name in _locals:
        return _locals[name]
    if default is not _UNSET:
        return default
    raise NameError(f"name {name!r} is not defined")


def setlocal(name: str, value: Any, /) -> None:
    _locals = locals()
    _locals[name] = value


def dellocal(name: str, /) -> None:
    _locals = locals()
    del _locals[name]


# ###################### GLOBALS ###########################


def hasglobal(name: str, /) -> bool:
    _globals = globals()
    return name in _globals


def getglobal(name: str, default: Any = _UNSET, /) -> Any:
    _globals = globals()
    if name in _globals:
        return _globals[name]
    if default is not _UNSET:
        return default
    raise NameError(f"name {name!r} is not defined")


def setglobal(name: str, value: Any, /) -> None:
    _globals = globals()
    _globals[name] = value


def delglobal(name: str, /) -> None:
    _globals = globals()
    del _globals[name]


# ###################### OBJATTR ###########################


def hasobjattr(obj: Any, name: str, /) -> bool:
    try:
        object.__getattribute__(obj, name)
        return True
    except AttributeError:
        return False


def getobjattr(obj: Any, name: str, default: Any = _UNSET, /) -> Any:
    try:
        return object.__getattribute__(obj, name)
    except AttributeError:
        if default is not _UNSET:
            return default
        raise


def setobjattr(obj: Any, name: str, value: Any, /) -> None:
    object.__setattr__(obj, name, value)


def delobjattr(obj: Any, name: str, /) -> None:
    object.__delattr__(obj, name)


# ###################### DUNDER ############################


def dunder(obj: Any, name: str, /) -> str:
    objtype = (
        obj  # <format-break>
        if isinstance(obj, builtins.type)
        else builtins.type(obj)
    )
    basename = str.strip(objtype.__name__, "_")
    return f"_{basename}__{name}"


def dunderlizer(obj: Any, /) -> Callable[[str], str]:
    objtype = (
        obj  # <format-break>
        if isinstance(obj, builtins.type)
        else builtins.type(obj)
    )
    basename = str.strip(objtype.__name__, "_")
    return lambda name: f"_{basename}__{name}"


def hasdunder(obj: Any, name: str, /) -> bool:
    return hasattr(obj, dunder(obj, name))


def getdunder(obj: Any, name: str, default: Any = _UNSET, /) -> Any:
    if default is _UNSET:
        return getattr(obj, dunder(obj, name))
    else:
        return getattr(obj, dunder(obj, name), default)


def setdunder(obj: Any, name: str, value: Any, /) -> None:
    setattr(obj, dunder(obj, name), value)


def deldunder(obj: Any, name: str, /) -> None:
    delattr(obj, dunder(obj, name))
