from typing import Any, List

import click


# ################################ PACKAGE #####################################


__sname__ = "click_autogroup"
__version__ = "1.3"
__description__ = ...

__requires__ = ("click",)


__all__ = ("AutoGroup",)


# ################################ GROUP #######################################


class AutoGroup(click.Group):

    def __init__(
        self,
        *args: Any,
        default_command: str,
        **attrs: Any,
    ) -> None:
        super().__init__(*args, **attrs)

        self.default_command = default_command

    def parse_args(
        self,
        ctx: click.Context,
        args: List[str],
    ) -> List[str]:
        if not args or (
            (args[0] not in self.commands)
            and not (args[0] == "--version")
            # <format-break>
        ):
            args.insert(0, self.default_command)
        return super().parse_args(ctx, args)
