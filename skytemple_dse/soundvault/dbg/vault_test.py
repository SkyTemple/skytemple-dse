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

import os
from typing import Dict

from ndspy.rom import NintendoDSRom

# noinspection PyUnresolvedReferences
from skytemple_files.common.util import get_files_from_rom_with_extension

from skytemple_dse.dse.swdl.model import Swdl
from skytemple_dse.dse.swdl.writer import SwdlWriter
from skytemple_dse.soundvault.vault import Vault

base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
output_dir = os.path.join(os.path.dirname(__file__), 'dbg_output')
os.makedirs(output_dir, exist_ok=True)
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy.nds'))

# Build vault
main_bank: Swdl = None
swdls: Dict[str, Swdl] = {}
for filename in get_files_from_rom_with_extension(rom, 'swd'):
    if 'bgm' not in filename:
        continue
    swdl = Swdl(rom.getFileByName(filename))
    if filename == 'SOUND/BGM/bgm.swd':
        main_bank = swdl
    else:
        swdls[filename.split('/')[-1]] = swdl

vault = Vault()
vault.fill_from_swdls(swdls, main_bank)
with open(os.path.join(output_dir, 'vault.bin'), 'wb') as f:
    f.write(vault.save())

prog = next(v for v in vault.get_all_from_swdl_by_filename()['bgm0004.swd'] if v.original_swdl_program_id == 0xA)
for fname, swdl in swdls.items():
    for prg in swdl.prgi.program_table:
        if prg is not None:
            assert not prog.load_into_swdl(swdl, main_bank, prg.id)
    rom.setFileByName(f'SOUND/BGM/{fname}', SwdlWriter(swdl).write())

rom.saveToFile(os.path.join(output_dir, 'out.nds'))
