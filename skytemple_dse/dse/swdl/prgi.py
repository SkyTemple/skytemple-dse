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
from typing import Union, List, Optional

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
    def __init__(self, data: Optional[Union[bytes, memoryview]]):
        if data is None:
            return
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

    @classmethod
    def new(cls, unk34, unk52, dest, wshape, rate, unk29, depth, delay, unk32, unk33):
        n = SwdlLfoEntry(None)
        vars(n).update({
            'unk34': unk34,
            'unk52': unk52,
            'dest': dest,
            'wshape': wshape,
            'rate': rate,
            'unk29': unk29,
            'depth': depth,
            'delay': delay,
            'unk32': unk32,
            'unk33': unk33,
        })
        return n

    def to_bytes(self):
        data = bytearray(16)
        dse_write_uintle(data, self.unk34, 0x00)
        dse_write_uintle(data, self.unk52, 0x01)
        dse_write_sintle(data, self.dest.value, 0x02)
        dse_write_sintle(data, self.wshape.value, 0x03)
        dse_write_uintle(data, self.rate, 0x04, 2)
        dse_write_uintle(data, self.unk29, 0x06, 2)
        dse_write_uintle(data, self.depth, 0x08, 2)
        dse_write_uintle(data, self.delay, 0x0A, 2)
        dse_write_uintle(data, self.unk32, 0x0C, 2)
        dse_write_uintle(data, self.unk33, 0x0E, 2)
        return data

    def __eq__(self, other):
        if not isinstance(other, SwdlLfoEntry):
            return False
        return vars(self) == vars(other)


class SwdlSplitEntry(DseAutoString):
    def __init__(self, data: Optional[Union[bytes, memoryview]]):
        if data is None:
            return
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

    @classmethod
    def new(cls, id, unk11, unk25, lowkey, hikey, lolevel, hilevel, unk16, unk17, sample_id, ftune, ctune, rootkey,
            ktps, sample_volume, sample_pan, keygroup_id, unk22, unk23, unk24, envelope, envelope_multiplier, unk37,
            unk38, unk39, unk40, attack_volume, attack, decay, sustain, hold, decay2, release, unk53):
        n = SwdlSplitEntry(None)
        vars(n).update({
            'id': id,
            'unk11': unk11,
            'unk25': unk25,
            'lowkey': lowkey,
            'hikey': hikey,
            'lolevel': lolevel,
            'hilevel': hilevel,
            'unk16': unk16,
            'unk17': unk17,
            'sample_id': sample_id,
            'ftune': ftune,
            'ctune': ctune,
            'rootkey': rootkey,
            'ktps': ktps,
            'sample_volume': sample_volume,
            'sample_pan': sample_pan,
            'keygroup_id': keygroup_id,
            'unk22': unk22,
            'unk23': unk23,
            'unk24': unk24,
            'envelope': envelope,
            'envelope_multiplier': envelope_multiplier,
            'unk37': unk37,
            'unk38': unk38,
            'unk39': unk39,
            'unk40': unk40,
            'attack_volume': attack_volume,
            'attack': attack,
            'decay': decay,
            'sustain': sustain,
            'hold': hold,
            'decay2': decay2,
            'release': release,
            'unk53': unk53
        })
        return n

    def to_bytes(self):
        data = bytearray(0x30)
        dse_write_uintle(data, self.id, 0x01)
        dse_write_uintle(data, self.unk11, 0x02)
        dse_write_uintle(data, self.unk25, 0x03)
        dse_write_sintle(data, self.lowkey, 0x04)
        dse_write_sintle(data, self.hikey, 0x05)
        dse_write_sintle(data, self.lowkey, 0x06)
        dse_write_sintle(data, self.hikey, 0x07)
        dse_write_sintle(data, self.lolevel, 0x08)
        dse_write_sintle(data, self.hilevel, 0x09)
        dse_write_sintle(data, self.lolevel, 0x0A)
        dse_write_sintle(data, self.hilevel, 0x0B)
        dse_write_sintle(data, self.unk16, 0x0C, 4)
        dse_write_sintle(data, self.unk17, 0x10, 2)
        dse_write_uintle(data, self.sample_id, 0x12, 2)
        dse_write_sintle(data, self.ftune, 0x14)
        dse_write_sintle(data, self.ctune, 0x15)
        dse_write_sintle(data, self.rootkey, 0x16)
        dse_write_sintle(data, self.ktps, 0x17)
        dse_write_sintle(data, self.sample_volume, 0x18)
        dse_write_sintle(data, self.sample_pan, 0x19)
        dse_write_sintle(data, self.keygroup_id, 0x1A)
        dse_write_uintle(data, self.unk22, 0x1B, 2)
        dse_write_uintle(data, self.unk23, 0x1C, 2)
        dse_write_uintle(data, self.unk24, 0x1E, 2)

        dse_write_uintle(data, self.envelope, 0x20)
        dse_write_uintle(data, self.envelope_multiplier, 0x21)
        dse_write_uintle(data, self.unk37, 0x22)
        dse_write_uintle(data, self.unk38, 0x23)
        dse_write_uintle(data, self.unk39, 0x24, 2)
        dse_write_uintle(data, self.unk40, 0x26, 2)
        dse_write_sintle(data, self.attack_volume, 0x28)
        dse_write_sintle(data, self.attack, 0x29)
        dse_write_sintle(data, self.decay, 0x2A)
        dse_write_sintle(data, self.sustain, 0x2B)
        dse_write_sintle(data, self.hold, 0x2C)
        dse_write_sintle(data, self.decay2, 0x2D)
        dse_write_sintle(data, self.release, 0x2E)
        dse_write_sintle(data, self.unk53, 0x2F)

        return data

    def __eq__(self, other):
        if not isinstance(other, SwdlSplitEntry):
            return False
        return vars(self) == vars(other)


class SwdlProgramTable(DseAutoString):
    def __init__(self, data: Optional[Union[bytes, memoryview]], _assertId: Optional[int]):
        if data is None:
            return
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
        self._delimiter = dse_read_uintle(data, 0x0C)
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

    @classmethod
    def new(cls, id, prg_volume, prg_pan, unk3, that_f_byte, unk4, unk5, delimiter, unk7, unk8, unk9, lfos, splits):
        n = SwdlProgramTable(None, None)
        vars(n).update({
            'id': id,
            'prg_volume': prg_volume,
            'prg_pan': prg_pan,
            'unk3': unk3,
            'that_f_byte': that_f_byte,
            'unk4': unk4,
            'unk5': unk5,
            '_delimiter': delimiter,
            'unk7': unk7,
            'unk8': unk8,
            'unk9': unk9,
            'lfos': lfos,
            'splits': splits
        })
        return n

    def get_initial_delimiter(self):
        return self._delimiter

    def copy(self, new_wavi_ids: List[int] = None, new_kgrp_ids: List[int] = None) -> 'SwdlProgramTable':
        n = SwdlProgramTable(None, None)
        vars(n).update(vars(self))
        if new_wavi_ids is not None:
            for split, wid in zip(n.splits, new_wavi_ids):
                split.sample_id = wid
        if new_kgrp_ids is not None:
            for split, kid in zip(n.splits, new_kgrp_ids):
                split.keygroup_id = kid
        return n

    def to_bytes(self, delimiter=0x00):
        data = bytearray(0x10)
        dse_write_uintle(data, self.id, 0x00, 2)
        dse_write_uintle(data, len(self.splits), 0x02, 2)
        dse_write_sintle(data, self.prg_volume, 0x04)
        dse_write_sintle(data, self.prg_pan, 0x05)
        dse_write_uintle(data, self.unk3, 0x06)
        dse_write_uintle(data, self.that_f_byte, 0x07)
        dse_write_uintle(data, self.unk4, 0x08, 2)
        dse_write_uintle(data, self.unk5, 0x0A, 2)
        dse_write_uintle(data, len(self.lfos), 0x0B)
        dse_write_uintle(data, delimiter, 0x0C)
        dse_write_uintle(data, self.unk7, 0x0D)
        dse_write_uintle(data, self.unk8, 0x0E)
        dse_write_uintle(data, self.unk9, 0x0F)
        for lfo in self.lfos:
            data += lfo.to_bytes()
        data += bytes([delimiter] * 16)
        for split in self.splits:
            data += split.to_bytes()
        return data

    def __eq__(self, other):
        if not isinstance(other, SwdlProgramTable):
            return False
        return vars(self) == vars(other)


class SwdlPrgi:
    def __init__(self, data: Union[bytes, memoryview], number_slots: int):
        assert data[0x00:0x04] == b'prgi', "Data is not valid SWDL PRGI"
        assert data[0x004:0x06] == bytes(2), "Data is not valid SWDL PRGI"
        assert data[0x006:0x08] == bytes([0x15, 0x04]), "Data is not valid SWDL PRGI"
        assert data[0x008:0x0C] == bytes([0x10, 0x00, 0x00, 0x00]), "Data is not valid SWDL PRGI"
        len_chunk_data = dse_read_uintle(data, 0x0C, 4)

        self._length = 0x10 + len_chunk_data

        self.program_table: List[Optional[SwdlProgramTable]] = []
        for idx, seek in enumerate(range(0, number_slots * 2, 2)):
            pnt = dse_read_uintle(data, 0x10 + seek, 2)
            assert pnt < len_chunk_data, "Data is not valid SWDL PRGI"
            if pnt == 0:
                self.program_table.append(None)
            else:
                self.program_table.append(SwdlProgramTable(data[0x10 + pnt:], _assertId=idx))

    def to_bytes(self) -> bytes:
        chunk = bytearray(len(self.program_table) * 2)
        # Padding after TOC
        if len(chunk) % 16 != 0:
            chunk += bytes([0x00] * (16 - (len(chunk) % 16)))
        for i, prg in enumerate(self.program_table):
            if prg is not None:
                assert prg.id == i
                dse_write_uintle(chunk, len(chunk), i * 2, 2)
                chunk += prg.to_bytes(prg.get_initial_delimiter())
            else:
                dse_write_uintle(chunk, 0, i * 2, 2)

        buffer = bytearray(b'prgi\0\0\x15\x04\x10\0\0\0\0\0\0\0')
        dse_write_uintle(buffer, len(chunk), 0x0C, 4)
        return buffer + chunk

    def __str__(self):
        chunks = ""
        for prog in self.program_table:
            chunks += f">> {prog}\n"
        return """PRGI
""" + chunks

    def get_initial_length(self):
        return self._length

    def __eq__(self, other):
        if not isinstance(other, SwdlPrgi):
            return False
        return self.program_table == other.program_table

