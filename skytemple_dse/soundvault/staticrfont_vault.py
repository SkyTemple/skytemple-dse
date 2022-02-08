"""A vault specialized for use with StaticR's soundfont."""
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
import csv
import logging
import os.path
import pickle
from typing import List, Dict, Optional, TypeVar, Generic, Tuple

from skytemple_dse.dse.smdl.model import SmdlTrack, SmdlEventSpecial, SmdlSpecialOpCode
from skytemple_dse.dse.swdl.kgrp import SwdlKeygroup
from skytemple_dse.dse.swdl.model import Swdl
from skytemple_dse.dse.swdl.pcmd import SwdlPcmd
from skytemple_dse.dse.swdl.prgi import SwdlProgramTable, SwdlSplitEntry
from skytemple_dse.soundvault.program import Program
PATH_SOUNDFONT_MAPPING = os.path.join(os.path.dirname(__file__), '..', '_resources', 'staticr_soundfont_mapping.csv')
PATH_SOUNDFONT_SWDL_MAPPING = os.path.join(os.path.dirname(__file__), '..', '_resources', 'staticr_soundfont_swdl_mapping.csv')
T = TypeVar('T')
logger = logging.getLogger(__name__)


class StaticRSoundfontProgram:
    """
    A class representing one row in staticr_soundfont_mapping.csv
    """
    def __init__(
            self, category, _1, _2, _3, instrument, program, bank, sf_ftune, sf_ctune,
            sf_lowkey, sf_highkey, _7, _8, _9, _10, _11, _12, _4, pitch_bend, unk25, lowkey, highkey, lovel, hivel,
            sample, ftune, ctune, root_key, kpts, volume, pan, kgrp_id, env, env_duration,
            attack_volume, attack, decay, sustain, hold, fade_out, release,
            _13, _14, _15, _16, _17
    ):
        self.category = category
        self.instrument = instrument
        self.program = int(program) if program != '' else -999
        self.bank = int(bank) if bank != '' else -999
        self.sf_ftune = int(sf_ftune) if sf_ftune != '' else -999
        self.sf_ctune = int(sf_ctune) if sf_ctune != '' else -999
        self.sf_lowkey = int(sf_lowkey) if (sf_lowkey != '-' and sf_lowkey != '') else -999
        self.sf_highkey = int(sf_highkey) if (sf_highkey != '-' and sf_highkey != '') else -999
        self.pitch_bend = int(pitch_bend)
        self.unk25 = int(unk25)
        self.lowkey = int(sf_lowkey) if (sf_lowkey != '-' and sf_lowkey != '')else -999  # lowkey
        self.highkey = int(sf_highkey) if (sf_highkey != '-' and sf_highkey != '')  else -999  # highkey
        self.lovel = int(lovel)
        self.hilvel = int(hivel)
        self.sample = int(sample)
        self.ftune = int(sf_ftune) if sf_ftune != '' else -999  # ftune
        self.ctune = int(sf_ctune) if sf_ctune != '' else -999  # ctune
        self.root_key = int(root_key)
        self.kpts = int(kpts)
        self.volume = int(volume) if volume != '' else -999
        self.pan = int(pan)
        self.kgrp_id = int(kgrp_id) if kgrp_id != '' else -999
        self.env = int(env)
        self.env_duration = int(env_duration)
        self.attack_volume = int(attack_volume)
        self.attack = int(attack)
        self.decay = int(decay)
        self.sustain = int(sustain)
        self.hold = int(hold)
        self.fade_out = int(fade_out)
        self.release = int(release)
        self.eos_mapping: Optional['StaticRSoundfontSwdlMapping'] = None


class StaticRSoundfontSwdlMapping:
    def __init__(self, _, swdl_filename, keygroup_id, *args):
        self.swdl_filename = swdl_filename
        self.keygroup_id = keygroup_id


class StaticRFontVault:
    def __init__(self):
        self._banks: Dict[int, Dict[int, Program]] = {}

    @classmethod
    def load(cls, data) -> 'StaticRFontVault':
        obj = pickle.loads(data)
        assert type(obj) == StaticRFontVault
        return obj

    def save(self) -> bytes:
        return pickle.dumps(self)

    def generate(self, swdls: Dict[str, Swdl], master_bank: Swdl):
        eos_mappings: List[StaticRSoundfontSwdlMapping] = []
        with open(PATH_SOUNDFONT_SWDL_MAPPING) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                eos_mappings.append(StaticRSoundfontSwdlMapping(*row.values()))

        info: Dict[int, Dict[int, List[StaticRSoundfontProgram]]] = {}
        with open(PATH_SOUNDFONT_MAPPING) as csvfile:
            reader = csv.DictReader(csvfile)
            for i_row, row in enumerate(reader):
                v = StaticRSoundfontProgram(*row.values())
                v.eos_mapping = eos_mappings[i_row]
                if v.program == -999 or v.lowkey == -999 or v.highkey == -999:
                    continue
                if v.bank not in info:
                    info[v.bank] = {}
                bank = info[v.bank]
                if v.program not in bank:
                    bank[v.program] = []
                bank[v.program].append(v)

        for bank_id, bank in info.items():
            for program_id, programs in bank.items():
                self._init_program(bank_id, program_id, programs, master_bank, swdls)

    def _init_program(self, bank_id: int, program_id: int, programs: List[StaticRSoundfontProgram],
                      master_bank: Swdl, swdls: Dict[str, Swdl]):
        if bank_id not in self._banks:
            self._banks[bank_id] = {}
        if program_id in self._banks[bank_id]:
            raise ValueError("Program defined multiple times.")

        prg = SwdlProgramTable(None, None)
        prg.id = -1
        prg.prg_volume = 127
        prg.prg_pan = 64
        prg.unk3 = 0
        prg.that_f_byte = 15
        prg.unk4 = 512
        prg.unk5 = 0
        prg.unk7 = 0
        prg.unk8 = 0
        prg.unk9 = 0
        prg.lfos = []
        prg.splits = []
        # TODO: LFOs?

        kgrps = []
        wavis = []
        sample_data = []
        for i, split_prog in enumerate(sorted(programs, key=lambda sp: sp.lowkey)):
            source_swdl, kgrp = self._load_subswdl_data(split_prog, swdls, master_bank)
            kgrps.append(kgrp)
            # Since the sub-bank wavis can override the main bank wavi's parameters
            # we use the sub-bank wavi but copy the offsets
            wavi = source_swdl.wavi.sample_info_table[int(split_prog.sample)]
            wavi.force_set_sample_pos(master_bank.wavi.sample_info_table[int(split_prog.sample)].get_initial_sample_pos())
            wavis.append(wavi)
            split_entry = SwdlSplitEntry(None)
            split_entry.id = i
            split_entry.unk11 = split_prog.pitch_bend
            split_entry.unk25 = 0  # Todo: Also 1 often
            split_entry.lowkey = split_prog.lowkey
            split_entry.hikey = split_prog.highkey
            split_entry.lolevel = split_prog.lovel
            split_entry.hilevel = split_prog.hilvel
            split_entry.unk16 = -1431655766  # Todo: Also 0 sometimes
            split_entry.unk17 = -21846  # Todo: Also 0 sometimes
            split_entry.sample_id = -1
            split_entry.ftune = split_prog.ftune
            split_entry.ctune = split_prog.ctune
            split_entry.rootkey = split_prog.root_key
            split_entry.ktps = split_prog.kpts
            split_entry.sample_volume = split_prog.volume
            split_entry.sample_pan = split_prog.pan
            split_entry.keygroup_id = -1
            split_entry.unk22 = 2
            split_entry.unk23 = 0
            split_entry.unk24 = 43690  # Todo: Also 0 rarely
            split_entry.envelope = split_prog.env
            split_entry.envelope_multiplier = split_prog.env_duration
            split_entry.unk37 = 1
            split_entry.unk38 = 3
            split_entry.unk39 = 65283
            split_entry.unk40 = 65535
            split_entry.attack_volume = split_prog.attack_volume
            split_entry.attack = split_prog.attack
            split_entry.decay = split_prog.decay
            split_entry.sustain = split_prog.sustain
            split_entry.hold = split_prog.hold
            split_entry.decay2 = split_prog.fade_out
            split_entry.release = split_prog.release
            split_entry.unk53 = -1

            prg.splits.append(split_entry)
        for w in wavis:
            smpl = self._extract_sample_from_master(
                master_bank.pcmd,
                w.get_initial_sample_pos(), w.sample_length
            )
            assert smpl in master_bank.pcmd.chunk_data
            sample_data.append(smpl)

        self._banks[bank_id][program_id] = Program(
            programs[0].instrument, None,
            sample_data, prg, kgrps, wavis,
            None, None, None
        )

    @staticmethod
    def _extract_sample_from_master(pcmd: SwdlPcmd, start: int, length: int):
        """Extracts a sample from the master bank."""
        return pcmd.chunk_data[start:start+length]

    @staticmethod
    def _load_subswdl_data(
            split_prog: StaticRSoundfontProgram, swdls: Dict[str, Swdl], master_bank: Swdl
    ) -> Tuple[Swdl, SwdlKeygroup]:
        if split_prog.eos_mapping.swdl_filename == '-1':
            # Fallback :(
            return master_bank, swdls['bgm0000.swd'].kgrp.keygroups[0]
        else:
            swdl = swdls[split_prog.eos_mapping.swdl_filename]
            return swdl, swdl.kgrp.keygroups[int(split_prog.eos_mapping.keygroup_id)]

    def apply(self, swdl: Swdl, main_bank: Swdl, tracks: List[SmdlTrack]):
        programs_used = set()
        for track in tracks:
            for event in track.events:
                if isinstance(event, SmdlEventSpecial) and event.op == SmdlSpecialOpCode.SET_SAMPLE:
                    programs_used.add(event.params[0])

        # Clear SWDL Programs, Keygroups, Wavi
        swdl.prgi.program_table = []
        swdl.kgrp.keygroups = []
        swdl.wavi.sample_info_table = []

        for program_id in programs_used:
            entry = self._banks[0][program_id]
            entry.load_into_swdl(swdl, main_bank, program_id)
