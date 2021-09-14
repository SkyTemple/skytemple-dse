"""Converts Smdl models back into the binary format used by the game"""
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
from typing import List

from skytemple_dse.dse.smdl.model import Smdl, SmdlEvent, SmdlEventSpecial, SmdlEventPlayNote, SmdlEventPause
from skytemple_dse.util import *


class SmdlWriter:
    def __init__(self, model: Smdl):
        self.model = model
        self.data = None

    def write(self) -> bytes:
        data = bytearray(128)
        # Tracks
        for track in self.model.tracks:
            events = self._events_to_bytes(track.events)
            preamble = track.preamble.to_bytes()
            data += track.header.to_bytes(len(preamble) + len(events))
            data += preamble
            data += events
            # padding
            if len(data) % 4 != 0:
                data += bytes([0x98] * (4 - len(data) % 4))
        # EOC
        data += self.model.eoc.to_bytes()
        # Header 64 bytes
        data[0:64] = self.model.header.to_bytes(len(data))
        # Song header 64 bytes
        data[64:128] = self.model.song.to_bytes(len(self.model.tracks))

        return data

    def _events_to_bytes(self, events: List[SmdlEvent]):
        buffer = bytearray()
        for event in events:
            if isinstance(event, SmdlEventPlayNote):
                buffer.append(event.velocity)
                note = event.note.value
                octmod = event.octave_mod
                if event.key_down_duration > 0xFFFFFF:
                    raise ValueError("Key down duration too large to encode.")
                elif event.key_down_duration > 0xFFFF:
                    n_p = 3
                elif event.key_down_duration > 0xFF:
                    n_p = 2
                elif event.key_down_duration >= 0:
                    n_p = 1
                else:
                    n_p = 0
                note_data = note & 0xF
                note_data += ((octmod + 2) & 0x3) << 4
                note_data += (n_p & 0x3) << 6
                buffer.append(note_data)
                if n_p > 0:
                    i = int.to_bytes(event.key_down_duration, n_p, byteorder='big', signed=False)
                    assert len(i) == n_p
                    buffer += i
            elif isinstance(event, SmdlEventPause):
                buffer.append(event.value.value)
            elif isinstance(event, SmdlEventSpecial):
                buffer.append(event.op.value)
                for param in event.params:
                    if param > 0xFF or param < 0:
                        raise ValueError("An SMDL special event parameter must be unsigned 0-255.")
                    buffer.append(param)
            else:
                raise TypeError(f"Invalid event type: {type(event)}")
        return buffer
