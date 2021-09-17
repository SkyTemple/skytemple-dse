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
from mido import MidiFile

#mid = MidiFile('/tmp/B_SYS_P3_OPENIN.mid')
mid = MidiFile('/home/marco/dev/skytemple/skytemple/dse/skytemple_dse/midi/dbg/dbg_output/SOUND_BGM_bgm0001.smd.mid')

for track in mid.tracks:
    print("TRACK")
    for m in track:
        print(m)
