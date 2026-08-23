import os
import os.path
import site
import sys
from typing import TYPE_CHECKING, Literal, cast


# ################################ COMPONENT ###################################


__component__ = "appdata"
__version__ = "3.0"
__description__ = ...

__requires__ = ()


__all__ = ()


# ################################ GLOBALS #####################################


if TYPE_CHECKING:

    package_path: str
    """Path to the package data."""
    application_path: str
    """Path to the application data."""
    user_path: str
    """Path to the roaming user data."""
    local_path: str
    """Path to the local user data."""
    temp_path: str
    """Path to the temporary data."""
    server_path: str
    """Path to the shared server data."""


_is_initialized = False
"""Whether the data locations have been initialized."""


# ################################ FUNCTIONS ###################################


def init(  # noqa: C901
    root: str,
    /,
    folder: str,
    container: str | None = None,
    *,
    package: str | None = None,
    application: str | None = None,
    server: str | bool | None = None,
) -> None:
    """
    Initializes the data locations.

    :param root:
        Root path of the package. <br/>
        (Just use `__file__` from the top-level `__init__.py`.)
    :param folder:
        Name of the subdirectory for all data locations.
        (Does not apply to package and application data locations.)
    :param container:
        Subpath for all data locations to nest the folder within.
        (Does not apply to package and application data locations.)
    :param package:
        Subpath of the data location within the package directory.
    :param application:
        Subpath of the data location within the application directory.
    :param server:
        Whether the server path is required (bool)
        or the path of the server itself (str).
    """
    global _is_initialized

    if _is_pyinstaller := getattr(sys, "frozen", False):
        # If the application is run as a bundle, the PyInstaller bootloader adds
        # the attribute 'frozen' (True) inside the 'sys' module and writes the
        # application path to the attribute '_MEIPASS'.
        rootpath = cast(str, ...)
    elif not os.path.exists(root):
        raise FileNotFoundError("application path does not exist")
    elif os.path.isfile(root):
        rootpath = os.path.dirname(root)
    else:
        rootpath = root

    subpath = os.path.normpath(
        os.path.join(container, folder)  #
        if container is not None  #
        else folder  #
    )

    # ########### PACKAGE ##############
    global package_path

    if _is_pyinstaller:
        basepath = getattr(sys, "_MEIPASS")
    else:
        basepath = rootpath

    package_path = os.path.abspath(
        os.path.join(basepath, package)  #
        if package is not None  #
        else basepath  #
    )

    # ########### APPLICATION ##########
    global application_path

    if _is_pyinstaller:
        basepath = os.path.dirname(sys.executable)
    elif _is_installed(rootpath):
        basepath = os.getcwd()
    else:
        basepath = rootpath

    application_path = os.path.abspath(
        os.path.join(basepath, application)
        if application is not None
        else basepath
    )

    # ########### USER #################
    global user_path

    basepath = os.getenv("APPDATA")
    if basepath is None:
        raise EnvironmentError("environment variable %APPDATA% not found")

    user_path = os.path.abspath(os.path.join(basepath, subpath))

    # ########### LOCAL ################
    global local_path

    basepath = os.getenv("LOCALAPPDATA")
    if basepath is None:
        raise EnvironmentError("environment variable %LOCALAPPDATA% not found")

    local_path = os.path.abspath(os.path.join(basepath, subpath))

    # ########### TEMP #################
    global temp_path

    basepath = os.getenv("TEMP")
    if basepath is None:
        raise EnvironmentError("environment variable %TEMP% not found")

    temp_path = os.path.abspath(os.path.join(basepath, subpath))

    # ########### SERVER ###############
    global server_path

    basepath = (
        server  #
        if isinstance(server, str)  #
        else os.getenv("SERVERAPPDATA")  #
    )
    if server is True and basepath is None:
        raise EnvironmentError("environment variable %SERVERAPPDATA% not found")

    if basepath is not None:
        server_path = os.path.abspath(os.path.join(basepath, subpath))

    _is_initialized = True


def make(
    *items: Literal[
        "package",
        "application",
        "user",
        "local",
        "temp",
        "server",
    ],
) -> None:
    """
    Creates the directories for the specified data locations.
    """
    if not _is_initialized:
        raise RuntimeError("appdata not initialized")
    _globals = globals()
    for item in items:
        os.makedirs(_globals[f"{item}_path"], exist_ok=True)


def get(
    item: Literal[
        "package",
        "application",
        "user",
        "local",
        "temp",
        "server",
    ],
    /,
    *paths: str,
) -> str:
    """
    Returns the path for the specified data location.
    """
    if not _is_initialized:
        raise RuntimeError("appdata not initialized")
    _globals = globals()
    return os.path.join(_globals[f"{item}_path"], *paths)


def _is_installed(rootpath: str, /) -> bool:
    """Returns wether the package is installed."""
    rootpath = os.path.abspath(rootpath)

    for site_path in site.getsitepackages():
        site_path = os.path.abspath(site_path)
        if os.path.commonpath((rootpath, site_path)) == site_path:
            return True

    site_path = site.getusersitepackages()
    if site_path:
        site_path = os.path.abspath(site_path)
        if os.path.commonpath((rootpath, site_path)) == site_path:
            return True

    return False
