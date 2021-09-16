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
import logging
import pickle
from typing import Union, List, Dict, Optional, Tuple

from skytemple_dse.dse.swdl.kgrp import SwdlKeygroup
from skytemple_dse.dse.swdl.model import Swdl
from skytemple_dse.dse.swdl.pcmd import SwdlPcmd
from skytemple_dse.dse.swdl.prgi import SwdlProgramTable
from skytemple_dse.dse.swdl.wavi import SwdlSampleInfoTblEntry
from skytemple_dse.soundvault.program import Program
logger = logging.getLogger(__name__)


class Vault:
    def __init__(self):
        # Sound programs collected from the game's SWDL files
        self._source_swdl_by_file_name: Dict[str, List[Program]] = {}
        self._source_swdl_by_src_name: Dict[str, List[Program]] = {}
        # Pre-defined sound programs, provided with the app.
        self._source_system: List[Program] = []
        # User-added sound programs.
        self._source_user: List[Program] = []

    @classmethod
    def load(cls, data) -> 'Vault':
        obj = pickle.loads(data)
        assert type(obj) == Vault
        return obj

    def save(self) -> bytes:
        return pickle.dumps(self)

    def fill_from_swdls(self, swdls: Dict[str, Swdl], master_bank: Swdl,
                        name_lookup_table: Optional[dict[str, List[Tuple[str, str]]]] = None):
        """
        Fill the vault with data from the original Swdls.
        :param swdls: The original Swdls. Keys are the original filenames (without path). Not including the master bank.
        :param master_bank: The master Swdl bank.
        :param name_lookup_table: A table that contains tuples (instrument_name, name) [see add_sample] for each program
                                  of each swdl. The outer keys are the filenames as in `swdls`, the inner lists contain
                                  one tuple per program. If an entry is None or this parameter is omitted, programs
                                  without names are not queryable by instrument or name.
                                  The name part is used here by convention for the original track name.
        """
        self._source_swdl_by_src_name = {}
        self._source_swdl_by_file_name = {}
        for fname, swdl in swdls.items():
            programs = []
            for progid, prg in enumerate(swdl.prgi.program_table):
                if prg is not None:
                    prg: SwdlProgramTable
                    instrument_name, name = None, None
                    if name_lookup_table is not None and fname in name_lookup_table and len(name_lookup_table[fname]) < progid:
                        instrument_name, name = name_lookup_table[fname][progid]
                    kgrps = []
                    wavis = []
                    sample_data = []
                    for s in prg.splits:
                        kgrpid = s.keygroup_id
                        if len(swdl.kgrp.keygroups) <= s.keygroup_id:
                            # Todo: Why?
                            logger.warning(f'{fname}: prg {progid} had invalid keygroup id: {s.keygroup_id}. '
                                           f'Max is {len(swdl.kgrp.keygroups)-1}. Replaced with 0.')
                            kgrpid = 0
                        kgrps.append(swdl.kgrp.keygroups[kgrpid])
                        # Since the sub-bank wavis can override the main bank wavi's parameters
                        # we use the sub-bank wavi but copy the offsets
                        wavi = swdl.wavi.sample_info_table[s.sample_id]
                        wavi.force_set_sample_pos(master_bank.wavi.sample_info_table[s.sample_id].get_initial_sample_pos())
                        wavis.append(wavi)
                    for w in wavis:
                        sample_data.append(self._extract_sample_from_master(
                            master_bank.pcmd,
                            w.get_initial_sample_pos(), w.sample_length
                        ))
                    programs.append(Program(
                        instrument_name, name,
                        sample_data, prg, kgrps, wavis,
                        fname, swdl.header.file_name, progid
                    ))

            self._source_swdl_by_file_name[fname] = programs
            self._source_swdl_by_src_name[swdl.header.file_name.string] = programs

    def add_sample_from_master(
            self, master_pcmd: SwdlPcmd, prg: SwdlProgramTable,
            kgrps: List[SwdlKeygroup], wavis: List[SwdlSampleInfoTblEntry],
            instrument_name: str, name: str, is_system=True
    ) -> Program:
        """
        Adds a sample provided as sample data from the master bank. If the sample data is NOT in the master bank,
        use add_sample manually instead.

        :param master_pcmd: Master bank PCMD data that contains sample data.
        :param prg: Program data
        :param kgrps: Keygroup of the program, one per split group in `prg`, in order.
        :param wavis: Sample information. Position and size of the sample are used and looked up in the master_pcmd.
                      One per split group in `prg`, in order.
                      WAVIS MUST BE FROM MAIN BANK FOR THIS FUNCTION.
        :param is_system: Whether to add to the system or user sample dir.
        :param name: Name that describes the preset
        :param instrument_name: Name of the instrument of the preset
        """
        samples = []
        for wavi in wavis:
            samples.append(
                self._extract_sample_from_master(master_pcmd, wavi.get_initial_sample_pos(), wavi.sample_length)
            )
        return self.add_sample(samples, prg, kgrps, wavis, instrument_name, name, is_system)

    def add_sample(
            self, sample_data: List[bytes], prg: SwdlProgramTable,
            kgrps: List[SwdlKeygroup], wavis: List[SwdlSampleInfoTblEntry],
            instrument_name: str, name: str, is_system=True
    ) -> Program:
        """
        Adds a sample provided as raw data
        :param sample_data: Sample data. Type is specified in the wavi. One per wavi, in order.
        :param prg: Program data
        :param kgrps: Keygroups of the program, one per split group in `prg`, in order.
        :param wavis: Sample information. Position and size of the sample are ignored (but loop begin is not!).
                     The provided sample data is used instead. Wavi also defines type of sample data encoding.
                     One per split group in `prg`, in order.
        :param is_system: Whether to add to the system or user sample dir.
        :param name: Name that describes the preset
        :param instrument_name: Name of the instrument of the preset
        :return:
        """
        prog = Program(
            instrument_name, name,
            sample_data, prg, kgrps, wavis
        )
        if is_system:
            self._source_system.append(prog)
        else:
            self._source_user.append(prog)
        return prog

    def get_all_from_swdl(self) -> List[Program]:
        return list(self._source_swdl_by_src_name.values())

    def get_all_from_swdl_by_filename(self) -> Dict[str, List[Program]]:
        return dict(self._source_swdl_by_file_name)

    def get_all_from_swdl_by_srcname(self) -> Dict[str, List[Program]]:
        return dict(self._source_swdl_by_src_name)

    def get_all_system(self) -> List[Program]:
        return list(self._source_system)

    def get_all_user(self) -> List[Program]:
        return list(self._source_user)

    def filter(self, *,
               instrument_name=None, name=None,
               original_swdl_filename=None, original_swdl_srcname=None,
               swdl=True, system=True, user=True
   ) -> List[Program]:
        """
        Return all programs matching the provided filters. Arguments with None as default can be strings for exact match
        or regex for regex based match.
        """
        raise NotImplementedError("filter is not implemented yet.")  # todo

    @staticmethod
    def _extract_sample_from_master(pcmd: SwdlPcmd, start: int, length: int):
        """Extracts a sample from the master bank."""
        return pcmd.chunk_data[start:start+length]
