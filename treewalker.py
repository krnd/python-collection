import os
import os.path
from abc import ABC, abstractmethod
from os import DirEntry
from typing import (
    Callable,
    Final,
    Generic,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Self,
    Set,
    TypeVar,
)


# ################################ METADATA ####################################


__pkgname__ = "treewalker"
__version__ = "1.0"

__dependencies__ = ()


# ################################ GLOBALS #####################################


__all__ = (
    # fmt: off
    "TreeWalker",
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


class TreeWalker(ABC, Generic[TENTRY], Iterator[TENTRY]):
    # ################## FIELDS ############################

    basepath: Final[str]

    _ignored_names: Set[str]
    _ignored_prefixes: List[str]
    _ignored_suffixes: List[str]
    _ignore: Callable[[DirEntry[str]], bool] | None

    scanpath: str
    _scaniter: Iterator[DirEntry[str]] | None
    _dirqueue: List[str]

    _stack: List[_StackEntry]

    # ################## STRUCTORS #########################

    def __init__(
        self,
        path: str,
        *,
        ignored_names: Iterable[str] | None = None,
        ignored_prefixes: Iterable[str] | None = None,
        ignored_suffixes: Iterable[str] | None = None,
        ignore: Callable[[DirEntry[str]], bool] | None = None,
    ) -> None:
        self.basepath = os.path.abspath(path)

        self._ignored_names = set(ignored_names or ())
        self._ignored_prefixes = list(ignored_prefixes or ())
        self._ignored_suffixes = list(ignored_suffixes or ())
        self._ignore = ignore

        self.scanpath = ""
        self._scaniter = None
        self._dirqueue = list()

        self._stack = list()

        self._dirqueue.append("")

    # ################## ABSTRACT ##########################

    @abstractmethod
    def make_entry(self, entry: DirEntry[str]) -> TENTRY: ...

    def on_enter(self, path: str) -> None: ...
    def on_exit(self, path: str) -> None: ...

    # ################## ITERATOR ##########################

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> TENTRY:  # noqa: C901
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
                # <format-break>
            )

            if entry.is_symlink():
                raise NotImplementedError(
                    "Symbolic links are currently not supported."
                    f" ({entry.path!r})"
                    # <format-break>
                )

            if entry.name in self._ignored_names:
                continue
            elif any(
                entry.name.startswith(prefix)
                for prefix in self._ignored_prefixes
            ):
                continue
            elif any(
                entry.name.endswith(suffix)
                for suffix in self._ignored_suffixes
            ):
                continue
            elif (
                self._ignore is not None
                and self._ignore(entry)
                # <format-break>
            ):
                continue

            if entry.is_dir():
                self._dirqueue.append(entry.name)

            break

        return self.make_entry(entry)

    def __next_dir__(self) -> bool:
        while self._dirqueue:
            scanpath = self._dirqueue.pop(0)

            self._stack.append(
                _StackEntry(
                    self.scanpath,
                    self._scaniter,
                    self._dirqueue,
                )
            )

            self.scanpath = os.path.join(self.scanpath, scanpath)
            self._scaniter = os.scandir(
                os.path.join(
                    self.basepath,
                    self.scanpath,
                )
            )
            self._dirqueue = list()

            self.on_enter(self.scanpath)

            return True

        if self._stack:

            self.on_exit(self.scanpath)

            _stackentry = self._stack.pop()

            self.scanpath = _stackentry.scanpath
            self._scaniter = _stackentry.scaniter
            self._dirqueue = _stackentry.dirqueue

            return False

        raise StopIteration()
