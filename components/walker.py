import fnmatch
import os
import os.path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    Final,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    NamedTuple,
    Self,
    TypeAlias,
    TypeVar,
    cast,
)


# ################################ COMPONENT ###################################


__component__ = "walker"
__version__ = "3.0"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "Walker",
    "DirWalker", "DirEntry",
    # fmt: on
)


# ################################ TYPING ######################################


TENTRY = TypeVar("TENTRY")


_YieldMode: TypeAlias = Literal["file", "dir"]


# ################################ TYPES #######################################


class _StackEntry(NamedTuple):
    scanpath: str
    """Path of the walked directory. (host-style separator)"""
    scanpathunix: str
    """Path of the walked directory. (unix-style separator)"""
    scaniter: Iterator[os.DirEntry[str]] | None
    """Iterator instance of the walked directory."""
    dirqueue: List[str]
    """Pending directories inside the walked directory."""


# ################################ WALKER ######################################


class Walker(ABC, Generic[TENTRY], Iterator[TENTRY]):
    """
    Depth-first iterator over the directory tree below a base path.
    (The iterator is single-pass and cannot be restarted.)

    Junctions are not supported and raise `NotImplementedError` unless they
    are excluded beforehand.
    """

    basepath: Final[str]
    """Path from which to start."""

    symlinks: Final[bool]
    """Whether to follow symbolic links."""
    _unixstyle: Final[bool]
    """Whether paths using the unix-style separator must be generated."""

    mode: Final[_YieldMode | None]
    """
    Indicates what types of entries should be yielded.
    - `file` -- Only yield files.
    - `dir` -- Only yield directories.
    """
    _yielddir: Final[bool]
    """Whether to yield directories."""
    _yieldfile: Final[bool]
    """Whether to yield files."""

    _ignores: Final[List[str] | None]
    """
    Directory name patterns to ignore.
    (`fnmatch`-style)
    """
    _includes: Final[List[str] | None]
    """
    Entry name patterns to include when yielding.
    (`fnmatch`-style)
    """
    _excludes: Final[List[str] | None]
    """
    Entry name patterns to exclude when yielding.
    (`fnmatch`-style)
    """
    _skiplist: List[str]
    """
    Dynamic list of skipped entry names.
    (The skip list is only valid for the currently walked directory.)
    """

    _scanpath: str
    """Path of the currently walked directory. (host-style separator)"""
    _scanpathunix: str
    """Path of the currently walked directory. (unix-style separator)"""
    _scaniter: Iterator[os.DirEntry[str]] | None
    """Iterator instance of the currently walked directory."""
    _dirqueue: List[str]
    """Pending directories inside the currently walked directory."""

    _stack: List[_StackEntry]
    """Stack of all currently walked directories. (depth-first)"""

    def __init__(
        self,
        path: str,
        mode: _YieldMode | None = None,
        *,
        ignore: Iterable[str] | None = None,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
        symlinks: bool = True,
    ) -> None:
        """
        :param path:
            Path from which to start.
        :param mode:
            Indicates what types of entries should be yielded.
        :param ignore:
            Directory name patterns to ignore.
            (`fnmatch`-style)
        :param include:
            Entry name patterns to include when yielding.
            (`fnmatch`-style)
        :param exclude:
            Entry name patterns to exclude when yielding.
            (`fnmatch`-style)
        :param symlinks:
            Whether to follow symbolic links.
        """

        self.basepath = os.path.abspath(path)

        self.symlinks = symlinks
        self._unixstyle = os.sep != "/"

        self.mode = mode
        self._yielddir = mode is None or mode == "dir"
        self._yieldfile = mode is None or mode == "file"

        self._ignores = list(ignore) if ignore is not None else None
        self._includes = list(include) if include is not None else None
        self._excludes = list(exclude) if exclude is not None else None
        self._skiplist = list()

        self._scanpath = ""
        self._scanpathunix = ""
        self._scaniter = None
        self._dirqueue = list()

        self._stack = list()

        # Add the starting directory to the pending directories.
        self._dirqueue.append("")

    @property
    def path(self) -> str:
        """
        Absolute path of the currently walked directory.
        (host-style separator)
        """
        return (
            os.path.join(self.basepath, self._scanpath)
            if self._scanpath
            else self.basepath
        )

    def skip(self, name: str, /) -> None:
        """
        Adds a name to the skip list.
        (The skip list is only valid for the currently walked directory.)
        """
        self._skiplist.append(name)

    @abstractmethod
    def create_entry(self, entry: os.DirEntry[str], path: str) -> TENTRY:
        """
        Creates an entry object from the yielded `os.DirEntry`.

        :param entry:
            The `os.DirEntry` from which to create the entry.
        :param path:
            Absolute path of the entry. (unix-style separator)
        """
        ...

    def check_ignore(self, entry: os.DirEntry[str], path: str) -> bool:
        """
        Returns whether a directory should be ignored.
        (Ignored directories are neither yielded nor walked into.)

        :param entry:
            The `os.DirEntry` of the directory to check.
        :param path:
            Absolute path of the directory.
            (unix-style separator)
        """
        return False

    def on_enter(self, path: str) -> None:
        """
        Callback executed upon entering a directory.
        (The path uses unix-style separators.)
        """
        pass

    def on_exit(self, path: str) -> None:
        """
        Callback executed upon exiting a directory.
        (The path uses unix-style separators.)
        """
        pass

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> TENTRY:  # noqa: C901
        while True:
            # Prevents the type checker from reporting unbound variable.
            entry = None

            if self._scaniter is not None:
                try:
                    entry = next(self._scaniter)
                except StopIteration:
                    self._scaniter = None

            if self._scaniter is None:
                # The skip list is only valid for the currently walked
                # directory. In order for the `on_enter` or `on_exit` callbacks
                # to modify the skip list, it must be cleared beforehand.
                self._skiplist.clear()

                self.__next_dir__()

                continue

            # The entry is guaranteed to be present at this point.
            entry = cast(os.DirEntry[str], entry)
            # Absolute path of the entry using unix-style separator.
            _upath = (
                entry.path.replace(os.sep, "/")
                if self._unixstyle
                else entry.path
            )

            if entry.name in self._skiplist:
                continue

            if entry.is_dir():

                if self._ignores and any(
                    fnmatch.fnmatchcase(entry.name, filter)
                    for filter in self._ignores
                ):
                    continue
                elif self.check_ignore(entry, _upath):
                    continue

                if entry.is_junction():
                    raise NotImplementedError(
                        f"junctions are not supported ({entry.path})",
                    )

                if not entry.is_symlink():
                    self._dirqueue.append(entry.name)
                elif self.symlinks:
                    self._dirqueue.append(entry.name)
                else:
                    continue

                if not self._yielddir:
                    continue

            else:

                if not self._yieldfile:
                    continue

            if self._includes and not any(
                fnmatch.fnmatchcase(entry.name, filter)
                for filter in self._includes
            ):
                continue
            elif self._excludes and any(
                fnmatch.fnmatchcase(entry.name, filter)
                for filter in self._excludes
            ):
                continue

            break

        return self.create_entry(entry, _upath)

    def __next_dir__(self) -> None:
        while self._dirqueue:
            scanpath = os.path.join(
                self._scanpath,
                self._dirqueue.pop(0),
            )
            scanpathunix = (
                scanpath.replace(os.sep, "/")
                if self._unixstyle
                else scanpath  #
            )

            self._stack.append(
                _StackEntry(
                    self._scanpath,
                    self._scanpathunix,
                    self._scaniter,
                    self._dirqueue,
                )
            )

            self._scanpath = scanpath
            self._scanpathunix = scanpathunix
            self._scaniter = os.scandir(
                os.path.join(
                    self.basepath,
                    scanpath,
                )
            )
            self._dirqueue = list()

            self.on_enter(scanpathunix)

            return

        if self._stack:
            _stackentry = self._stack.pop()

            self.on_exit(self._scanpathunix)

            self._scanpath = _stackentry.scanpath
            self._scanpathunix = _stackentry.scanpathunix
            self._scaniter = _stackentry.scaniter
            self._dirqueue = _stackentry.dirqueue

            return

        raise StopIteration()


# ################################ BUILTIN #####################################


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class DirEntry:
    """Immutable `os.DirEntry` wrapper with precomputed paths."""

    # TODO Comparing by inode is only reliable within a single drive.
    # The inode numbers are reused across drives, so entries from different
    # drives can end up treated as the same entry. Including the drive
    # (`stat().st_dev`) would fix it, at the cost of an extra `stat()` call.

    _entry: os.DirEntry[str]
    """Actual `os.DirEntry` as yielded internally by the walker."""

    name: str
    """Name of the entry."""
    path: str
    """
    Path of the entry relative to the base path of the walker.
    (unix-style separator)
    """
    dirpath: str
    """
    Path of the entry's directory relative to the base path of the walker.
    (unix-style separator)
    """
    rpath: str
    """Absolute path of the entry. (host-style separator)"""
    upath: str
    """Absolute path of the entry. (unix-style separator)"""

    def is_dir(self) -> bool:
        """
        Returns whether the entry is a directory or a symbolic link pointing to a directory.
        """
        return self._entry.is_dir()

    def is_file(self) -> bool:
        """
        Returns whether the entry is a file or a symbolic link pointing to a file.
        """
        return self._entry.is_file()

    def is_symlink(self) -> bool:
        """
        Returns whether the entry is a symbolic link.
        """
        return self._entry.is_symlink()

    def stat(self) -> os.stat_result:
        """
        Returns a `stat_result` object for this entry.
        """
        return self._entry.stat()

    def __eq__(self, other: object, /) -> bool:
        return (
            (self._entry.inode() == other._entry.inode())
            if isinstance(other, DirEntry)
            else False
        )

    def __hash__(self) -> int:
        return self._entry.inode()

    def __repr__(self) -> str:
        kind = "Directory" if self._entry.is_dir() else "File"
        return f"<{kind!s} {self.path!r}>"


class DirWalker(Walker[DirEntry]):
    """Walker yielding `DirEntry` entries."""

    def create_entry(
        self,
        entry: os.DirEntry[str],
        path: str,
    ) -> DirEntry:
        return DirEntry(
            entry,
            entry.name,
            # Prefer unix-style instead of host-style separator.
            #   os.path.join(self._scanpath, entry.name)
            (
                f"{self._scanpathunix}/{entry.name}"
                if self._scanpathunix
                else entry.name
            ),
            # Prefer unix-style instead of host-style separator.
            #   self._scanpath
            self._scanpathunix,
            entry.path,
            path,
        )
