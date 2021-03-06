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
import sys
import traceback
from tempfile import NamedTemporaryFile

from ndspy.rom import NintendoDSRom

# noinspection PyUnresolvedReferences
from skytemple_files.common.util import get_files_from_rom_with_extension

from skytemple_dse.dse.smdl.model import Smdl
from skytemple_dse.dse.smdl.writer import SmdlWriter

base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')
output_dir = os.path.join(os.path.dirname(__file__), 'dbg_output')
os.makedirs(output_dir, exist_ok=True)
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy.nds'))

for filename in get_files_from_rom_with_extension(rom, 'smd'):
    if not filename.startswith("SOUND"):
        continue
    print(filename)
    model_bytes = rom.getFileByName(filename)
    model = Smdl(model_bytes)
    after_bytes = SmdlWriter(model).write()

    try:
        assert model_bytes == after_bytes
    except:
        with open('/tmp/before.bin', 'wb') as f:
            f.write(model_bytes)
        with open('/tmp/after.bin', 'wb') as f:
            f.write(after_bytes)
        os.system('xxd /tmp/before.bin > /tmp/before.bin.hex')
        os.system('xxd /tmp/after.bin > /tmp/after.bin.hex')
        raise
