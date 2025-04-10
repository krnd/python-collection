from typing import (
    Callable,
    Final,
    NamedTuple,
    Sequence,
)

from serial.tools.list_ports import comports as pyserial_list_ports
from serial.tools.list_ports_common import ListPortInfo as PortInfo


# ################################ PACKAGE #####################################


__sname__ = "comport"
__version__ = "1.0"
__description__ = ...

__requires__ = ("pyserial",)


__all__ = ()


# ################################ TYPES #######################################


class _UsbFilter(NamedTuple):
    vid: int
    pid: int


# ################################ CONSTANTS ###################################


FILTERS_USB: Final = {
    "ftdi": {
        "": _UsbFilter(0x0403, 0x6001),
        "dual": _UsbFilter(0x0403, 0x6010),
        "quad": _UsbFilter(0x0403, 0x6011),
        "new": _UsbFilter(0x0403, 0x6014),
    },
}


# ################################ FUNCTIONS ###################################


def list() -> Sequence[PortInfo]:
    return pyserial_list_ports()


def names() -> Sequence[str]:
    return [port.name for port in pyserial_list_ports()]


def has(name: str, /) -> bool:
    for port in pyserial_list_ports():
        if port.name == name:
            return True
    return False


def get(name: str, /) -> PortInfo:
    for port in pyserial_list_ports():
        if port.name == name:
            return port
    raise KeyError(f"serial port {name!r} not found")


def find(filter: str | None = None, /) -> PortInfo | None:
    filter_callable: Callable[[PortInfo], bool]

    if filter:
        basefilter, _, subfilter = filter.partition(".")
    else:
        basefilter, subfilter = ("", "")

    if not basefilter:
        filter_callable = lambda port: True

    elif basefilter in FILTERS_USB:
        specs = FILTERS_USB[basefilter]

        try:
            specs = (
                (specs[subfilter],)
                if subfilter
                else specs.values()
                # <format-break>
            )
        except KeyError as exc:
            raise KeyError(f"unknown sub filter {filter!r}") from exc

        filter_callable = lambda port: any(
            port.pid == spec.pid and port.vid == spec.pid
            for spec in specs  # <format-break>
        )

    else:
        raise KeyError(f"unknown base filter {filter!r}")

    return next(
        (
            port  # <format-break>
            for port in pyserial_list_ports()
            if filter_callable(port)
        ),
        None,
    )
