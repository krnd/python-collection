import sys
import types
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Final, Generator, Literal, overload

import cmd2 as _cmd
import cmd2.ansi as _ansi


# ################################ PACKAGE #####################################


__sname__ = "cmdutil"
__version__ = "1.1"
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
"""Collection of all built-in commands."""


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
    """
    Setup a command interpreter.

    :param "base":
        Whether to exclude the advanced commands.
        (commands: alias, macro, shortcut)
    :param "file":
        Whether to include all file manipulation commands.
        (commands: edit)
    :param "shell":
        Whether to incldude all shell-related commands.
        (commands: shell)
    :param "python":
        Whether to include all python-related commands.
        (commands: py, run_pyscript)
    :param "scripts":
        Whether to include all script-related commands.
        (commands: run_script, run_pyscript)
    :param history:
        Whether to include or remove the history command.

    """
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
    """
    Applies a set of patches to a command interpreter.

    :param "pexcept":
        Slightly modifies the `pexcept` function to improve error reporting and supress the
        superfluous warning text.

    """
    if "pexcept" in patches:
        cmd.pexcept = types.MethodType(_cmd_pexcept, cmd)


def debug(
    cmd: _cmd.Cmd,
    /,
    value: bool = True,
) -> None:
    """
    Sets a the debug configuration item on a command interpreter.

    :param cmd:
        Instance of the command interpreter.
    :param value:
        New value of the debug configuration item.

    """
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
    name: Literal["debug"],
    value: None,
) -> None: ...


@overload
def configure(
    cmd: _cmd.Cmd,
    /,
    name: Literal["prompt"],
    value: str,
) -> None: ...


def configure(
    cmd: _cmd.Cmd,
    /,
    name: str,
    value: Any,
) -> None:
    """
    Sets a configuration item on a command interpreter.

    :param cmd:
        Instance of the command interpreter.
    :param name:
        Name of the configuration item to set.
    :param value:
        New value of the configuration item.

    """
    if not hasattr(cmd, "echo"):
        raise RuntimeError(
            f"The {'configure'!r} utility function must be called after the "
            "initialization of the command interpreter."
        )
    elif name == "debug":
        cmd.debug = bool(value)
    elif name == "prompt":
        cmd.prompt = str(value)
    else:
        raise ValueError(
            f"The configuration item {name!r} does not exists or is not "
            "available to the command interpreter."
        )


# ###################### COMMANDS ##########################


def exists(cmd: _cmd.Cmd, /, command: str) -> bool:
    """
    Returns whether a command exists.

    :param cmd:
        Instance of the command interpreter.
    :param command:
        Name of the command to look for.

    """
    return getattr(cmd, f"do_{command}", None) is not None


def hide(cmd: _cmd.Cmd, /, command: str, *, exist: bool = True) -> None:
    """
    Hides a command.

    :param cmd:
        Instance of the command interpreter.
    :param command:
        Name of the command to hide.
    :param exist:
        Whether the command must exist.

    """
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
    """
    Removes a command.

    :param cmd:
        Instance of the command interpreter.
    :param command:
        Name of the command to remove.
    :param exist:
        Whether the command must exist.

    """
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
        exit_on_error: bool = True,
        *,
        ap_completer_type: Optional[Type["ArgparseCompleter"]] = None,
    ) -> Generator[_cmd.Cmd2ArgumentParser, None, None]:
        """
        Returns a new argument parser as context object.

        :param prog: (cmd)
            The name of the program (default: ``os.path.basename(sys.argv[0])``)
        :param usage: (cmd)
            A usage message (default: auto-generated from arguments)
        :param description: (cmd)
            A description of what the program does
        :param epilog: (cmd)
            Text following the argument descriptions
        :param parents: (cmd)
            Parsers whose arguments should be copied into this one
        :param formatter_class: (cmd)
            HelpFormatter class for printing help messages
        :param prefix_chars: (cmd)
            Characters that prefix optional arguments
        :param fromfile_prefix_chars: (cmd)
            Characters that prefix files containing additional arguments
        :param argument_default: (cmd)
            The default value for all arguments
        :param conflict_handler: (cmd)
            String indicating how to handle conflicts
        :param add_help: (cmd)
            Add a -h/-help option
        :param allow_abbrev: (cmd)
            Allow long options to be abbreviated unambiguously
        :param exit_on_error: (cmd)
            Determines whether or not ArgumentParser exits with error info when an error occurs
        :param ap_completer_type: (cmd2)
            optional parameter which specifies a subclass of ArgparseCompleter for custom tab
            completion behavior on this parser. If this is None or not present, then cmd2 will use
            argparse_completer.DEFAULT_AP_COMPLETER when tab completing this parser's arguments

        """
        ...

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
    # Slightly modified variant of 'cmd2.Cmd.pexcept'.

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
