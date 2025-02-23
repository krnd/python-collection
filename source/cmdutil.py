import sys
import types
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Final, Generator, Literal, overload

import cmd2 as _cmd
import cmd2.ansi as _ansi


# ################################ PACKAGE #####################################


__sname__ = "cmdutil"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = ()


# ################################ CONSTANTS ###################################


ALL_COMMANDS: Final = (
    "alias",
    "edit",
    "help",
    "history",
    "ipy",
    "macro",
    "py",
    "quit",
    "run_pyscript",
    "run_script",
    "_relative_run_script",
    "set",
    "shell",
    "shortcut",
)


# ################################ FUNCTIONS ###################################


def setup(  # noqa: C901
    cmd: _cmd.Cmd,
    /,
    *sets: Literal[
        "base",
        "file",
        "shell",
        "python",
        "scripts",
    ],
    history: bool | None = None,
) -> None:
    commands = {
        "help",
        "history",
        "quit",
        "set",
    }

    if "base" not in sets:
        commands.add("alias")
        commands.add("macro")
        commands.add("shortcut")
    if "file" in sets:
        commands.add("edit")
    if "shell" in sets:
        commands.add("shell")
    if "python" in sets:
        commands.add("py")
    if "scripts" in sets:
        commands.add("run_script")
        commands.add("_relative_run_script")
    if "scripts" in sets and "python" in sets:
        commands.add("run_pyscript")

    if history is False:
        commands.remove("history")
    elif history is True:
        commands.add("history")

    has_hidden_commands = hasattr(cmd, "hidden_commands")
    for _command in ALL_COMMANDS:
        if _command in commands:
            continue
        if (
            has_hidden_commands  # <format-break>
            and _command in cmd.hidden_commands
        ):
            cmd.hidden_commands.remove(_command)
        setattr(cmd, f"do_{_command}", None)


def patch(
    cmd: _cmd.Cmd,
    /,
    *patches: Literal[
        "pexcept",
        # <format-break>
    ],
) -> None:
    if "pexcept" in patches:
        cmd.pexcept = types.MethodType(_cmd_pexcept, cmd)


def debug(
    cmd: _cmd.Cmd,
    /,
    value: bool = True,
) -> None:
    if not hasattr(cmd, "echo"):
        raise RuntimeError(
            f"The {'debug'!r} utility function must be called after the "
            "initialization of the command interpreter."
        )
    cmd.debug = value


# ###################### CONFIGURE #########################


@overload
def configure(
    cmd: _cmd.Cmd,
    /,
    name: Literal["prompt"],
    value: str,
) -> None: ...


@overload
def configure(
    cmd: _cmd.Cmd,
    /,
    name: Literal[""],
    value: None,
) -> None: ...


def configure(
    cmd: _cmd.Cmd,
    /,
    name: str,
    value: Any,
) -> None:
    if not hasattr(cmd, "echo"):
        raise RuntimeError(
            f"The {'configure'!r} utility function must be called after the "
            "initialization of the command interpreter."
        )
    elif name == "prompt":
        cmd.prompt = value
    else:
        raise ValueError(
            f"The configuration item {name!r} does not exists or is not "
            "available to the command interpreter."
        )


# ###################### COMMANDS ##########################


def exists(cmd: _cmd.Cmd, /, command: str) -> bool:
    return getattr(cmd, f"do_{command}", None) is not None


def hide(cmd: _cmd.Cmd, /, command: str, *, exist: bool = True) -> None:
    if getattr(cmd, f"do_{command}", None) is None:
        if exist:
            raise AttributeError(
                f"Command {command!r} not found.",
                name=command,
                obj=cmd,
            )
        return
    if (
        hasattr(cmd, "hidden_commands")
        and command not in cmd.hidden_commands
        # <format-break>
    ):
        cmd.hidden_commands.append(command)


def remove(cmd: _cmd.Cmd, /, command: str, *, exist: bool = True) -> None:
    if getattr(cmd, f"do_{command}", None) is None:
        if exist:
            raise AttributeError(
                f"Command {command!r} not found.",
                name=command,
                obj=cmd,
            )
        return
    if (
        hasattr(cmd, "hidden_commands")
        and command in cmd.hidden_commands
        # <format-break>
    ):
        cmd.hidden_commands.remove(command)
    setattr(cmd, f"do_{command}", None)


# ###################### ARGPARSER #########################
if TYPE_CHECKING:

    import argparse
    from typing import Optional, Sequence, Type

    from cmd2.argparse_completer import ArgparseCompleter
    from cmd2.argparse_custom import Cmd2HelpFormatter

    @contextmanager
    def argparser(
        prog: Optional[str] = None,
        usage: Optional[str] = None,
        description: Optional[str] = None,
        epilog: Optional[str] = None,
        parents: Sequence[argparse.ArgumentParser] = (),
        formatter_class: Type[argparse.HelpFormatter] = Cmd2HelpFormatter,
        prefix_chars: str = "-",
        fromfile_prefix_chars: Optional[str] = None,
        argument_default: Optional[str] = None,
        conflict_handler: str = "error",
        add_help: bool = True,
        allow_abbrev: bool = True,
        *,
        ap_completer_type: Optional[Type["ArgparseCompleter"]] = None,
    ) -> Generator[_cmd.Cmd2ArgumentParser, None, None]: ...

else:

    @contextmanager
    def argparser(
        *args: Any,
        **kwargs: Any,
    ) -> Generator[_cmd.Cmd2ArgumentParser, None, None]:
        yield _cmd.Cmd2ArgumentParser(*args, **kwargs)


# ################################ INTERNALS ###################################


def _cmd_pexcept(
    self: _cmd.Cmd,
    msg: Any,
    *,
    end: str = "\n",
    apply_style: bool = True,
) -> None:
    if self.debug and sys.exc_info() != (None, None, None):
        import traceback

        traceback.print_exc()

    if isinstance(msg, Exception):
        final_msg = f"{type(msg).__name__}: {msg}"
    else:
        final_msg = str(msg)

    if apply_style:
        final_msg = _ansi.style_error(final_msg)

    if """ always suppress warning """:
        pass
    elif not self.debug and "debug" in self.settables:
        warning = "\nTo enable full traceback, run the following command: 'set debug true'"  # noqa: B950
        final_msg += _ansi.style_warning(warning)

    self.perror(final_msg, end=end, apply_style=False)
