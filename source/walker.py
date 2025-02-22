import fnmatch
import os
import os.path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import DirEntry
from typing import (
    Final,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    NamedTuple,
    Self,
    TypeVar,
)


# ################################ PACKAGE #####################################


__sname__ = "walker"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "Walker",
    # fmt: on
)


# ################################ TYPING ######################################


TENTRY = TypeVar("TENTRY")


# ################################ TYPES #######################################


class _StackEntry(NamedTuple):
    scanpath: str
    scaniter: Iterator[DirEntry[str]] | None
    dirqueue: List[str]


# ################################ WALKER ######################################


class Walker(ABC, Generic[TENTRY], Iterator[TENTRY]):
    # ################## FIELDS ############################

    basepath: Final[str]

    symlinks: Final[bool]

    _ignore: List[str]
    _skiplist: List[str]

    scanpath: str
    _scaniter: Iterator[DirEntry[str]] | None
    _dirqueue: List[str]

    _stack: List[_StackEntry]

    # ################## STRUCTORS #########################

    def __init__(
        self,
        path: str,
        *,
        ignore: Iterable[str] | None = None,
        skip: Iterable[str] | None = None,
        symlinks: bool = True,
    ) -> None:
        self.basepath = os.path.abspath(path)

        self.symlinks = symlinks

        self._ignore = list(ignore or ())
        self._skiplist = list(skip or ())

        self.scanpath = ""
        self._scaniter = None
        self._dirqueue = list()

        self._stack = list()

        self._dirqueue.append("")

    # ################## BASECLASS #########################

    @abstractmethod
    def make_entry(self, entry: DirEntry[str]) -> TENTRY: ...

    def on_enter(self, path: str) -> None: ...
    def on_exit(self, path: str) -> None: ...

    # ################## ITERATOR ##########################

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> TENTRY:
        while True:
            entry = None

            if self._scaniter:
                try:
                    entry = next(self._scaniter)
                except StopIteration:
                    self._scaniter = None

            if self._scaniter is None:
                self.__next_dir__()
                continue

            assert entry is not None, (
                f"Variable {'entry'!r} is unexpectedly unset."
                f" ({self.scanpath!r})"
            )

            if entry.name in self._skiplist:
                continue
            elif any(
                fnmatch.fnmatchcase(entry.name, filter)
                for filter in self._ignore
            ):
                continue

            if entry.is_junction():
                raise NotImplementedError(
                    f"Junctions are currently not supported."
                    f" ({entry.path!r})"
                )

            if entry.is_dir() and (not entry.is_symlink() or self.symlinks):
                self._dirqueue.append(entry.name)

            break

        return self.make_entry(entry)

    def __next_dir__(self) -> bool:
        while self._dirqueue:
            _dirname = self._dirqueue.pop(0)

            scanpath = os.path.join(self.scanpath, _dirname)

            if _dirname in self._skiplist:
                continue

            self._stack.append(
                _StackEntry(
                    self.scanpath,
                    self._scaniter,
                    self._dirqueue,
                )
            )

            self.scanpath = scanpath
            self._scaniter = os.scandir(
                os.path.join(
                    self.basepath,
                    scanpath,
                )
            )
            self._dirqueue = list()

            self.on_enter(scanpath)

            return True

        if self._stack:
            _stackentry = self._stack.pop()

            self.on_exit(self.scanpath)

            self.scanpath = _stackentry.scanpath
            self._scaniter = _stackentry.scaniter
            self._dirqueue = _stackentry.dirqueue

            return False

        raise StopIteration()


# ################################ GENERIC #####################################


@dataclass(eq=False, frozen=True, slots=True)
class _DirEntry:
    entry: DirEntry[str]
    name: str
    path: str
    rpath: str
    type: Literal["dir", "file"]
    symlink: bool


class DirWalker(Walker[_DirEntry]):
    def make_entry(self, entry: DirEntry[str]) -> _DirEntry:
        return _DirEntry(
            entry,
            entry.name,
            os.path.join(self.scanpath, entry.name),
            entry.path,
            ("file" if entry.is_file() else "dir"),
            entry.is_symlink(),
        )
