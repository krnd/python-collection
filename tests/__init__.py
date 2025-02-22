import inspect
import os.path
import sys
from types import EllipsisType


sys.path.append("source")


__ASSETS_PATH__ = os.path.join(
    os.path.dirname(__file__),
    "assets",
)


def asset(
    path: str | EllipsisType,
    /,
    *paths: str,
) -> str:
    assetpath = os.path.join(*paths)

    if isinstance(path, str):
        caller = inspect.stack()[1]
        testee = (
            # <explicit>
            caller.frame.f_globals.get("__TESTEE__", None)
            # <filename>
            or str.removeprefix(
                os.path.splitext(
                    os.path.basename(caller.filename)
                    # <format-break>
                )[0],
                "test_",
            )
        )

        assetpath = os.path.join(testee, path, assetpath)

    return os.path.join(__ASSETS_PATH__, assetpath)
