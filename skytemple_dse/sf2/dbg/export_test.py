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
import csv
import os

from ndspy.rom import NintendoDSRom

# noinspection PyUnresolvedReferences
from skytemple_dse.dse.smdl.model import Smdl
from skytemple_files.common.util import get_files_from_rom_with_extension

from skytemple_dse.dse.swdl.model import Swdl
from skytemple_dse.sf2.swdl_to_sf2 import swdl_to_sf2

base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
output_dir = os.path.join(os.path.dirname(__file__), 'dbg_output')
os.makedirs(output_dir, exist_ok=True)
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy.nds'))

with open(os.path.join(output_dir, 'out.csv'), 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow([
        'TrackID', 'Track', 'ProgramID', 'SplitID', 'LowestKey', 'HighestKey',
        'ProgramVolume', 'ProgramPan', 'ProgramUnk3', 'ProgramUnk4', 'ProgramUnk5', 'ProgramUnk7', 'ProgramUnk8', 'ProgramUnk9',
        'LowestVelocity', 'HighestVelocity', 'SampleID', 'Volume', 'Pan', 'FineTune', 'CoarseTune',
        'PitchBendRange', 'RootKey', 'KeyTransposition', 'KeyGroupID',
        'SplitUnk25', 'SplitUnk16', 'SplitUnk17', 'SplitUnk22', 'SplitUnk23', 'SplitUnk24',
        'SplitUnk37', 'SplitUnk38', 'SplitUnk39', 'SplitUnk40', 'SplitUnk53',
        'EnableEnveloppe', 'EnveloppeDurationMultiplier', 'AttackVolume',
        'Attack', 'Decay', 'Sustain', 'Hold', 'FadeOut', 'Release'
    ])

    for filename in get_files_from_rom_with_extension(rom, 'swd'):
        try:
            if not filename.startswith("SOUND"):
                continue

            print(filename)
            model = Swdl(rom.getFileByName(filename))
            model_smdl = Smdl(rom.getFileByName(filename.replace('swd', 'smd')))
        except:
            print("Skipped (read error).")
            continue
            #traceback.print_exc()

        sf2 = swdl_to_sf2(model)
        sf2.Write(os.path.join(output_dir, filename.replace('/', '_') + '.sf2'))

        for pid, program in enumerate(model.prgi.program_table):
            if program is None:
                continue
            for sid, split in enumerate(program.splits):
                spamwriter.writerow([
                    filename.split('/')[-1], model_smdl.header.file_name, pid, sid, split.lowkey, split.hikey,
                    program.prg_volume, program.prg_pan, program.unk3, program.unk4, program.unk5, program.unk7, program.unk8, program.unk9,
                    split.lolevel, split.hilevel, split.sample_id, split.sample_volume, split.sample_pan, split.ftune, split.ctune,
                    split.unk11, split.rootkey, split.ktps, split.keygroup_id,
                    split.unk25, split.unk16, split.unk17, split.unk22, split.unk23, split.unk24,
                    split.unk37, split.unk38, split.unk39, split.unk40, split.unk53,
                    split.envelope, split.envelope_multiplier, split.attack_volume,
                    split.attack, split.decay, split.sustain, split.hold, split.decay2, split.release
                ])
