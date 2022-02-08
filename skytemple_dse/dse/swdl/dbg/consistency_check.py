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
import os
from typing import List

from ndspy.rom import NintendoDSRom

from skytemple_dse.dse.swdl.model import Swdl
from skytemple_files.common.util import get_files_from_rom_with_extension

base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy_us_unpatched.nds'))

main_bank: Swdl = None
swdls: List[Swdl] = []
for filename in get_files_from_rom_with_extension(rom, 'swd'):
    if 'bgm' not in filename:
        continue
    swdl = Swdl(rom.getFileByName(filename))
    if filename == 'SOUND/BGM/bgm.swd':
        main_bank = swdl
    else:
        swdls.append(swdl)


def assert_check(base_list, sub_list_getter):
    lst = []
    for bobj_id, bobj in enumerate(base_list):
        for sobj_id, sobj in enumerate(sub_list_getter(bobj)):
            if sobj is not None:
                while len(lst) <= sobj_id:
                    lst.append(None)
                if lst[sobj_id] is None:
                    lst[sobj_id] = sobj
                else:
                    try:
                        assert lst[sobj_id] == sobj
                    except AssertionError:
                        print(f"err at {bobj_id},{sobj_id}")
                        raise


# WAVIS
try:
    assert_check([main_bank] + swdls, lambda swdl: swdl.wavi.sample_info_table)
except AssertionError:
    print("WAVIS NOT SAME")
else:
    print("wavis ok")

# SAMPLES
try:
    wavis = []
    for wavi_id, wavi in enumerate(main_bank.wavi.sample_info_table):
        if wavi is None:
            #print(f"> main wavi {wavi_id} is None?")
            continue
        wavis.append(main_bank.pcmd.chunk_data[wavi.get_initial_sample_pos():wavi.get_initial_sample_pos()+wavi.sample_length])

    for swdl_id, swdl in enumerate(swdls):
        for wavi_id, wavi in enumerate(swdl.wavi.sample_info_table):
            if wavi is not None:
                try:
                    assert main_bank.pcmd.chunk_data[wavi.get_initial_sample_pos():wavi.get_initial_sample_pos()+wavi.sample_length]
                except AssertionError:
                    print(f"err at {swdl_id},{wavi_id}")
                    raise
except AssertionError:
    print("SAMPLES NOT SAME")
else:
    print("samples ok")

# PROGRAMS
try:
    assert_check(swdls, lambda swdl: swdl.prgi.program_table)
except AssertionError:
    print("PROGRAMS NOT SAME")
else:
    print("programs ok")

# KEYGROUPS
try:
    assert_check(swdls, lambda swdl: swdl.kgrp.keygroups)
except AssertionError:
    print("KEYGROUPS NOT SAME")
else:
    print("keygroups ok")
