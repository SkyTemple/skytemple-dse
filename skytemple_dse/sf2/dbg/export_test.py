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

from ndspy.rom import NintendoDSRom

# noinspection PyUnresolvedReferences
from skytemple_files.common.util import get_files_from_rom_with_extension

from skytemple_dse.dse.swdl.model import Swdl
from skytemple_dse.sf2.swdl_to_sf2 import swdl_to_sf2

base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
output_dir = os.path.join(os.path.dirname(__file__), 'dbg_output')
os.makedirs(output_dir, exist_ok=True)
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy.nds'))

for filename in get_files_from_rom_with_extension(rom, 'swd'):
    try:
        if not filename.startswith("SOUND"):
            continue
        print(filename)
        model = Swdl(rom.getFileByName(filename))
    except:
        print("Skipped (read error).")
        continue
        #traceback.print_exc()

    sf2 = swdl_to_sf2(model)
    sf2.Write(os.path.join(output_dir, filename.replace('/', '_') + '.sf2'))
