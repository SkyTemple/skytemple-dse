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
from typing import Union, Optional

from skytemple_dse.dse.common.date import DseDate
from skytemple_dse.dse.common.string import DseFilenameString
from skytemple_dse.dse.swdl.kgrp import SwdlKgrp
from skytemple_dse.dse.swdl.pcmd import SwdlPcmd
from skytemple_dse.dse.swdl.prgi import SwdlPrgi
from skytemple_dse.dse.swdl.wavi import SwdlWavi, SwdlPcmdReference
from skytemple_dse.util import *
LEN_HEADER = 80


class SwdlPcmdLen(DseAutoString):
    def __init__(self, ref: Optional[int], external: bool):
        self.ref = ref
        self.external = external

    @classmethod
    def from_bytes(cls, data: bytes):
        data = dse_read_uintle(data, 0, 4)
        ref = data
        external = False
        if data >> 0x10 == 0xAAAA:
            ref = data & 0x10
            external = True
        return cls(ref, external)

    def __eq__(self, other):
        if not isinstance(other, SwdlPcmdLen):
            return False
        return vars(self) == vars(other)

    def to_bytes(self):
        data = bytearray(4)
        if self.external:
            dse_write_uintle(data, self.ref + (0xAAAA << 0x10), 0, 4)
        else:
            dse_write_uintle(data, self.ref, 0, 4)

        assert self == self.from_bytes(data)
        return data


class SwdlHeader(DseAutoString):
    def __init__(self, data: Union[bytes, memoryview]):
        # Protected properties may only be valid during read of the model, you can get them with the getters.
        assert data[0:4] == b'swdl', "Data is not valid SWDL"
        assert data[4:8] == bytes(4), "Data is not valid SWDL"
        _in_length = dse_read_uintle(data, 0x08, 4)
        assert len(data) == _in_length, "Data is not valid SWDL"
        self.version = dse_read_uintle(data, 0x0C, 2)
        self.unk1 = dse_read_uintle(data, 0x0E, 1)
        self.unk2 = dse_read_uintle(data, 0x0F, 1)
        assert data[0x10:0x18] == bytes(8), "Data is not valid SWDL"
        self.modified_date = DseDate.from_bytes(data[0x18:0x20])
        self.file_name = DseFilenameString.from_bytes(data[0x20:0x30])
        assert data[0x30:0x34] == b'\x00\xaa\xaa\xaa', "Data is not valid SWDL"
        assert data[0x34:0x3C] == bytes(8), "Data is not valid SWDL"
        self.unk13 = dse_read_uintle(data, 0x3C, 4)
        self.pcmdlen = SwdlPcmdLen.from_bytes(data[0x40:0x44])
        assert data[0x44:0x46] == bytes(2), "Data is not valid SWDL"
        self._number_wavi_slots = dse_read_uintle(data, 0x46, 2)
        self._number_prgi_slots = dse_read_uintle(data, 0x48, 2)
        self.unk17 = dse_read_uintle(data, 0x4A, 2)
        self._len_wavi = dse_read_uintle(data, 0x4C, 4)

    def get_initial_wavi_len(self):
        return self._len_wavi

    def get_initial_number_wavi_slots(self):
        return self._number_wavi_slots

    def get_initial_number_prgi_slots(self):
        return self._number_prgi_slots

    def to_bytes(self, length: int, pcmdlen: SwdlPcmdLen, wavi_slots: int, prgi_slots: int, length_wavi: int):
        data = bytearray(80)
        data[0:4] = b'swdl'
        dse_write_uintle(data, length, 0x08, 4)
        dse_write_uintle(data, self.version, 0x0C, 2)
        dse_write_uintle(data, self.unk1, 0x0E, 1)
        dse_write_uintle(data, self.unk2, 0x0F, 1)
        data[0x18:0x20] = self.modified_date.to_bytes()
        data[0x20:0x30] = self.file_name.to_bytes(end_byte_0xaa=True)
        data[0x30:0x34] = b'\x00\xaa\xaa\xaa'
        dse_write_uintle(data, self.unk13, 0x3C, 4)
        data[0x40:0x44] = self.pcmdlen.to_bytes()
        dse_write_uintle(data, wavi_slots, 0x46, 2)
        dse_write_uintle(data, prgi_slots, 0x48, 2)
        dse_write_uintle(data, self.unk17, 0x4A, 2)
        dse_write_uintle(data, length_wavi, 0x4C, 4)
        return data

    def __eq__(self, other):
        if not isinstance(other, DseAutoString):
            return False
        return vars(self) == vars(other)


class Swdl:
    def __init__(self, data: bytes):
        if not isinstance(data, memoryview):
            data = memoryview(data)
        self.header = SwdlHeader(data)
        len_wavi = self.header.get_initial_wavi_len() + 0x10  # (0x10 = Header size) TODO: Is this correct???
        number_wavi_slots = self.header.get_initial_number_wavi_slots()
        number_prgi_slots = self.header.get_initial_number_prgi_slots()

        self.wavi: SwdlWavi = SwdlWavi(data[LEN_HEADER:LEN_HEADER + len_wavi], number_wavi_slots)
        assert len_wavi == self.wavi.get_initial_length(), "Data is not valid SWDL"

        start_prgi = start_pcmd = LEN_HEADER + len_wavi
        self.pcmd: Optional[SwdlPcmd] = None
        self.prgi: Optional[SwdlPrgi] = None
        self.kgrp: Optional[SwdlKgrp] = None
        if data[start_pcmd:start_pcmd + 4] == b'prgi':
            # Has PRGI & KGRP
            self.prgi = SwdlPrgi(data[start_prgi:], number_prgi_slots)
            start_kgrp = start_prgi + self.prgi.get_initial_length()
            assert start_kgrp % 16 == 0
            self.kgrp = SwdlKgrp(data[start_kgrp:])

            start_pcmd += self.prgi.get_initial_length() + self.kgrp.get_initial_length()

        if not self.header.pcmdlen.external and self.header.pcmdlen.ref:
            self.pcmd = SwdlPcmd(data[start_pcmd:start_pcmd + self.header.pcmdlen.ref + 0x10])  # (0x10 = Header size) TODO: Is this correct???
            self._dbg_pcmd_after_wavi = True
            start_prgi += self.pcmd.get_initial_length()

            # Add pcmd samples to wavi
            for sample in self.wavi.sample_info_table:
                if sample:
                    offs, length = sample.get_initial_sample_pos(), sample.sample_length
                    assert offs+length <= len(self.pcmd.chunk_data), "Invalid Swdl sample data"
                    sample.sample = SwdlPcmdReference(self.pcmd, offs, length)

    def __str__(self):
        return f"""SWDL <<{self.header}>>:
> {self.wavi}
> {self.prgi}
> {self.kgrp}
-----------"""

    def __eq__(self, other):
        if not isinstance(other, Swdl):
            return False
        return self.pcmd == other.pcmd and self.prgi == other.prgi and self.kgrp == other.kgrp and \
               self.wavi == other.wavi and self.header == other.header
