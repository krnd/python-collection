import os
import os.path
import sys
from typing import TYPE_CHECKING, Literal


# ################################ PACKAGE #####################################


__sname__ = "appdata"
__version__ = "2.0"
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
        os.path.join(container, folder)
        if container is not None
        else folder  # <format-break>
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
            "Environment variable %APPDATA% not found."
            # <format-break>
        )

    __appdata_user_path__ = user_path = os.path.abspath(
        os.path.join(basepath, subpath)
        # <format-break>
    )

    # ################## LOCAL #############################
    global __appdata_local_path__, local_path

    basepath = os.getenv("LOCALAPPDATA")
    if basepath is None:
        raise EnvironmentError(
            "Environment variable %LOCALAPPDATA% not found."
            # <format-break>
        )

    __appdata_local_path__ = local_path = os.path.abspath(
        os.path.join(basepath, subpath)
        # <format-break>
    )

    # ################## TEMP ##############################
    global __appdata_temp_path__, temp_path

    basepath = os.getenv("TEMP")
    if basepath is None:
        raise EnvironmentError(
            "Environment variable %TEMP% not found."
            # <format-break>
        )

    __appdata_temp_path__ = temp_path = os.path.abspath(
        os.path.join(basepath, subpath)
        # <format-break>
    )

    # ################## SERVER ############################
    global __appdata_server_path__, server_path

    basepath = (
        server  # <format-break>
        if isinstance(server, str)
        else os.getenv("SERVERAPPDATA")
    )
    if basepath is None and server is True:
        raise EnvironmentError(
            "Environment variable %SERVERAPPDATA% not found."
            # <format-break>
        )

    if basepath is not None:
        __appdata_server_path__ = server_path = os.path.abspath(
            os.path.join(basepath, subpath)
            # <format-break>
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

    for name in entities:
        path = _globals[f"__appdata_{name}_path__"]

        os.makedirs(path, exist_ok=True)
