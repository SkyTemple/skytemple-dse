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
from enum import Enum
from typing import Union

from skytemple_dse.util import *

LEN_LFO = 16
LEN_SPLITS = 48


class SwdlLfoDest(Enum):
    NONE = 0
    PITCH = 1
    VOLUME = 2
    PAN = 3
    FILTER = 4


class SwdlWshape(Enum):
    NULL = 0
    SQUARE = 1
    TRIANGLE = 2
    SINUS = 3
    UNK4 = 4
    SAW = 5
    NOISE = 6
    RANDOM = 7


class SwdlLfoEntry(DseAutoString):
    def __init__(self, data: Union[bytes, memoryview]):
        self.unk34 = dse_read_uintle(data, 0x00)
        self.unk52 = dse_read_uintle(data, 0x01)
        self.dest = SwdlLfoDest(dse_read_uintle(data, 0x02))
        self.wshape = SwdlWshape(dse_read_uintle(data, 0x03))
        self.rate = dse_read_uintle(data, 0x04, 2)
        self.unk29 = dse_read_uintle(data, 0x06, 2)
        self.depth = dse_read_uintle(data, 0x08, 2)
        self.delay = dse_read_uintle(data, 0x0A, 2)
        self.unk32 = dse_read_uintle(data, 0x0C, 2)
        self.unk33 = dse_read_uintle(data, 0x0E, 2)


class SwdlSplitEntry(DseAutoString):
    def __init__(self, data: Union[bytes, memoryview]):
        assert data[0] == 0, "Data is not valid WDL PRG Split Entry"
        self.id = dse_read_uintle(data, 0x01)
        self.unk11 = dse_read_uintle(data, 0x02)
        self.unk25 = dse_read_uintle(data, 0x03)
        self.lowkey = dse_read_sintle(data, 0x04)
        self.hikey = dse_read_sintle(data, 0x05)
        assert self.lowkey == dse_read_sintle(data, 0x06), "Data is not valid WDL PRG Split Entry"  # Copy
        assert self.hikey == dse_read_sintle(data, 0x07), "Data is not valid WDL PRG Split Entry"  # Copy
        self.lolevel = dse_read_sintle(data, 0x08)
        self.hilevel = dse_read_sintle(data, 0x09)
        assert self.lolevel == dse_read_sintle(data, 0x0A), "Data is not valid WDL PRG Split Entry"  # Copy
        assert self.hilevel == dse_read_sintle(data, 0x0B), "Data is not valid WDL PRG Split Entry"  # Copy
        self.unk16 = dse_read_sintle(data, 0x0C, 4)
        self.unk17 = dse_read_sintle(data, 0x10, 2)
        self.sample_id = dse_read_uintle(data, 0x12, 2)
        self.ftune = dse_read_sintle(data, 0x14)
        self.ctune = dse_read_sintle(data, 0x15)
        self.rootkey = dse_read_sintle(data, 0x16)
        self.ktps = dse_read_sintle(data, 0x17)
        self.sample_volume = dse_read_sintle(data, 0x18)
        self.sample_pan = dse_read_sintle(data, 0x19)
        self.keygroup_id = dse_read_sintle(data, 0x1A)
        self.unk22 = dse_read_uintle(data, 0x1B, 2)
        self.unk23 = dse_read_uintle(data, 0x1C, 2)
        self.unk24 = dse_read_uintle(data, 0x1E, 2)

        self.envelope = dse_read_uintle(data, 0x20)
        self.envelope_multiplier = dse_read_uintle(data, 0x21)
        self.unk37 = dse_read_uintle(data, 0x22)
        self.unk38 = dse_read_uintle(data, 0x23)
        self.unk39 = dse_read_uintle(data, 0x24, 2)
        self.unk40 = dse_read_uintle(data, 0x26, 2)
        self.attack_volume = dse_read_sintle(data, 0x28)
        self.attack = dse_read_sintle(data, 0x29)
        self.decay = dse_read_sintle(data, 0x2A)
        self.sustain = dse_read_sintle(data, 0x2B)
        self.hold = dse_read_sintle(data, 0x2C)
        self.decay2 = dse_read_sintle(data, 0x2D)
        self.release = dse_read_sintle(data, 0x2E)
        self.unk53 = dse_read_sintle(data, 0x2F)


class SwdlProgramTable(DseAutoString):
    def __init__(self, data: Union[bytes, memoryview], _assertId: int):
        self.id = dse_read_uintle(data, 0x00, 2)
        assert self.id == _assertId, "Data is not valid WDL PRGI Program Entry"
        number_splits = dse_read_uintle(data, 0x02, 2)
        self.prg_volume = dse_read_sintle(data, 0x04)
        self.prg_pan = dse_read_sintle(data, 0x05)
        self.unk3 = dse_read_uintle(data, 0x06)
        self.that_f_byte = dse_read_uintle(data, 0x07)
        self.unk4 = dse_read_uintle(data, 0x08, 2)
        self.unk5 = dse_read_uintle(data, 0x0A)
        number_lfos = dse_read_uintle(data, 0x0B)
        # TODO: ????????? - 0x0C should be delimiter but it seems to just be any of these two?
        delimiter = (0x00, 0xAA)
        self.unk7 = dse_read_uintle(data, 0x0D)
        self.unk8 = dse_read_uintle(data, 0x0E)
        self.unk9 = dse_read_uintle(data, 0x0F)
        self.lfos = []
        self.splits = []

        end_lfos = 0x10 + number_lfos * LEN_LFO
        for off in range(0x10, end_lfos, LEN_LFO):
            self.lfos.append(SwdlLfoEntry(data[off:off + LEN_LFO]))
        assert any(data[end_lfos:end_lfos + 16] == bytes([d] * 16) for d in
                   delimiter), "Data is not valid WDL PRGI Program Entry"
        end_splits = end_lfos + 16 + number_splits * LEN_SPLITS
        for off in range(end_lfos + 16, end_splits, LEN_SPLITS):
            self.splits.append(SwdlSplitEntry(data[off:off + LEN_SPLITS]))


class SwdlPrgi:
    def __init__(self, data: Union[bytes, memoryview], number_slots: int):
        assert data[0x00:0x04] == b'prgi', "Data is not valid SWDL PRGI"
        assert data[0x004:0x06] == bytes(2), "Data is not valid SWDL PRGI"
        assert data[0x006:0x08] == bytes([0x15, 0x04]), "Data is not valid SWDL PRGI"
        assert data[0x008:0x0C] == bytes([0x10, 0x00, 0x00, 0x00]), "Data is not valid SWDL PRGI"
        len_chunk_data = dse_read_uintle(data, 0x0C, 4)

        self._length = 0x10 + len_chunk_data

        self.program_table = []
        for idx, seek in enumerate(range(0, number_slots * 2, 2)):
            pnt = dse_read_uintle(data, 0x10 + seek, 2)
            assert pnt < len_chunk_data, "Data is not valid SWDL PRGI"
            if pnt == 0:
                self.program_table.append(None)
            else:
                self.program_table.append(SwdlProgramTable(data[0x10 + pnt:], _assertId=idx))

    def __str__(self):
        chunks = ""
        for prog in self.program_table:
            chunks += f">> {prog}\n"
        return """PRGI
""" + chunks

    def get_initial_length(self):
        return self._length
