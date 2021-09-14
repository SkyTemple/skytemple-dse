#  Copyright 2020-2021 Parakoopa and the SkyTemple Contributors
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
from datetime import datetime

from skytemple_dse.util import DseAutoString, dse_read_uintle, dse_write_uintle


class DseDate(DseAutoString):
    def __init__(self, year: int, month: int, day: int, hour: int, minute: int, second: int, centisecond: int):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.centisecond = centisecond

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            dse_read_uintle(data, 0x00, 2),
            dse_read_uintle(data, 0x02, 1),
            dse_read_uintle(data, 0x03, 1),
            dse_read_uintle(data, 0x04, 1),
            dse_read_uintle(data, 0x05, 1),
            dse_read_uintle(data, 0x06, 1),
            dse_read_uintle(data, 0x07, 1)
        )

    @classmethod
    def now(cls):
        date = datetime.now()
        return cls(
            date.year,
            date.month,
            date.day,
            date.hour,
            date.minute,
            date.second,
            0
        )

    def to_bytes(self):
        buffer = bytearray(8)
        dse_write_uintle(buffer, self.year, 0x00, 2),
        dse_write_uintle(buffer, self.month, 0x02, 1),
        dse_write_uintle(buffer, self.day, 0x03, 1),
        dse_write_uintle(buffer, self.hour, 0x04, 1),
        dse_write_uintle(buffer, self.minute, 0x05, 1),
        dse_write_uintle(buffer, self.second, 0x06, 1),
        dse_write_uintle(buffer, self.centisecond, 0x07, 1)
        return buffer
