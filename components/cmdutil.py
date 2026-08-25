import sys
import types
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Final, Generator, Literal, overload

import cmd2
from cmd2.argparse_utils import Cmd2ArgumentParser
from cmd2.rich_utils import Cmd2ExceptionConsole
from rich.highlighter import ReprHighlighter
from rich.text import Text
from rich.traceback import Traceback


# ################################ COMPONENT ###################################


__component__ = "cmdutil"
__version__ = "2.0"
__description__ = ...

__requires__ = ("cmd2" "~=4.0",)


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
    "_eof",
    "run_pyscript",
    "run_script",
    "_relative_run_script",
    "set",
    "shell",
    "shortcuts",
)
"""Collection of all built-in commands."""


# ################################ FUNCTIONS ###################################


def setup(  # noqa: C901
    cmd: cmd2.Cmd,
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

    Every built-in command not covered by the given sets is removed.
    The commands `help`, `quit`, `_eof` and `set` are always kept,
    `ipy` is always removed.

    :param "base":
        Whether to exclude the advanced commands.
        (commands: alias, macro, shortcuts)
    :param "file":
        Whether to include all file manipulation commands.
        (commands: edit)
    :param "shell":
        Whether to include all shell-related commands.
        (commands: shell)
    :param "python":
        Whether to include all python-related commands.
        (commands: py, run_pyscript)
    :param "scripts":
        Whether to include all script-related commands.
        (commands: run_script, _relative_run_script, run_pyscript)
    :param history:
        Whether to include or remove the history command.

    """
    commands = {
        "help",
        "history",
        "quit",
        "_eof",
        "set",
    }

    if "base" not in sets:
        commands.add("alias")
        commands.add("macro")
        commands.add("shortcuts")
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
    cmd: cmd2.Cmd,
    /,
    *patches: Literal[
        "format_exception",
        # <format-break>
    ],
) -> None:
    """
    Applies a set of patches to a command interpreter.

    :param "format_exception":
        Slightly modifies the `format_exception` function to supress the
        superfluous warning text advertising the `set debug true` command.

    """
    if "format_exception" in patches:
        cmd.format_exception = types.MethodType(_cmd_format_exception, cmd)


def debug(
    cmd: cmd2.Cmd,
    /,
    value: bool = True,
) -> None:
    """
    Sets the debug configuration item on a command interpreter.

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
    cmd: cmd2.Cmd,
    /,
    name: Literal["debug"],
    value: bool,
) -> None: ...


@overload
def configure(
    cmd: cmd2.Cmd,
    /,
    name: Literal["prompt"],
    value: str,
) -> None: ...


def configure(
    cmd: cmd2.Cmd,
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
            f"The configuration item {name!r} does not exist or is not "
            "available to the command interpreter."
        )


# ###################### COMMANDS ##########################


def exists(cmd: cmd2.Cmd, /, command: str) -> bool:
    """
    Returns whether a command exists.

    :param cmd:
        Instance of the command interpreter.
    :param command:
        Name of the command to look for.

    """
    return callable(getattr(cmd, f"do_{command}", None))


def hide(cmd: cmd2.Cmd, /, command: str, *, exist: bool = True) -> None:
    """
    Hides a command.

    :param cmd:
        Instance of the command interpreter.
    :param command:
        Name of the command to hide.
    :param exist:
        Whether the command must exist.

    """
    if not exists(cmd, command):
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


def remove(cmd: cmd2.Cmd, /, command: str, *, exist: bool = True) -> None:
    """
    Removes a command.

    :param cmd:
        Instance of the command interpreter.
    :param command:
        Name of the command to remove.
    :param exist:
        Whether the command must exist.

    """
    if not exists(cmd, command):
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
    from cmd2.rich_utils import Cmd2HelpFormatter, HelpContent

    @contextmanager
    def argparser(
        prog: Optional[str] = None,
        usage: Optional[str] = None,
        description: Optional[HelpContent] = None,
        epilog: Optional[HelpContent] = None,
        parents: Sequence[argparse.ArgumentParser] = (),
        formatter_class: Type[Cmd2HelpFormatter] = Cmd2HelpFormatter,
        prefix_chars: str = "-",
        fromfile_prefix_chars: Optional[str] = None,
        argument_default: Optional[str] = None,
        conflict_handler: str = "error",
        add_help: bool = True,
        allow_abbrev: bool = True,
        exit_on_error: bool = True,
        suggest_on_error: bool = False,
        color: bool = False,
        *,
        completer_class: Optional[Type["ArgparseCompleter"]] = None,
    ) -> Generator[Cmd2ArgumentParser, None, None]:
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
        :param suggest_on_error: (cmd)
            Enables suggestions for mistyped argument choices and subparser
            names (default: ``False``)
        :param color: (cmd)
            Allow color output in help messages (default: ``False``)
        :param completer_class: (cmd2)
            optional parameter which specifies a subclass of ArgparseCompleter
            for custom completion behavior on this parser. If this is None, then
            it will be set to argparse_completer.DEFAULT_ARGPARSE_COMPLETER.

        """
        ...

else:

    @contextmanager
    def argparser(
        *args: Any,
        **kwargs: Any,
    ) -> Generator[Cmd2ArgumentParser, None, None]:
        yield Cmd2ArgumentParser(*args, **kwargs)


# ################################ INTERNALS ###################################


def _cmd_format_exception(
    self: cmd2.Cmd,
    exception: BaseException,
) -> str:
    # Slightly modified variant of 'cmd2.Cmd.format_exception'.
    # fmt: off

    console = Cmd2ExceptionConsole(file=sys.stderr)
    with console.capture() as capture:
        # Only print a traceback if we're in debug mode and one exists.
        if self.debug and sys.exc_info() != (None, None, None):
            traceback = Traceback(**self.traceback_kwargs)
            console.print(traceback, end="")

        else:
            # Print the exception in the same style Rich uses after a traceback.
            exception_str = str(exception)

            if exception_str:
                highlighter = ReprHighlighter()

                final_msg = Text.assemble(
                    (f"{type(exception).__name__}: ", "traceback.exc_type"),
                    highlighter(exception_str),
                )
            else:
                final_msg = Text(f"{type(exception).__name__}", style="traceback.exc_type")

            # If not in debug mode and the 'debug' setting is available,
            # inform the user how to enable full tracebacks.
            # if not self.debug and "debug" in self.settables:
            #     help_msg = Text.assemble(
            #         "\n\n",
            #         ("To enable full traceback, run the following command: ", Cmd2Style.WARNING),
            #         ("set debug true", Cmd2Style.COMMAND_LINE),
            #     )
            #     final_msg.append(help_msg)

            console.print(final_msg)

    return capture.get()
    # fmt: on
