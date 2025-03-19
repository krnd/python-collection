from typing import Final, Literal


# ################################ PACKAGE #####################################


__sname__ = "nbase"
__version__ = "1.0"
__description__ = ...

__requires__ = ()


__all__ = ("BaseN",)


# ################################ BASEN #######################################


class BaseN:

    base: Final
    alphabet: Final

    length: Final

    _reverse: Final

    def __init__(
        self,
        base: int,
        /,
        alphabet: str,
        *,
        length: int | None = None,
        align: Literal["left", "right"] | None = None,
    ) -> None:
        assert base > 0, (
            "base must be greater than zero"
            # <format-break>
        )
        self.base = base

        if len(alphabet) != base:
            raise ValueError("alphabet must have length of base")
        self.alphabet = alphabet

        assert (length is None) or (length > 0), (
            "length must be greater than zero"
            # <format-break>
        )
        self.length = length

        self._reverse = True if align == "left" else False

    def encode(
        self,
        value: int,
        /,
        length: int | None = None,
    ) -> str:
        base = self.base
        alphabet = self.alphabet

        _length = length or self.length

        text = ""
        if _length:
            for _ in range(_length):
                text = alphabet[value % base] + text
                value = value // base
        else:
            if value == 0:
                return alphabet[0]
            while value != 0:
                text = alphabet[value % base] + text
                value = value // base

        return (
            text[::-1]
            if self._reverse
            else text
            # <format-break>
        )

    def decode(
        self,
        text: str,
        /,
        length: int | None = None,
    ) -> int:
        base = self.base
        alphabet = self.alphabet

        _length = length or self.length

        value = 0
        for i, c in enumerate(reversed(text) if self._reverse else text):
            value = value * base + str.index(alphabet, c)

            if i == _length:
                break

        return value
