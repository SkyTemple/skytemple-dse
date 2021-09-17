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

from skytemple_dse.dse.smdl.model import Smdl
from skytemple_dse.dse.smdl.writer import SmdlWriter
from skytemple_dse.midi.midi_to_smdl import midi_to_smdl
from skytemple_dse.midi.smdl_to_midi import smdl_to_midi
from skytemple_files.common.util import get_files_from_rom_with_extension

base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
output_dir = os.path.join(os.path.dirname(__file__), 'dbg_output')
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy_us_unpatched.nds'))

for fname in get_files_from_rom_with_extension(rom, 'smd'):
    if not fname.startswith("SOUND") or 'bgm' not in fname or fname == 'SOUND/BGM/bgm.smd':
        continue
    print(fname)
    try:
        midi = smdl_to_midi(Smdl(rom.getFileByName(fname)))
        midi.save(os.path.join(output_dir, fname.replace('/', '_') + '.mid'))
        #for track in midi.tracks:
        #    for msg in track:
        #        if msg.type == 'marker' and msg.text.startswith('UNK'):
        #            msg.text = 'remove'
        #        if msg.type == 'marker' and msg.text.startswith('HEADER1'):
        #            msg.text = 'HEADER1 121'
        #        if msg.type == 'marker' and msg.text.startswith('HEADER2'):
        #            msg.text = 'HEADER2 126'

        rom.setFileByName(fname, SmdlWriter(midi_to_smdl(midi, 121, 126)[0]).write())
    except ValueError:
        print("failed.")  # TODO: Fix these

rom.saveToFile(os.path.join(output_dir, 'out_ref.nds'))
