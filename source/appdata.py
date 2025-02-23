import os.path
import sys
from typing import TYPE_CHECKING


# ################################ PACKAGE #####################################


__sname__ = "appdata"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = (
    # fmt: off
    "__PACKAGE_APPDATA__",
    "__USER_APPDATA__",
    "__LOCAL_APPDATA__",
    "__TEMP_APPDATA__",
    "__SERVER_APPDATA__",
    # fmt: on
)


# ################################ GLOBALS #####################################


if TYPE_CHECKING:

    __PACKAGE_APPDATA__: str
    __USER_APPDATA__: str
    __LOCAL_APPDATA__: str
    __TEMP_APPDATA__: str
    __SERVER_APPDATA__: str


# ################################ FUNCTIONS ###################################


def init(
    folder: str,
    container: str | None = None,
    *,
    package: str | None = None,
    server: str | None = None,
) -> None:
    subpath = os.path.normpath(
        os.path.join(container, folder)
        if container is not None
        else folder  # <format-break>
    )

    # ################## PACKAGE ###########################
    global __PACKAGE_APPDATA__

    if getattr(sys, "frozen", False):
        basepath = os.path.dirname(sys.executable)
        assert basepath == getattr(sys, "_MEIPASS"), (
            "If the application is run as a bundle, the PyInstaller bootloader "
            "adds the attribute 'frozen' (True) inside the 'sys' module and "
            "writes the application path to the attribute '_MEIPASS'."
        )
    else:
        basepath = os.path.dirname(__file__)

    __PACKAGE_APPDATA__ = os.path.abspath(
        os.path.join(basepath, package)
        if package is not None
        else basepath
        # <format-break>
    )

    # ################## USER ##############################
    global __USER_APPDATA__

    basepath = os.getenv("APPDATA")
    if basepath is None:
        raise EnvironmentError(
            "Environment variable %APPDATA% not found."
            # <format-newline>
        )

    __USER_APPDATA__ = os.path.abspath(
        os.path.join(basepath, subpath)
        # <format-break>
    )

    # ################## LOCAL #############################
    global __LOCAL_APPDATA__

    basepath = os.getenv("LOCALAPPDATA")
    if basepath is None:
        raise EnvironmentError(
            "Environment variable %LOCALAPPDATA% not found."
            # <format-newline>
        )

    __LOCAL_APPDATA__ = os.path.abspath(
        os.path.join(basepath, subpath)
        # <format-break>
    )

    # ################## TEMP ##############################
    global __TEMP_APPDATA__

    basepath = os.getenv("TEMP")
    if basepath is None:
        raise EnvironmentError(
            "Environment variable %TEMP% not found."
            # <format-newline>
        )

    __TEMP_APPDATA__ = os.path.abspath(
        os.path.join(basepath, subpath)
        # <format-break>
    )

    # ################## SERVER ############################
    global __SERVER_APPDATA__

    basepath = server or os.getenv("SERVERAPPDATA")
    if basepath is not None:

        __SERVER_APPDATA__ = os.path.abspath(
            os.path.join(basepath, subpath)
            # <format-break>
        )
