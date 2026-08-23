from typing import (
    Callable,
    Iterable,
    Literal,
    Mapping,
    Sequence,
    TypeAlias,
    TypeVar,
    overload,
)

from serial.tools.list_ports import comports as _pyserial_list_ports
from serial.tools.list_ports_common import ListPortInfo as PortInfo


# ################################ COMPONENT ###################################


__component__ = "comport"
__version__ = "3.0"
__description__ = ...

__requires__ = ("pyserial",)


__all__ = ()


# ################################ TYPING ######################################


T = TypeVar("T")


# ################################ FILTERS #####################################

_FilterCollection: TypeAlias = Mapping[str, Sequence[T]]
"""Collection of data mapped by a named filter."""


_FILTERS_USB: _FilterCollection[
    # (VID, PID)
    tuple[int, int]
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
    "usb:ftdi": (
        (0x0403, 0x6001),
        (0x0403, 0x6010),
        (0x0403, 0x6011),
        (0x0403, 0x6014),
    ),
    # Prolific (0x067B)
    #   PL2303                      0x23A3
    #   PL2303GD                    0x2323
    "usb:prolific": (
        (0x067B, 0x23A3),
        (0x067B, 0x2323),
    ),
}


# ################################ FUNCTIONS ###################################


def list() -> Sequence[PortInfo]:
    """Returns a collection of all available serial ports."""
    return _pyserial_list_ports()


def names() -> Sequence[str]:
    """Returns a collection of all available serial port names."""
    return [port.name for port in _pyserial_list_ports()]


def has(name: str, /) -> bool:
    """Checks whether a specific serial port is available."""
    for port in _pyserial_list_ports():
        if port.name == name:
            return True
    return False


def get(name: str, /) -> PortInfo:
    """Returns the info for a specific serial port."""
    for port in _pyserial_list_ports():
        if port.name == name:
            return port
    raise KeyError(f"serial port {name!r} not found")


@overload
def find() -> PortInfo | None:
    """Returns the first available serial port."""
    ...


@overload
def find(
    filter: Literal["usb"],
    /,
    vpid: tuple[int, int],
) -> PortInfo | None:
    """Returns a serial port matching a specific USB VID and PID."""
    ...


@overload
def find(
    filter: Literal["usb"],
    /,
    *,
    vid: int,
    pid: Iterable[int] | int,
) -> PortInfo | None:
    """Returns a serial port matching a specific USB VID and PID."""
    ...


@overload
def find(filter: str, /) -> PortInfo | None:
    """Returns a serial port matching a predefined named filter."""
    ...


def find(
    filter: str | None = None,
    /,
    *args: ...,
    **kwargs: ...,
) -> PortInfo | None:
    _filter: Callable[[PortInfo], bool]

    if not filter:
        _filter = lambda port: True

    elif filter == "usb":
        if args:
            vid, pid = args[0]
        else:
            vid, pid = kwargs["vid"], kwargs["pid"]
            pid = (pid,) if isinstance(pid, int) else pid
        _filter = lambda port: any(
            (port.vid == vid and port.pid == _pid)
            for _pid in pid  # <format-break>
        )

    elif filter in _FILTERS_USB:
        _filter = lambda port: any(
            (port.vid == _vid and port.pid == _pid)
            for _vid, _pid in _FILTERS_USB[filter]
        )

    else:
        raise KeyError(f"unknown filter {filter!r}")

    return next(
        (
            port  # <format-break>
            for port in _pyserial_list_ports()
            if _filter(port)
        ),
        None,
    )
