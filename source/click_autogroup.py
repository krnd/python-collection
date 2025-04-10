from typing import Any, Callable, List

import click


# ################################ PACKAGE #####################################


__sname__ = "click_autogroup"
__version__ = "1.2"
__description__ = ...

__requires__ = ("click",)


__all__ = ("AutoGroup",)


# ################################ GROUP #######################################


class AutoGroup(click.Group):

    def __init__(
        self,
        *args: Any,
        default_command: str,
        version_option: Callable[[click.Command], click.Command] | None = None,
        **attrs: Any,
    ) -> None:
        super().__init__(*args, **attrs)

        self.default_command = default_command
        self.version_option = version_option

    def parse_args(
        self,
        ctx: click.Context,
        args: List[str],
    ) -> List[str]:
        if not args or args[0] not in self.commands:
            args.insert(0, self.default_command)
        return super().parse_args(ctx, args)

    def add_command(
        self,
        cmd: click.Command,
        name: str | None = None,
    ) -> None:
        if not self.commands and self.version_option:
            cmd = self.version_option(cmd)
        return super().add_command(cmd, name)
