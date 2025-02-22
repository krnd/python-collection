import os
import os.path
from types import TracebackType
from typing import TYPE_CHECKING, NamedTuple, Self, Type


# ################################ PACKAGE #####################################


__sname__ = "flock"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "LockFile",
    "AlreadyLocked",
    # fmt: on
)


# ################################ EXCEPTIONS ##################################


class AlreadyLocked(Exception):
    def __init__(self, exc: FileExistsError) -> None:
        super().__init__(str(exc.filename))
        self.exc = exc


class LockFileOperationError(Exception):
    def __init__(self, exc: FileNotFoundError) -> None:
        super().__init__(str(exc.filename))
        self.exc = exc


# ################################ LOCKFILE ####################################


class LockFile(NamedTuple):
    # ################## FIELDS ############################

    file: str
    user: str

    # ################## STRUCTORS #########################

    def __new__(cls, file: str, /) -> Self:

        _filepath = os.path.abspath(file)
        _filedir = os.path.dirname(_filepath)
        if not os.path.exists(_filedir):
            raise FileNotFoundError(_filedir)
        else:
            _file = _filepath

        _username = os.environ["USERNAME"]
        _userdomain = os.getenv("USERDOMAIN")
        _user = (
            f"{_userdomain}/{_username}"
            if _userdomain is not None
            else _username
        )

        return super().__new__(cls, (_file, _user))

    if TYPE_CHECKING:

        def __init__(self, file: str, /) -> None: ...

    # ################## METHODS ###########################

    @staticmethod
    def remove(file: str, /) -> bool:
        try:
            os.remove(file)
        except FileNotFoundError:
            return False
        return True

    def lock(self) -> None:
        try:
            with open(self.file, "x", encoding="utf-8") as file:
                file.write(self.user)
        except FileExistsError as exc:
            raise AlreadyLocked(exc) from exc

    def trylock(self) -> bool:
        try:
            self.lock()
        except AlreadyLocked:
            return False
        return True

    def unlock(self, *, weak: bool = False) -> None:
        try:
            os.remove(self.file)
        except FileNotFoundError as exc:
            if weak:
                return
            raise LockFileOperationError(exc) from exc

    # ################## CONTEXT ###########################

    def __enter__(self) -> None:
        self.lock()

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        self.unlock()


# ################################ FUNCTIONS ###################################


def file(
    path: str,
    /,
    *,
    basepath: str | None = None,
) -> LockFile:
    return LockFile(
        os.path.join(basepath, path)
        if basepath is not None
        else path  # <format-break>
    )
