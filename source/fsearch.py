import glob as _internalglob
import itertools
import os.path
from typing import (
    Annotated,
    Callable,
    Iterable,
    Literal,
    Sequence,
    TypeVar,
    Union,
    overload,
)


# ################################ PACKAGE #####################################


__sname__ = "fsearch"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = ()


# ################################ TYPING ######################################


TCONTAINER = TypeVar("TCONTAINER", bound=Sequence[str])


_NewContainerCallable = Callable[[Iterable[str]], TCONTAINER]


# ################################ FUNCTIONS ###################################


def paths(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    container: _NewContainerCallable[TCONTAINER] = list,
    basepath: str | None = None,
) -> TCONTAINER:
    return container(
        _searchpaths(
            paths,
            filenames,
            extensions,
            basepath=basepath,
        )
    )


# ###################### FIND ##############################


def _finditer(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    basepath: str | None = None,
) -> Iterable[str]:
    for searchpath in _searchpaths(
        paths,
        filenames,
        extensions,
        basepath=basepath,
    ):
        if os.path.isfile(searchpath):
            yield searchpath


@overload
def find(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    basepath: str | None = ...,
) -> str | None: ...


@overload
def find(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    basepath: str | None = ...,
    exists: Literal[False],
) -> str | None: ...


@overload
def find(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    basepath: str | None = ...,
    exists: Literal[True],
) -> str: ...


@overload
def find(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    basepath: str | None = ...,
    exists: bool = ...,
) -> str | None: ...


def find(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    basepath: str | None = None,
    exists: bool = False,
) -> str | None:
    _iterable = _finditer(
        paths,
        filenames,
        extensions,
        basepath=basepath,
    )
    return (
        next(iter(_iterable))
        if exists
        else next(
            iter(_iterable),
            None,  # default
        )
    )


@overload
def findall(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    basepath: str | None = ...,
) -> Iterable[str]: ...


@overload
def findall(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    container: _NewContainerCallable[TCONTAINER],
    basepath: str | None = ...,
) -> TCONTAINER: ...


def findall(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    container: _NewContainerCallable[TCONTAINER] | None = None,
    basepath: str | None = None,
) -> Union[
    Annotated[Iterable[str], "iterable"],
    Annotated[TCONTAINER, "container"],
]:
    _iterable = _finditer(
        paths,
        filenames,
        extensions,
        basepath=basepath,
    )
    return (
        container(_iterable)
        if container
        else _iterable
        # <format-break>
    )


# ###################### GLOB ##############################


def _globiter(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    basepath: str | None = None,
    recursive: bool = True,
) -> Iterable[str]:
    for searchpath in _searchpaths(
        paths,
        filenames,
        extensions,
        basepath=basepath,
    ):
        yield from (
            _path
            for _path in _internalglob.iglob(
                searchpath,
                recursive=recursive,
            )
            if os.path.isfile(_path)
        )


def glob(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    basepath: str | None = None,
    recursive: bool = True,
) -> str | None:
    return next(
        iter(
            _globiter(
                paths,
                filenames,
                extensions,
                basepath=basepath,
                recursive=recursive,
            )
        ),
        None,  # default
    )


@overload
def globall(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    basepath: str | None = ...,
    recursive: bool = ...,
) -> Iterable[str]: ...


@overload
def globall(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    container: _NewContainerCallable[TCONTAINER],
    basepath: str | None = ...,
    recursive: bool = ...,
) -> TCONTAINER: ...


def globall(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    /,
    *,
    container: _NewContainerCallable[TCONTAINER] | None = None,
    basepath: str | None = None,
    recursive: bool = True,
) -> Union[
    Annotated[Iterable[str], "iterable"],
    Annotated[TCONTAINER, "container"],
]:
    _iterable = _globiter(
        paths,
        filenames,
        extensions,
        basepath=basepath,
        recursive=recursive,
    )
    return (
        container(_iterable)
        if container
        else _iterable
        # <format-break>
    )


# ################################ HELPERS #####################################


def _searchpaths(
    paths: Iterable[str] | str,
    filenames: Iterable[str] | str,
    extensions: Iterable[str] | str,
    *,
    basepath: str | None,
) -> Iterable[str]:
    _paths = (
        (paths,)
        if isinstance(paths, str)
        else paths
        # <format-newline>
    )
    _filenames = (
        (filenames,)
        if isinstance(filenames, str)
        else filenames
        # <format-newline>
    )
    _extensions = (
        (extensions,)
        if isinstance(extensions, str)
        else extensions
        # <format-newline>
    )

    for fpath, fname, fext in (
        itertools.product(_paths, _filenames, _extensions)
        # <format-newline>
    ):
        fext = (
            f".{fext}"
            if fext and fext[0] != "."
            else fext
            # <format-break>
        )

        fullpath = os.path.join(fpath, fname + fext)

        if basepath:
            fullpath = os.path.join(basepath, fullpath)

        yield os.path.abspath(fullpath)
