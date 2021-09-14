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

from mido import MidiFile, Message
from ndspy.rom import NintendoDSRom

from skytemple_dse.dse.smdl.model import *
from skytemple_dse.dse.smdl.writer import SmdlWriter
from skytemple_dse.dse.swdl.model import Swdl
from skytemple_dse.midi.midi_to_smdl import midi_to_smdl
from skytemple_dse.midi.smdl_to_midi import smdl_to_midi

base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
output_dir = os.path.join(os.path.dirname(__file__), 'dbg_output')
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy_us_unpatched.nds'))

midi_to_import = '/usr/share/openttd/gm/tttheme2.mid'
#midi_to_import = os.path.join(output_dir, 'B_SYS_MENU.SMD.mid')


def remap_programs(midi: MidiFile):
    """This is needed, because the font doesn't contain any other programs."""
    mapping = {
        0: None,  # drums
        5: None,  # ?
        7: 7,  # bass
        26: 0x36, # background
        28: None, # ?
        30: 0x4b, # e guitar
        33: 6, # low bass
        35: 0x36, # bassy melody
        48: None, # ?
        66: 0x36  # main melody
    }
    tracks_to_remove = set()
    for tid, track in enumerate(midi.tracks):
        for event in track:
            if isinstance(event, Message) and event.type == 'program_change':
                if event.program in mapping:
                    if mapping[event.program] is None:
                        tracks_to_remove.add(tid)
                        continue
                    event.program = mapping[event.program]
    return tracks_to_remove


midi = MidiFile(midi_to_import)

filtered = remap_programs(midi)
midi.tracks = [t for tid, t in enumerate(midi.tracks) if tid not in filtered]
midi2 = MidiFile(midi_to_import)
midi2.tracks = [t for tid, t in enumerate(midi2.tracks) if tid not in filtered]
midi2.save('/tmp/filtered.midi')

midi.tracks = midi.tracks

smd, warnings = midi_to_smdl(midi)
for warning in warnings:
    print(warning)

model_bytes = rom.getFileByName('SOUND/BGM/bgm0002.smd')
after_bytes = SmdlWriter(smd).write()
rom.setFileByName('SOUND/BGM/bgm0002.smd', after_bytes)

with open('/tmp/before.bin', 'wb') as f:
    f.write(model_bytes)
with open('/tmp/after.bin', 'wb') as f:
    f.write(after_bytes)
os.system('xxd /tmp/before.bin > /tmp/before.bin.hex')
os.system('xxd /tmp/after.bin > /tmp/after.bin.hex')

after_midi = smdl_to_midi(smd)
after_midi.save(os.path.join(output_dir, 'after.mid'))

with open('/tmp/before.txt', 'w') as f:
    for track in midi.tracks:
        print("t", file=f)
        for event in track:
            print(event, file=f)
with open('/tmp/after.txt', 'w') as f:
    for track in after_midi.tracks:
        print("t", file=f)
        for event in track:
           print(event, file=f)

with open('/tmp/before_heads.txt', 'w') as f:
    model = Smdl(model_bytes)
    print(model.header, file=f)
    print(model.song, file=f)
    print(model.eoc, file=f)
    for track in model.tracks:
        print("t", file=f)
        print(track.header, file=f)
        print(track.preamble, file=f)
with open('/tmp/after_heads.txt', 'w') as f:
    model = smd
    print(model.header, file=f)
    print(model.song, file=f)
    print(model.eoc, file=f)
    for track in model.tracks:
        print("t", file=f)
        print(track.header, file=f)
        print(track.preamble, file=f)


# Adjust SWDL
swdl = Swdl(rom.getFileByName('SOUND/BGM/bgm0002.swd'))
print("swdl:")
print(swdl.header)
prgi_ids = set()
for track in smd.tracks:
    for e in track.events:
        if isinstance(e, SmdlEventSpecial) and e.op == SmdlSpecialOpCode.SET_SAMPLE:
            prgi_ids.add(e.params[0])
print("prgi - ")
kgrp_ids = set()
smpl_ids = set()
for i, x in enumerate(swdl.prgi.program_table):
    if i in prgi_ids:
        print(i, x)
        if x is not None:
            for s in x.splits:
                kgrp_ids.add(s.keygroup_id)
            for s in x.splits:
                smpl_ids.add(s.sample_id)

for i, x in enumerate(swdl.kgrp.keygroups):
    if i in kgrp_ids:
        print(i, x)

for i, x in enumerate(swdl.wavi.sample_info_table):
    if i in smpl_ids:
        print(i, x)

#print(swdl.wavi)


rom.saveToFile(os.path.join(output_dir, 'out.nds'))
