import os
import os.path
from dataclasses import dataclass
from types import TracebackType
from typing import TypeAlias


# ################################ COMPONENT ###################################


__component__ = "flock"
__version__ = "2.0"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "FileLock",
    "AlreadyLocked",
    # fmt: on
)


# ################################ EXCEPTIONS ##################################


class AlreadyLocked(Exception):
    def __init__(self, lock: "_LockFile") -> None:
        super().__init__(lock.file)


# ################################ TYPES #######################################


@dataclass(init=False, repr=True, eq=False, frozen=True, slots=True)
class _LockFile:

    file: str
    user: str

    def __init__(self, file: str, /) -> None:

        _filepath = os.path.abspath(file)
        _filedir = os.path.dirname(_filepath)
        if not os.path.exists(_filedir):
            raise FileNotFoundError(_filedir)
        else:
            file = _filepath

        _username = os.environ["USERNAME"]
        _userdomain = os.getenv("USERDOMAIN")
        user = (
            f"{_userdomain}/{_username}"
            if _userdomain is not None
            else _username
        )

        object.__setattr__(self, "file", file)
        object.__setattr__(self, "user", user)

    def lock(self) -> None:
        try:
            with open(self.file, "x", encoding="utf-8") as _file:
                _file.write(self.user)
        except FileExistsError as exc:
            raise AlreadyLocked(self) from exc

    def trylock(self) -> bool:
        try:
            self.lock()
        except AlreadyLocked:
            return False
        return True

    def unlock(self, *, safe: bool = False) -> None:
        try:
            with open(self.file, "r", encoding="utf-8") as _file:
                _user = _file.readline()
            if _user != self.user:
                raise PermissionError("lock not owned")
            os.remove(self.file)
        except FileNotFoundError as exc:
            if safe:
                return
            raise RuntimeError("lock not found") from exc

    def holder(self) -> str | None:
        try:
            with open(self.file, "r", encoding="utf-8") as _file:
                return _file.readline()
        except FileNotFoundError:
            return None

    def __enter__(self) -> None:
        self.lock()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        self.unlock()


FileLock: TypeAlias = _LockFile


# ################################ FUNCTIONS ###################################


def create(file: str, /, *, path: str | None = None) -> FileLock:
    file = os.path.join(path, file) if path else file
    return _LockFile(file)


def holder(file: str, /, *, path: str | None = None) -> str | None:
    file = os.path.join(path, file) if path else file
    try:
        with open(file, "r", encoding="utf-8") as _file:
            return _file.readline()
    except FileNotFoundError:
        return None


def reset(lock: FileLock | str, /) -> bool:
    file = lock if isinstance(lock, str) else lock.file
    try:
        os.remove(file)
    except FileNotFoundError:
        return False
    return True
