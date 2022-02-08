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
from typing import Optional, List

from skytemple_dse.dse.common import HasId
from skytemple_dse.dse.swdl.kgrp import SwdlKeygroup
from skytemple_dse.dse.swdl.model import Swdl
from skytemple_dse.dse.swdl.prgi import SwdlProgramTable
from skytemple_dse.dse.swdl.wavi import SwdlSampleInfoTblEntry
logger = logging.getLogger(__name__)


class Program:
    def __init__(
            self, instrument_name: Optional[str], name: Optional[str],
            sample_data: List[bytes], prg: SwdlProgramTable,
            kgrps: List[SwdlKeygroup], wavis: List[SwdlSampleInfoTblEntry],
            original_swdl_filename: Optional[str] = None, original_swdl_srcname: Optional[str] = None,
            original_swdl_program_id: Optional[int] = None
    ):
        self.original_swdl_srcname = original_swdl_srcname
        self.original_swdl_filename = original_swdl_filename
        self.wavis = wavis  # are usually expected to be the versions from the main bank, if applicable
        self.kgrps = kgrps
        self.prg = prg
        self.sample_data = sample_data
        self.name = name
        self.instrument_name = instrument_name
        self.original_swdl_program_id = original_swdl_program_id
        assert len(self.wavis) == len(self.sample_data) == len(self.kgrps) == len(self.prg.splits)

    def load_into_swdl(self, swdl: Swdl, main_bank_swdl: Swdl, program_id: int, allow_add_samples=True) -> bool:
        """Load this program into the provided SWDL.
        Try finding the original sample in the SWDL if it comes from there.
        If not possible the sample data is inserted into the main bank (unless allow_add_samples is False, in which case
        an exception is raised instead). Additionally if an exact match of a wavi is found, that one is used, instead
        of a new wavi being inserted into both the main bank and it's copy into the swdl. Keygroups are also checked if
        they already exist in the swdl, and are re-used if so.
        Returns whether the main bank swdl was modified."""

        modified = False
        logger.info(f'Importing a program into slot {program_id} in {swdl.header.file_name}.')

        # lookup wavis and create in main bank if needed
        wavi_ids = []
        for src_sample, src_wavi in zip(self.sample_data, self.wavis):
            wavi_id = self._lookup_list(src_wavi, main_bank_swdl.wavi.sample_info_table, ignore_id=True)
            if wavi_id is None:
                logger.warning(f'Had to create a new wavi.')
                wavi_id = self._create_new_wavi(main_bank_swdl, src_wavi)
                modified = True
            src_wavi.id = wavi_id
            wavi_ids.append(wavi_id)
            assert main_bank_swdl.wavi.sample_info_table[wavi_id].id == wavi_id
            # lookup samples in wavis and create in main bank if needed
            sample_start = self._lookup_bytes(src_sample, main_bank_swdl.pcmd.chunk_data)
            if sample_start is None:
                if not allow_add_samples:
                    raise ValueError("Sample not found in main bank.")
                logger.warning(f'Had to create a new sample.')
                sample_start = self._create_new_sample(main_bank_swdl, src_sample)
                modified = True
                main_bank_swdl.wavi.sample_info_table[wavi_id].force_set_sample_pos(sample_start)
            src_wavi.force_set_sample_pos(sample_start)
            #assert main_bank_swdl.wavi.sample_info_table[wavi_id] == src_wavi

        # lookup keygroups and create in swdl if needed
        kgrp_ids = []
        for src_kgrp in self.kgrps:
            kgrp_id = self._lookup_list(src_kgrp, swdl.kgrp.keygroups)
            if kgrp_id is None:
                logger.info(f'Had to create a new keygroup.')
                kgrp_id = self._create_new_keygroup(swdl, src_kgrp)
            src_kgrp.id = kgrp_id
            kgrp_ids.append(kgrp_id)
            assert swdl.kgrp.keygroups[kgrp_id] == src_kgrp

        # Collect all still used wavi IDs
        used_wavi_ids = []
        for prg_id, prg in enumerate(swdl.prgi.program_table):
            if prg_id != program_id and prg is not None:
                for split in prg.splits:
                    used_wavi_ids.append(split.sample_id)

        used_wavi_ids += wavi_ids

        # Copy program info and assign references to wavi and keygroupds
        while len(swdl.prgi.program_table) <= program_id:
            swdl.prgi.program_table.append(None)
        swdl.prgi.program_table[program_id] = self.prg.copy(wavi_ids, kgrp_ids)
        swdl.prgi.program_table[program_id].id = program_id

        # Copy and assign wavi
        # Wavi of original swdl must be cleared.
        # Then it needs to be re-filled with the original wavi entries, however the offsets start at 0 and then
        # increment with the lengths of the samples.
        cursor = 0
        swdl.wavi.sample_info_table = []
        for wavi in main_bank_swdl.wavi.sample_info_table:
            # Also deletes wavis that are now unused after assigning the new program.
            if wavi is not None:
                if wavi.id in used_wavi_ids:
                    remapped_wavi = wavi.copy(cursor)
                    cursor += remapped_wavi.sample_length
                    swdl.wavi.sample_info_table.append(remapped_wavi)
                else:
                    swdl.wavi.sample_info_table.append(None)
            else:
                swdl.wavi.sample_info_table.append(None)


        # TODO: Delete keygroups that are now unused after assigning the new program??

        return modified

    @staticmethod
    def _lookup_list(entry: HasId, lst: List[HasId], ignore_id=False) -> Optional[int]:
        for i, refentry in enumerate(lst):
            if refentry is not None:
                if ignore_id:
                    if refentry.equals_without_id(entry):
                        return i
                else:
                    if refentry == entry:
                        return i

    @staticmethod
    def _lookup_bytes(needle: bytes, haystack: bytes) -> Optional[int]:
        fresult = haystack.find(needle)
        return fresult if fresult >= 0 else None

    @staticmethod
    def _create_new_wavi(swdl: Swdl, wavi: SwdlSampleInfoTblEntry) -> int:
        swdl.wavi.sample_info_table.append(wavi)
        return len(swdl.wavi.sample_info_table) - 1

    @staticmethod
    def _create_new_sample(swdl: Swdl, sample: bytes) -> int:
        start = len(swdl.pcmd.chunk_data)
        swdl.pcmd.chunk_data += sample
        return start

    @staticmethod
    def _create_new_keygroup(swdl: Swdl, kgrp: SwdlKeygroup) -> int:
        swdl.kgrp.keygroups.append(kgrp)
        return len(swdl.kgrp.keygroups) - 1
