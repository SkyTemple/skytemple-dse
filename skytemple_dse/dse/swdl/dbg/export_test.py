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
from tempfile import NamedTemporaryFile

from ndspy.rom import NintendoDSRom

# noinspection PyUnresolvedReferences
from skytemple_files.common.util import get_files_from_rom_with_extension

from skytemple_dse.dse.swdl.model import Swdl
from skytemple_dse.dse.swdl.wavi import SampleFormatConsts
from skytemple_dse.dse.swdl.writer import SwdlWriter
from skytemple_dse.ppmdu_adpcm import DecodeADPCM_NDS, Uint8Vector


def run(cmd):
    print(f'> {cmd}')
    os.system(f'{cmd} 2>&1')


base_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')
output_dir = os.path.join(os.path.dirname(__file__), 'dbg_output')
os.makedirs(output_dir, exist_ok=True)
rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy.nds'))

for filename in get_files_from_rom_with_extension(rom, 'swd'):
    if 'bgm' not in filename:
        continue
    print(filename)
    model_bytes = rom.getFileByName(filename)
    model = Swdl(model_bytes)
    assert model == Swdl(model_bytes)
    after_bytes = SwdlWriter(model).write()
    rom.setFileByName(filename, after_bytes)

    try:
        after = Swdl(after_bytes)
        assert model.header == after.header
        assert model.pcmd == after.pcmd
        assert model.prgi == after.prgi
        assert model.kgrp == after.kgrp
        assert model.wavi == after.wavi
        assert model == after
        #assert model_bytes == after_bytes
    except:
        with open('/tmp/before.bin', 'wb') as f:
            f.write(model_bytes)
        with open('/tmp/after.bin', 'wb') as f:
            f.write(after_bytes)
        os.system('xxd /tmp/before.bin > /tmp/before.bin.hex')
        os.system('xxd /tmp/after.bin > /tmp/after.bin.hex')
        raise

    for i, smpl in enumerate(model.wavi.sample_info_table):
        if smpl is not None and smpl.sample is not None:
            with NamedTemporaryFile(mode='wb') as f:
                if smpl.sample_format == SampleFormatConsts.ADPCM_4BIT:
                    bs = bytes(smpl.sample)
                    v = Uint8Vector(len(bs))
                    for vi in range(0, len(bs)):
                        v[vi] = bs[vi]
                    out = DecodeADPCM_NDS(v)
                    smplout = bytearray()
                    for vi in out:
                        vi: int
                        smplout += vi.to_bytes(2, byteorder='little', signed=True)
                else:
                    smplout = bytes(smpl.sample)
                f.write(smplout)
                f.flush()
                out_wavname = filename.replace('/', '_') + '_' + str(i) + '.wav'
                out_fname = os.path.join(output_dir, out_wavname)
                if smpl.sample_format == SampleFormatConsts.PCM_8BIT:
                    run(f'sox -t s8 -c 1 -r {smpl.sample_rate} -e signed-integer {f.name} -e signed-integer -b 16 {out_fname}')
                elif smpl.sample_format == SampleFormatConsts.PCM_16BIT or smpl.sample_format == SampleFormatConsts.ADPCM_4BIT:
                    run(f'sox -t s16 -c 1 -r {smpl.sample_rate} -e signed-integer {f.name} -e signed-integer -b 16 {out_fname}')
                else:
                    print(f"Unknown format: 0x{smpl.sample_format:0x}")
                os.makedirs(os.path.join(output_dir, 'raw'), exist_ok=True)
                with open(os.path.join(output_dir, 'raw', out_wavname + '.pcm'), 'wb') as fi:
                    fi.write(smplout)
                with open(os.path.join(output_dir, 'raw', out_wavname + '.pcm.samplerate.txt'), 'w') as fi:
                    fi.write(str(smpl.sample_rate))

rom.saveToFile(os.path.join(output_dir, 'out_swdl.nds'))
