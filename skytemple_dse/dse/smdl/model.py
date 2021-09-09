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
import warnings
from enum import Enum
from typing import Union, List, Optional

from skytemple_dse.dse.common.date import DseDate
from skytemple_dse.dse.common.string import DseFilenameString
from skytemple_dse.util import *


class SmdlHeader(DseAutoString):
    def __init__(self, data: Union[bytes, memoryview]):
        assert data[0:4] == b'smdl', "Data is not valid SMDL"
        assert data[4:8] == bytes(4), "Data is not valid SMDL"
        self._in_length = dse_read_uintle(data, 0x08, 4)
        assert len(data) == self._in_length, "Data is not valid SMDL"
        self.version = dse_read_uintle(data, 0x0C, 2)
        self.unk1 = dse_read_uintle(data, 0x0E, 1)
        self.unk2 = dse_read_uintle(data, 0x0F, 1)
        assert data[0x10:0x18] == bytes(8), "Data is not valid SMDL"
        self.modified_date = DseDate.from_bytes(data[0x18:0x20])
        self.file_name = DseFilenameString.from_bytes(data[0x20:0x30])
        self.unk5 = dse_read_uintle(data, 0x30, 4)
        self.unk6 = dse_read_uintle(data, 0x34, 4)
        self.unk8 = dse_read_uintle(data, 0x38, 4)
        self.unk9 = dse_read_uintle(data, 0x3C, 4)


class SmdlSong(DseAutoString):
    def __init__(self, data: Union[bytes, memoryview]):
        assert data[0:4] == b'song', "Data is not valid SMDL"
        self.unk1 = dse_read_uintle(data, 0x04, 4)
        self.unk2 = dse_read_uintle(data, 0x08, 4)
        self.unk3 = dse_read_uintle(data, 0x0C, 4)
        self.unk4 = dse_read_uintle(data, 0x10, 2)
        # Ticks Per Quarter Note? Usually 0x30 or 48 ticks per quarter note. (Works like MIDI clock ticks it seems.)
        # Or possibly just the tick rate..
        self.tpqn = dse_read_uintle(data, 0x12, 2)
        self.unk5 = dse_read_uintle(data, 0x14, 2)
        self._nbtrks = dse_read_uintle(data, 0x16, 1)
        self.nbchans = dse_read_uintle(data, 0x17, 1)
        self.unk6 = dse_read_uintle(data, 0x18, 4)
        self.unk7 = dse_read_uintle(data, 0x1C, 4)
        self.unk8 = dse_read_uintle(data, 0x20, 4)
        self.unk9 = dse_read_uintle(data, 0x24, 4)
        self.unk10 = dse_read_uintle(data, 0x28, 2)
        self.unk11 = dse_read_uintle(data, 0x2A, 2)
        self.unk12 = dse_read_uintle(data, 0x2C, 4)
        assert data[0x30:0x40] == bytes([0xFF] * 16), "Data is not valid SMDL"

    def get_initial_track_count(self):
        return self._nbtrks


class SmdlEoc(DseAutoString):
    def __init__(self, data: Union[bytes, memoryview]):
        assert data[0:4] == b'eoc\x20', "Data is not valid SMDL"
        self.param1 = dse_read_uintle(data, 0x04, 4)
        self.param2 = dse_read_uintle(data, 0x08, 4)
        assert dse_read_uintle(data, 0x0C, 4) == 0

    def get_initial_track_count(self):
        return self._nbtrks


class SmdlTrackHeader(DseAutoString):
    def __init__(self, data: Union[bytes, memoryview]):
        assert data[0:4] == b'trk\x20', "Data is not valid SMDL"
        self.param1 = dse_read_uintle(data, 0x4, 4)
        self.param2 = dse_read_uintle(data, 0x8, 4)
        self._len = dse_read_uintle(data, 0xC, 4)

    def get_initial_length(self):
        return self._len


class SmdlTrackPreamble(DseAutoString):
    def __init__(self, data: Union[bytes, memoryview]):
        self.track_id = dse_read_uintle(data, 0)
        self.channel_id = dse_read_uintle(data, 1)
        self.unk1 = dse_read_uintle(data, 2)
        self.unk2 = dse_read_uintle(data, 3)


class SmdlNote(Enum):
    C  = 0x0
    CS = 0x1
    D  = 0x2
    DS = 0x3
    E  = 0x4
    F  = 0x5
    FS = 0x6
    G  = 0x7
    GS = 0x8
    A  = 0x9
    AS = 0xA
    B  = 0xB
    INVALID_C = 0xC
    INVALID_D = 0xD
    INVALID_E = 0xE
    UNK = 0xF


class SmdlEventPlayNote(DseAutoString):
    MAX = 0x7F

    def __init__(self, velocity: int, octave_mod: int, note: SmdlNote, key_down_duration: Optional[int]):
        self.velocity = velocity
        self.octave_mod = octave_mod
        self.note = note
        self.key_down_duration = key_down_duration


class SmdlPause(Enum):
    HALF_NOTE = 0x80, 96
    DOTTED_QUARTER_NOTE = 0x81, 72
    X2_3_OF_HALF_NOTE = 0x82, 64
    QUARTER_NOTE = 0x83, 48
    DOTTED_EIGHT_NOTE = 0x84, 36
    X2_3_OF_QUARTER_NOTE = 0x85, 32
    EIGTH_NOTE = 0x86, 24
    DOTTED_SIXTEENTH_NOTE = 0x87, 18
    X2_3_OF_EIGTH_NOTE = 0x88, 16
    SIXTEENTH_NOTE = 0x89, 12
    DOTTED_THRITYSECOND_NOTE = 0x8A, 9
    X2_3_OF_SIXTEENTH_NOTE = 0x8B, 8
    THRITYSECOND_NOTE = 0x8C, 6
    DOTTED_SIXTYFORTH_NOTE = 0x8D, 4
    X2_3_OF_THRITYSECOND_NOTE = 0x8E, 3
    SIXTYFORTH_NOTE = 0x8F, 2

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(
            self, _: str, length: int
    ):
        # in ticks
        self.length = length


class SmdlEventPause(DseAutoString):
    MAX = 0x8F

    def __init__(self, value: SmdlPause):
        self.value = value


class SmdlSpecialOpCode(Enum):
    # Params: -
    # Pause the track processing for the duration of the last pause.(Includes fixed duration pauses)
    REPEAT_LAST_PAUSE = 0x90, []
    # Params: (uint8)Duration
    # Pause the track processing for the duration of the last pause + the duration in ticks specified.
    # (Includes fixed duration pauses)
    ADD_TO_LAST_PAUSE = 0x91, [8]
    # Params: (uint8)Duration
    # Pause the track processing for the duration in ticks.
    PAUSE8_BITS = 0x92, [8]
    # Params: (uint16)Duration
    # Pause the track processing for the duration in ticks.
    PAUSE16_BITS = 0x93, [16]
    # Params: (uint24)Duration
    # Pause the track processing for the duration in ticks.
    PAUSE24_BITS = 0x94, [24]
    # Params: (uint8)CheckInterval
    # Pause the track processing as long as a note is held down. Will wait for at least "CheckInterval" ticks,
    # then checks every "CheckInterval" ticks if all notes have been released on the current track.
    PAUSE_UNTIL_RELEASE = 0x95, [8]
    # Params: -
    # Disable current track.
    INVALID_0x96 = 0x96, []
    # Params: -
    # Disable current track.
    INVALID_0x97 = 0x97, []
    # Params: -
    # Marks the end of the track. Is also used as padding to align the end of the track on 4 bytes.
    END_OF_TRACK = 0x98, []
    # Params: -
    # Marks the point the track will loop to after the end of track is reached.
    LOOP_POINT = 0x99, []
    # Params: -
    # Disable current track.
    INVALID_0x9A = 0x9A, []
    # Params: -
    # Disable current track.
    INVALID_0x9B = 0x9B, []
    # Params: ??
    # ??
    UNK_0x9C = 0x9C, [8]
    # Params: ??
    # ??
    UNK_0x9D = 0x9D, None
    # Params: ??
    # ??
    UNK_0x9E = 0x9E, []
    # Params: -
    # Disable current track.
    INVALID_0x9F = 0x9F, []
    # Params: (uint8)Octave
    # Sets the current track's octave to the value specified. Valid range is 0 - 9.
    SET_TRACK_OCTAVE = 0xA0, [8]
    # Params: (uint8)Octave
    # Adds the value specified to the current track octave.
    ADD_TO_TRACK_OCTAVE = 0xA1, [8]
    # Params: -
    # Disable current track.
    INVALID_0xA2 = 0xA2, []
    # Params: -
    # Disable current track.
    INVALID_0xA3 = 0xA3, []
    # Params: (uint8)TempoBPM
    # Sets the track's tempo in beats per minute.
    SET_TEMPO = 0xA4, [8]
    # Params: (uint8)TempoBPM
    # Sets the track's tempo in beats per minute? (The code is identical to 0xA4)
    SET_TEMPO2 = 0xA5, [8]
    # Params: -
    # Disable current track.
    INVALID_0xA6 = 0xA6, []
    # Params: -
    # Disable current track.
    INVALID_0xA7 = 0xA7, []
    # Params: ??
    # ??
    UNK_0xA8 = 0xA8, [8, 8]
    # Params: (uint8)???
    # Set that first unknown value from the track's header
    SET_UNK1 = 0xA9, [8]
    # Params: (uint8)???
    # Set that first unknown value from the track's header
    SET_UNK2 = 0xAA, [8]
    # Params: -
    # Skips the next byte in the track.
    SKIP_NEXT_BYTE = 0xAB, []
    # Params: (uint8)ProgramID
    # Change the track's program(Instrument Preset) to the one specified.
    SET_PROGRAM = 0xAC, [8]
    # Params: -
    # Disable current track.
    INVALID_0xAD = 0xAD, []
    # Params: -
    # Disable current track.
    INVALID_0xAE = 0xAE, []
    # Params: ??
    # ??
    UNK_0xAF = 0xAF, None
    # Params: ??
    # ??
    UNK_0xB0 = 0xB0, []
    # Params: ??
    # ??
    UNK_0xB1 = 0xB1, [8]
    # Params: ??
    # ??
    UNK_0xB2 = 0xB2, None
    # Params: ??
    # Params: ??
    # ??
    UNK_0xB3 = 0xB3, None
    # Params: ??
    # ??
    UNK_0xB4 = 0xB4, [8, 8]
    # Params: ??
    # ??
    UNK_0xB5 = 0xB5, None
    # Params: ??
    # ??
    UNK_0xB6 = 0xB6, None
    # Params: -
    # Disable current track.
    INVALID_0xB7 = 0xB7, []
    # Params: -
    # Disable current track.
    INVALID_0xB8 = 0xB8, []
    # Params: -
    # Disable current track.
    INVALID_0xB9 = 0xB9, []
    # Params: -
    # Disable current track.
    INVALID_0xBA = 0xBA, []
    # Params: -
    # Disable current track.
    INVALID_0xBB = 0xBB, []
    # Params: ??
    # ??
    UNK_0xBC = 0xBC, [8]
    # Params: -
    # Disable current track.
    INVALID_0xBD = 0xBD, []
    # Params: ??
    # ??
    SET_MODULATION = 0xBE, [8]
    # Params: ??
    # ??
    UNK_0xBF = 0xBF, [8]
    # Params: ??
    # ??
    UNK_0xC0 = 0xC0, []
    # Params: -
    # Disable current track.
    INVALID_0xC1 = 0xC1, []
    # Params: -
    # Disable current track.
    INVALID_0xC2 = 0xC2, []
    # Params: ??
    # ??
    UNK_0xC3 = 0xC3, None
    # Params: -
    # Disable current track.
    INVALID_0xC4 = 0xC4, []
    # Params: -
    # Disable current track.
    INVALID_0xC5 = 0xC5, []
    # Params: -
    # Disable current track.
    INVALID_0xC6 = 0xC6, []
    # Params: -
    # Disable current track.
    INVALID_0xC7 = 0xC7, []
    # Params: -
    # Disable current track.
    INVALID_0xC8 = 0xC8, []
    # Params: -
    # Disable current track.
    INVALID_0xC9 = 0xC9, []
    # Params: -
    # Disable current track.
    INVALID_0xCA = 0xCA, []
    # Params: -
    # Skip the next 2 bytes in the track.
    SKIP_NEXT2_BYTES = 0xCB, []
    # Params: -
    # Disable current track.
    INVALID_0xCC = 0xCC, []
    # Params: -
    # Disable current track.
    INVALID_0xCD = 0xCD, []
    # Params: -
    # Disable current track.
    INVALID_0xCE = 0xCE, []
    # Params: -
    # Disable current track.
    INVALID_0xCF = 0xCF, []
    # Params: ??
    # ??
    UNK_0xD0 = 0xD0, [8]
    # Params: ??
    # ??
    UNK_0xD1 = 0xD1, [8]
    # Params: ??
    # ??
    UNK_0xD2 = 0xD2, [8]
    # Params: ??
    # ??
    UNK_0xD3 = 0xD3, [8, 8]
    # Params: ??
    # ??
    UNK_0xD4 = 0xD4, [8, 8, 8]
    # Params: ??
    # ??
    UNK_0xD5 = 0xD5, [8, 8]
    # Params: ??
    # ??
    UNK_0xD6 = 0xD6, [8, 8]
    # Params: (uint16)Bend
    # Bend the pitch of the note.
    PITCH_BEND = 0xD7, [16]
    # Params: ??
    # ??
    UNK_0xD8 = 0xD8, [8, 8]
    # Params: -
    # Disable current track.
    INVALID_0xD9 = 0xD9, []
    # Params: -
    # Disable current track.
    INVALID_0xDA = 0xDA, []
    # Params: ??
    # ??
    UNK_0xDB = 0xDB, [8]
    # Params: ??
    # ??
    UNK_0xDC = 0xDC, [8, 8, 8, 8, 8]  # ???
    # Params: ??
    # ??
    UNK_0xDD = 0xDD, None
    # Params: -
    # Disable current track.
    INVALID_0xDE = 0xDE, []
    # Params: ??
    # ??
    UNK_0xDF = 0xDF, [8]
    # Params: (int8)TrackVolume
    # Change the track's volume to the value specified. (0x0-0x7F)
    SET_TRACK_VOLUME = 0xE0, [8]
    # Params: ??
    # ??
    UNK_0xE1 = 0xE1, [8]
    # Params: ??
    # ??
    UNK_0xE2 = 0xE2, None
    # Params: (int8)TrackExpression
    # Change the track's expression(secondary volume) to the value specified. (0x0-0x7F)
    SET_TRACK_EXPRESSION = 0xE3, [8]
    # Params: ??
    # ??
    UNK_0xE4 = 0xE4, [8, 8, 8, 8, 8]  # ???
    # Params: ??
    # ??
    UNK_0xE5 = 0xE5, None
    # Params: -
    # Disable current track.
    INVALID_0xE6 = 0xE6, []
    # Params: ??
    # ??
    UNK_0xE7 = 0xE7, [8]
    # Params: (int8)Pan
    # Change the track's pan to the value specified. (0x0-0x7F. 0x40 is middle, 0x0 full left, and 0x7F full right )
    SET_TRACK_PAN = 0xE8, [8]
    # Params: ??
    # ??
    UNK_0xE9 = 0xE9, None
    # Params: ??
    # ??
    UNK_0xEA = 0xEA, None
    # Params: -
    # Disable current track.
    INVALID_0xEB = 0xEB, []
    # Params: ??
    # ??
    UNK_0xEC = 0xEC, [8, 8, 8, 8, 8]  # TODO: ???
    # Params: ??
    # ??
    UNK_0xED = 0xED, None
    # Params: -
    # Disable current track.
    INVALID_0xEE = 0xEE, []
    # Params: ??
    # ??
    UNK_0xEF = 0xEF, None
    # Params: ??
    # ??
    UNK_0xF0 = 0xF0, [8, 8, 8, 8, 8]  # TODO: ???
    # Params: ??
    # ??
    UNK_0xF1 = 0xF1, None
    # Params: ??
    # ??
    UNK_0xF2 = 0xF2, None
    # Params: ??
    # ??
    UNK_0xF3 = 0xF3, None
    # Params: -
    # Disable current track.
    INVALID_0xF4 = 0xF4, []
    # Params: -
    # Disable current track.
    INVALID_0xF5 = 0xF5, []
    # Params: ??
    # ??
    UNK_0xF6 = 0xF6, [8]
    # Params: -
    # Disable current track.
    INVALID_0xF7 = 0xF7, []
    # Params: -
    # Skips the next 2 bytes in the track.
    SKIP_NEXT2_BYTES2 = 0xF8, []
    # Params: -
    # Disable current track.
    INVALID_0xF9 = 0xF9, []
    # Params: -
    # Disable current track.
    INVALID_0xFA = 0xFA, []
    # Params: -
    # Disable current track.
    INVALID_0xFB = 0xFB, []
    # Params: -
    # Disable current track.
    INVALID_0xFC = 0xFC, []
    # Params: -
    # Disable current track.
    INVALID_0xFD = 0xFD, []
    # Params: -
    # Disable current track.
    INVALID_0xFE = 0xFE, []
    # Params: -
    # Disable current track.
    INVALID_0xFF = 0xFF, []

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(
            self, _: str, parameters: Optional[List[int]]
    ):
        # List of parameters, number represents bit length (8, 16, 32). If negative: signed
        # If the object is None instead: Unknown OP
        self.parameters = parameters


class SmdlEventSpecial(DseAutoString):
    def __init__(self, op: SmdlSpecialOpCode, params: List[int]):
        self.op = op
        self.params = params


SmdlEvent = Union[SmdlEventSpecial, SmdlEventPause, SmdlEventPlayNote]


class SmdlTrack(DseAutoString):
    def __init__(self, header: SmdlTrackHeader, data: Union[bytes, memoryview]):
        self.header = header
        self.preamble = SmdlTrackPreamble(data)
        length = header.get_initial_length()

        self.events: List[SmdlEvent] = []
        pnt = 4

        while pnt < length:
            op_code = dse_read_uintle(data, pnt)
            pnt += 1
            if op_code <= SmdlEventPlayNote.MAX:
                velocity = op_code
                pnt += 1
                param1 = dse_read_uintle(data, pnt)
                pnt += 1
                number_params = param1 >> 6
                octave_mod = param1 >> 4 & 0x3
                note = param1 & 0xF
                key_down_duration = None
                if number_params > 0:
                    key_down_duration = dse_read_uintle(data, pnt, number_params)
                pnt += number_params
                self.events.append(SmdlEventPlayNote(velocity, octave_mod, SmdlNote(note), key_down_duration))
            elif op_code <= SmdlEventPause.MAX:
                self.events.append(SmdlEventPause(SmdlPause(op_code)))
            else:
                op_code = SmdlSpecialOpCode(op_code)
                if op_code == SmdlSpecialOpCode.SKIP_NEXT_BYTE:
                    pnt += 1
                    continue
                elif op_code == SmdlSpecialOpCode.SKIP_NEXT2_BYTES or op_code == SmdlSpecialOpCode.SKIP_NEXT2_BYTES2:
                    pnt += 2
                    continue
                elif op_code.parameters is None:
                    warnings.warn(f"SMDL: Unknown operation: {op_code}")
                    self.events.append(SmdlEventSpecial(op_code, []))
                else:
                    params = []
                    for param_length in op_code.parameters:
                        param_length //= 8
                        params.append(dse_read_uintle(data, pnt, param_length))
                        pnt += param_length

                    self.events.append(SmdlEventSpecial(op_code, params))

            if pnt > length:
                raise ValueError("Tried to read past EOF while reading SMDL track data")

        assert isinstance(self.events[len(self.events) - 1], SmdlEventSpecial) and \
               self.events[len(self.events) - 1].op == SmdlSpecialOpCode.END_OF_TRACK

        # Padding
        padding_needed = (4 - (length % 4))
        if 0 < padding_needed < 4:
            for i in range(length, length + padding_needed):
                assert dse_read_uintle(data, i) == SmdlSpecialOpCode.END_OF_TRACK.value


class Smdl:
    def __init__(self, data: bytes):
        if not isinstance(data, memoryview):
            data = memoryview(data)

        self.header = SmdlHeader(data)
        self.song = SmdlSong(data[64:])

        self.tracks = []
        pnt = 128
        for i in range(0, self.song.get_initial_track_count()):
            assert pnt <= len(data), "Data is not valid SMDL"

            track_header = SmdlTrackHeader(data[pnt:])

            pnt += 16
            assert pnt + track_header.get_initial_length() <= len(data), "Data is not valid SMDL"
            self.tracks.append(SmdlTrack(track_header, data[pnt:]))
            mod = 4 - (track_header.get_initial_length() % 4)
            if mod == 4:
                mod = 0
            pnt += track_header.get_initial_length() + mod

        self.eoc = SmdlEoc(data[pnt:])
