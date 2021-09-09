"""Copy of some utility functions from skytemple-file. Copied here for dependency reasons."""
#  Copyright 2020-2021 Capypara and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.


def dse_read_bytes(data: bytes, start=0, length=1) -> bytes:
    """
    Read a number of bytes (default 1) from a bytes-like object
    Recommended usage with memoryview for performance!
    """
    return data[start:(start + length)]


def dse_read_uintle(data: bytes, start=0, length=1) -> int:
    """
    Return an unsiged integer in little endian from the bytes-like object at the given position.
    Recommended usage with memoryview for performance!
    """
    return int.from_bytes(data[start:(start + length)], byteorder='little', signed=False)


def dse_read_sintle(data: bytes, start=0, length=1) -> int:
    """
    Return an signed integer in little endian from the bytes-like object at the given position.
    Recommended usage with memoryview for performance!
    """
    return int.from_bytes(data[start:(start + length)], byteorder='little', signed=True)


def dse_read_uintbe(data: bytes, start=0, length=1) -> int:
    """
    Return an unsiged integer in big endian from the bytes-like object at the given position.
    Recommended usage with memoryview for performance!
    """
    return int.from_bytes(data[start:(start + length)], byteorder='big', signed=False)


def dse_read_sintbe(data: bytes, start=0, length=1) -> int:
    """
    Return an signed integer in big endian from the bytes-like object at the given position.
    Recommended usage with memoryview for performance!
    """
    return int.from_bytes(data[start:(start + length)], byteorder='big', signed=True)


def dse_write_uintle(data: bytes, to_write: int, start=0, length=1):
    """
    Write an unsiged integer in little endian to the bytes-like mutable object at the given position.
    """
    data[start:start + length] = to_write.to_bytes(length, byteorder='little', signed=False)


def dse_write_sintle(data: bytes, to_write: int, start=0, length=1):
    """
    Write an signed integer in little endian to the bytes-like mutable object at the given position.
    """
    data[start:start + length] = to_write.to_bytes(length, byteorder='little', signed=True)


def dse_write_uintbe(data: bytes, to_write: int, start=0, length=1):
    """
    Write an unsiged integer in big endian to the bytes-like mutable object at the given position.
    """
    data[start:start + length] = to_write.to_bytes(length, byteorder='big', signed=False)


def dse_write_sintbe(data: bytes, to_write: int, start=0, length=1):
    """
    Write an signed integer in big endian to the bytes-like mutable object at the given position.
    """
    data[start:start + length] = to_write.to_bytes(length, byteorder='big', signed=True)


class DseAutoString:
    """Utility base class, that implements convenient __str__ and __repr__ based on object attributes."""

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.__class__.__name__}<{str({k: v for k, v in self.__dict__.items() if v is not None and not k[0] == '_'})}>"
