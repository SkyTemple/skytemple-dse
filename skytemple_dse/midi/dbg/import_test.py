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
from skytemple_dse.dse.swdl.kgrp import SwdlKeygroup
from skytemple_dse.dse.swdl.model import Swdl
from skytemple_dse.dse.swdl.prgi import SwdlProgramTable, SwdlSplitEntry, SwdlLfoEntry, SwdlLfoDest, SwdlWshape
from skytemple_dse.dse.swdl.writer import SwdlWriter
from skytemple_dse.midi.midi_to_smdl import midi_to_smdl
from skytemple_dse.midi.smdl_to_midi import smdl_to_midi
from skytemple_dse.soundvault.vault import Vault

base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
output_dir = os.path.join(os.path.dirname(__file__), 'dbg_output')
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'CLEAN_ROM', '4468 - Pokemon Mystery Dungeon - Explorers of Sky (Europe) (En,Fr,De,Es,It).nds'))

#midi_to_import = '/usr/share/openttd/gm/tttheme2.mid'
midi_to_import = os.path.join(os.path.dirname(__file__), 'MysteryLOVANIA_Multi_Track.mid')
#midi_to_import = os.path.join(output_dir, 'B_SYS_MENU.SMD.mid')
BGM_ID = 'bgm0015'


def remove_program(midi: MidiFile, pid):
    tracks_to_remove = set()
    for tid, track in enumerate(midi.tracks):
        for event in track:
            if isinstance(event, Message) and event.type == 'program_change':
                if event.program == pid:
                    tracks_to_remove.add(tid)
    midi.tracks = [t for tid, t in enumerate(midi.tracks) if tid not in tracks_to_remove]


midi = MidiFile(midi_to_import)
remove_program(midi, 125)

swdl_in_bytes = rom.getFileByName(f'SOUND/BGM/{BGM_ID}.swd')
swdl = Swdl(swdl_in_bytes)
swdl.header.unk1 = 127
swdl.header.unk2 = 0

smd, warnings = midi_to_smdl(midi, swdl.header.unk2, swdl.header.unk1)
for warning in warnings:
    print(warning)

model_bytes = rom.getFileByName(f'SOUND/BGM/{BGM_ID}.smd')
after_bytes = SmdlWriter(smd).write()
rom.setFileByName(f'SOUND/BGM/{BGM_ID}.smd', after_bytes)

with open('/tmp/before.bin', 'wb') as f:
    f.write(model_bytes)
with open('/tmp/after.bin', 'wb') as f:
    f.write(after_bytes)
os.system('xxd /tmp/before.bin > /tmp/before.bin.hex')
os.system('xxd /tmp/after.bin > /tmp/after.bin.hex')

after_midi = smdl_to_midi(smd)
after_midi.save(os.path.join(output_dir, 'after.mid'))
smd, warnings = midi_to_smdl(after_midi, swdl.header.unk2, swdl.header.unk1)
for warning in warnings:
    print(warning)

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
with open(os.path.join(os.path.dirname(__file__), '..', '..', 'soundvault', 'dbg', 'dbg_output', 'vault.bin'), 'rb') as f:
    vault = Vault.load(f.read())
print("swdl:")
print(swdl.header)
prgi_ids = set()
for track in smd.tracks:
    for e in track.events:
        if isinstance(e, SmdlEventSpecial) and e.op == SmdlSpecialOpCode.SET_SAMPLE:
            prgi_ids.add(e.params[0])


def remap_program(in_swdl, in_main_bank, in_prog_id, filename, orig_prog_id):
    if in_prog_id not in prgi_ids:
        print(in_prog_id, " not mapped.")
        return
    prog = next(v for v in vault.get_all_from_swdl_by_filename()[filename] if v.original_swdl_program_id == orig_prog_id)
    assert not prog.load_into_swdl(in_swdl, in_main_bank, in_prog_id)
    #if prog.load_into_swdl(in_swdl, in_main_bank, in_prog_id):
    #    rom.setFileByName(f'SOUND/BGM/{BGM_ID}.swd', SwdlWriter(in_main_bank).write())


def map_new_programm(in_swdl, in_main_bank, in_prog_id, wavi_id, in_prg, instrument_name, name):
    if in_prog_id not in prgi_ids:
        print(in_prog_id, " not mapped.")
        return
    prog = vault.add_sample_from_master(
        in_main_bank.pcmd, in_prg,
        [in_swdl.kgrp.keygroups[0]], [in_main_bank.wavi.sample_info_table[wavi_id]],
        instrument_name, name
    )
    assert not prog.load_into_swdl(in_swdl, in_main_bank, in_prog_id)

empty_lfo = SwdlLfoEntry.new(
    unk34=0, unk52=0, dest=SwdlLfoDest.NONE, wshape=SwdlWshape.SQUARE, rate=0, unk29=0, depth=0,
    delay=0, unk32=0, unk33=0
)
# https://docs.google.com/spreadsheets/d/1kCE4aSEHMuXJv36APnee0gORP8ncfiizQvI62XuAGL8/edit#gid=1732285436
main_bank = Swdl(rom.getFileByName('SOUND/BGM/bgm.swd'))

swdl.prgi.program_table = []
swdl.kgrp.keygroups = [swdl.kgrp.keygroups[0]]
swdl.wavi.sample_info_table = []

#remap_program(swdl, main_bank, 125, 'bgm0008.swd', 0x7f)  # Drumkit
remap_program(swdl, main_bank, 13, 'bgm0001.swd', 0x0C)   # Explorers of Time Opening, Tubular Bells
remap_program(swdl, main_bank, 21, 'bgm0047.swd', 0x1C)   # Deep Brine Cave, Pick Bass
remap_program(swdl, main_bank, 39, 'bgm0007.swd', 0x48)   # Wigglytuff's Guild, Violin 1
remap_program(swdl, main_bank, 53, 'bgm0016.swd', 0x44)   # Battle Against Dialga, Trumpet Section
remap_program(swdl, main_bank, 49, 'bgm0014.swd', 0x23)   # End of Dungeon, Choir Aahs
remap_program(swdl, main_bank, 64, 'bgm0090.swd', 0x42)   # Ending Theme (Staff Roll/Credits), Brass 4
remap_program(swdl, main_bank, 65, 'bgm0024.swd', 0x40)   # Waterfall Cave, Horn Section
remap_program(swdl, main_bank, 87, 'bgm0003.swd', 0x61)   # Marowack Dojo, Synth Jaw
remap_program(swdl, main_bank, 32, 'bgm0178.swd', 0x16)   # Team Charm's Theme (Part 1: Suspense), Distorted Guitar
remap_program(swdl, main_bank, 43, 'bgm0009.swd', 0x2e)   # Treasure Town, Viola Section
remap_program(swdl, main_bank, 44, 'bgm0001.swd', 0x1f)   # Explorers of Time Opening, String Section
remap_program(swdl, main_bank, 92, 'bgm0018.swd', 0x21)   # Battle Vs. Regi's, Synth 2
remap_program(swdl, main_bank, 18, 'bgm0064.swd', 0x08)   # Explorers of Time/Darkness Opening, Synth Organ
remap_program(swdl, main_bank, 88, 'bgm0012.swd', 0x60)   # Keckleon Shop in Dungeon, Synth Square
remap_program(swdl, main_bank, 25, 'bgm0005.swd', 0x19)   # Mission Success, Synth Bass 1
remap_program(swdl, main_bank, 60, 'bgm0007.swd', 0x03)   # Battle Against Dusknoir, Brass Section
remap_program(swdl, main_bank, 93, 'bgm0015.swd', 0x5e)   # Boss Battle, Synth 3
remap_program(swdl, main_bank, 31, 'bgm0099.swd', 0x16)   # Lower Spring Cave, Ocerdriven Guitar
map_new_programm(swdl, main_bank, 55, 0x63,               # 55: Solo Trumpet 2 [Wavi 0x63]
                 SwdlProgramTable.new(
                     id=-1, prg_volume=127, prg_pan=64, unk3=0, that_f_byte=0xF, unk4=0x200, unk5=0, delimiter=0xAA,
                     unk7=0, unk8=0, unk9=0, lfos=[empty_lfo], splits=[SwdlSplitEntry.new(
                         id=0, unk11=2, unk25=1, lowkey=0, hikey=127, lolevel=0, hilevel=127, unk16=0, unk17=0,
                         sample_id=-1, ftune=88, ctune=-7, rootkey=74, ktps=0, sample_volume=127, sample_pan=64,
                         keygroup_id=-1, unk22=2, unk23=0, unk24=0, envelope=1, envelope_multiplier=1, unk37=1,
                         unk38=3, unk39=65283, unk40=65285, attack_volume=0, attack=0, decay=0, sustain=127, hold=0,
                         decay2=127, release=40, unk53=-1
                     )]
                 ),
                 'Solo Trumpet 2', 'SF55')
map_new_programm(swdl, main_bank, 48, 0x57,               # 48: Orchestral Hit [Wavi 0x57]
                 SwdlProgramTable.new(
                     id=-1, prg_volume=127, prg_pan=64, unk3=0, that_f_byte=0xF, unk4=0x200, unk5=0, delimiter=0xAA,
                     unk7=0, unk8=0, unk9=0, lfos=[empty_lfo], splits=[SwdlSplitEntry.new(
                         id=0, unk11=2, unk25=1, lowkey=0, hikey=127, lolevel=0, hilevel=127, unk16=0, unk17=0,
                         sample_id=-1, ftune=88, ctune=-7, rootkey=60, ktps=0, sample_volume=127, sample_pan=64,
                         keygroup_id=-1, unk22=2, unk23=0, unk24=0, envelope=1, envelope_multiplier=1, unk37=1,
                         unk38=3, unk39=65283, unk40=65285, attack_volume=0, attack=0, decay=0, sustain=127, hold=0,
                         decay2=127, release=40, unk53=-1
                     )]
                 ),
                 'Orchestral Hit', 'SF48')
map_new_programm(swdl, main_bank, 79, 0x0F,               # 79: Hard Clarinet [Wavi 0xf]
                 SwdlProgramTable.new(
                     id=-1, prg_volume=127, prg_pan=64, unk3=0, that_f_byte=0xF, unk4=0x200, unk5=0, delimiter=0xAA,
                     unk7=0, unk8=0, unk9=0, lfos=[empty_lfo], splits=[SwdlSplitEntry.new(
                         id=0, unk11=2, unk25=1, lowkey=0, hikey=127, lolevel=0, hilevel=127, unk16=0, unk17=0,
                         sample_id=-1, ftune=88, ctune=-7, rootkey=60, ktps=0, sample_volume=127, sample_pan=64,
                         keygroup_id=-1, unk22=2, unk23=0, unk24=0, envelope=1, envelope_multiplier=1, unk37=1,
                         unk38=3, unk39=65283, unk40=65285, attack_volume=0, attack=0, decay=0, sustain=127, hold=0,
                         decay2=127, release=40, unk53=-1
                     )]
                 ),
                 'Hard Clarinet', 'SF79')


swdl_bytes = SwdlWriter(swdl).write()
rom.setFileByName(f'SOUND/BGM/{BGM_ID}.swd', swdl_bytes)

print("prgi - ")
kgrp_ids = set()
smpl_ids = set()
for i, x in enumerate(swdl.prgi.program_table):
    if i in prgi_ids:
        print(i, x)
        assert x is not None
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
with open(os.path.join(output_dir, 'out.swdl'), 'wb') as f:
    f.write(swdl_bytes)
with open(os.path.join(output_dir, 'out.smdl'), 'wb') as f:
    f.write(after_bytes)
with open(os.path.join(output_dir, 'in.swdl'), 'wb') as f:
    f.write(swdl_in_bytes)
with open(os.path.join(output_dir, 'in.smdl'), 'wb') as f:
    f.write(model_bytes)
with open(os.path.join(output_dir, 'main.swdl'), 'wb') as f:
    f.write(rom.getFileByName('SOUND/BGM/bgm.swd'))
