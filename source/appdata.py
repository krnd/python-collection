import os
import os.path
import sys
from typing import TYPE_CHECKING, Literal


# ################################ PACKAGE #####################################


__sname__ = "appdata"
__version__ = "2.1"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "__appdata_package_path__",
    "__appdata_user_path__",
    "__appdata_local_path__",
    "__appdata_temp_path__",
    "__appdata_server_path__",
    # fmt: on
)


# ################################ GLOBALS #####################################


if TYPE_CHECKING:

    __appdata_package_path__: str
    __appdata_user_path__: str
    __appdata_local_path__: str
    __appdata_temp_path__: str
    __appdata_server_path__: str

    package_path: str
    user_path: str
    local_path: str
    temp_path: str
    server_path: str


# ################################ FUNCTIONS ###################################


def init(
    folder: str,
    container: str | None = None,
    *,
    package: str | None = None,
    server: str | bool | None = None,
) -> None:

    subpath = os.path.normpath(
        os.path.join(container, folder) if container else folder
    )

    # ################## PACKAGE ###########################
    global __appdata_package_path__, package_path

    if getattr(sys, "frozen", False):
        basepath = os.path.dirname(sys.executable)
        assert basepath == getattr(sys, "_MEIPASS"), (
            "If the application is run as a bundle, the PyInstaller bootloader "
            "adds the attribute 'frozen' (True) inside the 'sys' module and "
            "writes the application path to the attribute '_MEIPASS'."
        )
    else:
        basepath = os.path.dirname(__file__)

    __appdata_package_path__ = package_path = os.path.abspath(
        os.path.join(basepath, package)
        if package is not None
        else basepath
        # <format-break>
    )

    # ################## USER ##############################
    global __appdata_user_path__, user_path

    basepath = os.getenv("APPDATA")
    if basepath is None:
        raise EnvironmentError(
            "environment variable %APPDATA% not found",
        )

    __appdata_user_path__ = user_path = os.path.abspath(
        os.path.join(basepath, subpath)
    )

    # ################## LOCAL #############################
    global __appdata_local_path__, local_path

    basepath = os.getenv("LOCALAPPDATA")
    if basepath is None:
        raise EnvironmentError(
            "environment variable %LOCALAPPDATA% not found",
        )

    __appdata_local_path__ = local_path = os.path.abspath(
        os.path.join(basepath, subpath)
    )

    # ################## TEMP ##############################
    global __appdata_temp_path__, temp_path

    basepath = os.getenv("TEMP")
    if basepath is None:
        raise EnvironmentError(
            "environment variable %TEMP% not found",
        )

    __appdata_temp_path__ = temp_path = os.path.abspath(
        os.path.join(basepath, subpath)
    )

    # ################## SERVER ############################
    global __appdata_server_path__, server_path

    basepath = (
        server
        if isinstance(server, str)
        else os.getenv("SERVERAPPDATA")
        # <format-break>
    )
    if basepath is None and server is True:
        raise EnvironmentError(
            "environment variable %SERVERAPPDATA% not found",
        )

    if basepath is not None:
        __appdata_server_path__ = server_path = os.path.abspath(
            os.path.join(basepath, subpath)
        )


def make(
    *entities: Literal[
        "package",
        "user",
        "local",
        "temp",
        "server",
    ],
) -> None:
    _globals = globals()
    for entity in entities:
        os.makedirs(
            _globals[f"{entity}_path"],
            exist_ok=True,
        )


def get(
    entity: Literal[
        "package",
        "user",
        "local",
        "temp",
        "server",
    ],
    /,
    *paths: str,
) -> str:
    _globals = globals()
    return os.path.join(
        _globals[f"{entity}_path"],
        *paths,
    )
