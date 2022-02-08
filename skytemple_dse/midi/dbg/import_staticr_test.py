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
from skytemple_dse.soundvault.staticrfont_vault import StaticRFontVault
from skytemple_dse.soundvault.vault import Vault

base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
output_dir = os.path.join(os.path.dirname(__file__), 'dbg_output')
os.makedirs(output_dir, exist_ok=True)
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'CLEAN_ROM', '4468 - Pokemon Mystery Dungeon - Explorers of Sky (Europe) (En,Fr,De,Es,It).nds'))

#midi_to_import = '/usr/share/openttd/gm/tttheme2.mid'
midi_to_import = os.path.join(os.path.dirname(__file__), 'MysteryLOVANIA_Multi_Track.mid')
BGM_ID = 'bgm0001'


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

after_midi = smdl_to_midi(smd)
smd, warnings = midi_to_smdl(after_midi, swdl.header.unk2, swdl.header.unk1)
for warning in warnings:
    print(warning)


# Adjust SWDL
with open(os.path.join(os.path.dirname(__file__), '..', '..', 'soundvault', 'dbg', 'dbg_output', 'staticrvault.bin'), 'rb') as f:
    vault = StaticRFontVault.load(f.read())
main_bank = Swdl(rom.getFileByName('SOUND/BGM/bgm.swd'))

vault.apply(swdl, main_bank, smd.tracks)

swdl_bytes = SwdlWriter(swdl).write()
rom.setFileByName(f'SOUND/BGM/{BGM_ID}.swd', swdl_bytes)

rom.saveToFile(os.path.join(output_dir, 'out.nds'))
