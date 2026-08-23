from typing import (
    Annotated,
    Callable,
    Final,
    Literal,
    Mapping,
    Sequence,
    Tuple,
    TypeAlias,
    TypeVar,
    overload,
)

from serial.tools.list_ports import comports as pyserial_list_ports
from serial.tools.list_ports_common import ListPortInfo as PortInfo


# ################################ PACKAGE #####################################


__component__ = "comport"
__version__ = "2.0"
__description__ = ...

__requires__ = ("pyserial",)


__all__ = ()


# ################################ TYPING ######################################


T = TypeVar("T")


_FilterCollection: TypeAlias = Final[Mapping[str, Sequence[T]]]


# ################################ CONSTANTS ###################################


FILTERS_USB: _FilterCollection[
    Tuple[
        Annotated[int, "VID"],
        Annotated[int, "PID"],
    ]
] = {
    # FTDI (0x0403)
    #   FT232BM/L/Q, FT245BM/L/Q    0x6001
    #   FT232RL/Q, FT245RL/Q        0x6001
    #   FT2232C/D/L                 0x6010
    #   FT2232HL/Q                  0x6010
    #   FT4232HL/Q                  0x6011
    #   FT232HL/Q                   0x6014
    #   VNC1L with VDPS Firmware    0x6001
    #   VNC2 with FT232Slave        0x6001
    "ftdi": (
        (0x0403, 0x6001),
        (0x0403, 0x6010),
        (0x0403, 0x6011),
        (0x0403, 0x6014),
    ),
    # Prolific (0x067B)
    #   PL2303                      0x23A3
    #   PL2303GD                    0x2323
    "prolific": (
        (0x067B, 0x23A3),
        (0x067B, 0x2323),
    ),
    "pl2303": (
        (0x067B, 0x23A3),
        # The PL2303GD is not included here.
    ),
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


@overload
def find() -> PortInfo | None: ...


@overload
def find(
    filter: Literal["usb"],
    /,
    *,
    pid: int,
    vid: int | None = None,
) -> PortInfo | None: ...


@overload
def find(filter: str, /) -> PortInfo | None: ...


def find(
    filter: str | None = None,
    /,
    *,
    pid: int | None = None,
    vid: int | None = None,
) -> PortInfo | None:
    _filter: Callable[[PortInfo], bool]

    if not filter:
        _filter = lambda port: True
    elif filter == "usb":
        _filter = lambda port: (
            (port.vid == vid)
            if pid is None
            else (port.vid == vid and port.pid == pid)
        )
    elif filter in FILTERS_USB:
        _filter = lambda port: any(
            (port.vid == _vid and port.pid == _pid)
            for _vid, _pid in FILTERS_USB[filter]
        )
    else:
        raise KeyError(f"unknown filter {filter!r}")

    return next(
        (
            port  # <format-break>
            for port in pyserial_list_ports()
            if _filter(port)
        ),
        None,
    )
