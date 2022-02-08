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

from ndspy.rom import NintendoDSRom

from skytemple_dse.dse.smdl.model import Smdl, SmdlTrack, SmdlTrackHeader, SmdlTrackPreamble, SmdlEventPlayNote, \
    SmdlEventPause, SmdlPause, SmdlNote, SmdlEventSpecial, SmdlSpecialOpCode
from skytemple_dse.dse.smdl.writer import SmdlWriter
from skytemple_dse.dse.swdl.model import Swdl
from skytemple_dse.dse.swdl.writer import SwdlWriter
from skytemple_dse.midi.smdl_to_midi import smdl_to_midi

base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..')
output_dir = os.path.join(os.path.dirname(__file__), 'dbg_output')
os.makedirs(output_dir, exist_ok=True)
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy.nds'))

main = Swdl(rom.getFileByName(f'SOUND/BGM/bgm.swd'))
swdl = Swdl(rom.getFileByName(f'SOUND/BGM/bgm0001.swd'))
smdl = Smdl(rom.getFileByName(f'SOUND/BGM/bgm0001.smd'))

# Modify to only play sample notes
octs = []
for i in range(0, 10):
    octs += [
        SmdlEventSpecial(SmdlSpecialOpCode.SET_OCTAVE, [i]),
        SmdlEventPause(SmdlPause.HALF_NOTE),
        SmdlEventPlayNote(127, 0, SmdlNote.C, 48),
        SmdlEventPause(SmdlPause.HALF_NOTE),
        SmdlEventPlayNote(127, 0, SmdlNote.G, 48),
    ]
track = SmdlTrack(smdl.tracks[1].header, None, preamble=smdl.tracks[1].preamble)
track.events += smdl.tracks[1].events[0:6] + [SmdlEventSpecial(SmdlSpecialOpCode.SET_SAMPLE, [0x35])] + smdl.tracks[1].events[7:10] + octs + [SmdlEventPause(SmdlPause.HALF_NOTE)] * 20
smdl.tracks = [smdl.tracks[0], track]
smdl_to_midi(smdl).save('/tmp/out.mid')
assert SmdlWriter(smdl).write() == SmdlWriter(Smdl(SmdlWriter(smdl).write())).write()
rom.setFileByName(f'SOUND/BGM/bgm0001.smd', SmdlWriter(smdl).write())

# Delete all programs except 0x35 -> set attack = 127 | 64, all others 0
for s in swdl.prgi.program_table[0x35].splits:
    s.attack_volume = 127
    s.attack = 127
    s.decay = 0
    s.decay2 = 0
    s.release = 0
    s.hold = 0
    s.sustain = 127
    s.sample_id = 0x65
swdl.wavi.sample_info_table[0x65] = main.wavi.sample_info_table[0x65]

rom.setFileByName(f'SOUND/BGM/bgm0001.swd', SwdlWriter(swdl).write())
rom.saveToFile(os.path.join(output_dir, '127.nds'))

"""
for s in swdl.prgi.program_table[0x35].splits:
    s.attack = 126

rom.setFileByName(f'SOUND/BGM/bgm0001.swd', SwdlWriter(swdl).write())
rom.saveToFile(os.path.join(output_dir, '126.nds'))

for s in swdl.prgi.program_table[0x35].splits:
    s.attack = 64

rom.setFileByName(f'SOUND/BGM/bgm0001.swd', SwdlWriter(swdl).write())
rom.saveToFile(os.path.join(output_dir, '64.nds'))


for s in swdl.prgi.program_table[0x35].splits:
    s.attack = 32

rom.setFileByName(f'SOUND/BGM/bgm0001.swd', SwdlWriter(swdl).write())
rom.saveToFile(os.path.join(output_dir, '32.nds'))
"""

print(swdl.wavi.sample_info_table[182])