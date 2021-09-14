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
SMDL_VERSION = 1045


class SmdlHeader(DseAutoString):
    def __init__(self, data: Optional[Union[bytes, memoryview]], *, filename: str = None):
        if not data:
            self.version = SMDL_VERSION
            self.unk1 = 65  # UNKNOWN!!
            self.unk2 = 121  # UNKNOWN!! 110~130 seems to be very common
            self.modified_date = DseDate.now()
            self.file_name = DseFilenameString(filename)
            self.unk5 = 1  # UNKNOWN!! Usual value.
            self.unk6 = 1  # UNKNOWN!! Usual value.
            self.unk8 = 0xFFFFFFFF  # UNKNOWN!! Usual value.
            self.unk9 = 0xFFFFFFFF  # UNKNOWN!! Usual value.
            return
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

    @classmethod
    def new(cls, filename: str):
        return SmdlHeader(None, filename=filename)

    def to_bytes(self, file_byte_length: int) -> bytes:
        buffer = bytearray(64)
        buffer[:4] = b'smdl'
        dse_write_uintle(buffer, file_byte_length, 0x08, 4)
        dse_write_uintle(buffer, self.version, 0x0C, 2)
        dse_write_uintle(buffer, self.unk1, 0x0E, 1)
        dse_write_uintle(buffer, self.unk2, 0x0F, 1)
        buffer[0x18:0x20] = self.modified_date.to_bytes()
        buffer[0x20:0x30] = self.file_name.to_bytes()
        dse_write_uintle(buffer, self.unk5, 0x30, 4)
        dse_write_uintle(buffer, self.unk6, 0x34, 4)
        dse_write_uintle(buffer, self.unk8, 0x38, 4)
        dse_write_uintle(buffer, self.unk9, 0x3C, 4)
        return buffer


class SmdlSong(DseAutoString):
    def __init__(self, data: Optional[Union[bytes, memoryview]]):
        if data is None:
            self.unk1 = 16777216  # UNKNOWN!! Usual value.
            self.unk2 = 0xFF10  # UNKNOWN!! Usual value.
            self.unk3 = 0xFFFFFFB0  # UNKNOWN!! Usual value.
            self.unk4 = 0x1  # UNKNOWN!! Usual value.
            self.tpqn = 48
            self.unk5 = 0xFF01  # UNKNOWN!! Usual value
            self.nbchans = 0  # needs to be initialized later!
            self.unk6 = 0x0F000000  # UNKNOWN!! Usual value
            self.unk7 = 0xFFFFFFFF  # UNKNOWN!! Usual value
            self.unk8 = 0x40000000  # UNKNOWN!! Usual value
            self.unk9 = 0x00404000  # UNKNOWN!! Usual value
            self.unk10 = 0x0200  # UNKNOWN!! Usual value
            self.unk11 = 0x0800  # UNKNOWN!! Usual value
            self.unk12 = 0xFFFFFF00  # UNKNOWN!! Usual value
            return
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

    @classmethod
    def new(cls):
        return SmdlSong(None)

    def to_bytes(self, number_tracks: int) -> bytes:
        buffer = bytearray(64)
        buffer[:4] = b'song'
        dse_write_uintle(buffer, self.unk1, 0x04, 4)
        dse_write_uintle(buffer, self.unk2, 0x08, 4)
        dse_write_uintle(buffer, self.unk3, 0x0C, 4)
        dse_write_uintle(buffer, self.unk4, 0x10, 2)
        dse_write_uintle(buffer, self.tpqn, 0x12, 2)
        dse_write_uintle(buffer, self.unk5, 0x14, 2)
        dse_write_uintle(buffer, number_tracks, 0x16, 1)
        dse_write_uintle(buffer, self.nbchans, 0x17, 1)
        dse_write_uintle(buffer, self.unk6, 0x18, 4)
        dse_write_uintle(buffer, self.unk7, 0x1C, 4)
        dse_write_uintle(buffer, self.unk8, 0x20, 4)
        dse_write_uintle(buffer, self.unk9, 0x24, 4)
        dse_write_uintle(buffer, self.unk10, 0x28, 2)
        dse_write_uintle(buffer, self.unk11, 0x2A, 2)
        dse_write_uintle(buffer, self.unk12, 0x2C, 4)
        buffer[0x30:0x40] = bytes([0xFF] * 16)
        return buffer


class SmdlEoc(DseAutoString):
    def __init__(self, data: Optional[Union[bytes, memoryview]]):
        if data is None:
            self.param1 = 16777216  # UNKNOWN!! Usual value
            self.param2 = 65284  # UNKNOWN!! Usual value
            return
        assert data[0:4] == b'eoc\x20', "Data is not valid SMDL"
        self.param1 = dse_read_uintle(data, 0x04, 4)
        self.param2 = dse_read_uintle(data, 0x08, 4)
        assert dse_read_uintle(data, 0x0C, 4) == 0

    @classmethod
    def new(cls):
        return SmdlEoc(None)

    def to_bytes(self) -> bytes:
        buffer = bytearray(16)
        buffer[:4] = b'eoc\x20'
        dse_write_uintle(buffer, self.param1, 0x4, 4)
        dse_write_uintle(buffer, self.param2, 0x8, 4)
        return buffer


class SmdlTrackHeader(DseAutoString):
    def __init__(self, data: Optional[Union[bytes, memoryview]]):
        if data is None:
            self.param1 = 16777216  # UNKNOWN!! Value often used.
            self.param2 = 65284  # UNKNOWN!! Value often used.
            return
        assert data[0:4] == b'trk\x20', "Data is not valid SMDL"
        self.param1 = dse_read_uintle(data, 0x4, 4)
        self.param2 = dse_read_uintle(data, 0x8, 4)
        self._len = dse_read_uintle(data, 0xC, 4)

    def get_initial_length(self):
        return self._len

    @classmethod
    def new(cls):
        return SmdlTrackHeader(None)

    def to_bytes(self, track_len: int) -> bytes:
        buffer = bytearray(16)
        buffer[:4] = b'trk\x20'
        dse_write_uintle(buffer, self.param1, 0x4, 4)
        dse_write_uintle(buffer, self.param2, 0x8, 4)
        dse_write_uintle(buffer, track_len, 0xC, 4)
        return buffer


class SmdlTrackPreamble(DseAutoString):
    def __init__(self, data: Optional[Union[bytes, memoryview]], *, track_id=None, channel_id=None):
        if data is None:
            self.track_id = track_id
            self.channel_id = channel_id
            self.unk1 = 0  # Unknown!! Value often used.
            self.unk2 = 0  # Unknown!! Value often used.
            return
        self.track_id = dse_read_uintle(data, 0)
        self.channel_id = dse_read_uintle(data, 1)
        self.unk1 = dse_read_uintle(data, 2)
        self.unk2 = dse_read_uintle(data, 3)

    @classmethod
    def new(cls, track_id, channel_id):
        return SmdlTrackPreamble(None, track_id=track_id, channel_id=channel_id)

    def to_bytes(self) -> bytes:
        buffer = bytearray(4)
        dse_write_uintle(buffer, self.track_id, 0x0)
        dse_write_uintle(buffer, self.channel_id, 0x1)
        dse_write_uintle(buffer, self.unk1, 0x2)
        dse_write_uintle(buffer, self.unk2, 0x3)
        return buffer


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

    def __str__(self):
        return f"PLAY_NOTE: {self.note.value} oct {self.octave_mod} at v{self.velocity} for {self.key_down_duration}"


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

    def __str__(self):
        return f"DELTA_TIME: {self.value.length} ticks"


class SmdlSpecialOpCode(Enum):
    WAIT_AGAIN = 0x90, 0
    WAIT_ADD = 0x91, 1
    WAIT_1BYTE = 0x92, 1
    WAIT_2BYTE = 0x93, 2  # LE
    WAIT_3BYTE = 0x94, 2  # LE
    TRACK_END = 0x98, 0
    LOOP_POINT = 0x99, 0
    SET_OCTAVE = 0xA0, 1
    SET_TEMPO = 0xA4, 1
    SET_HEADER1 = 0xA9, 1
    SET_HEADER2 = 0xAA, 1
    SET_SAMPLE = 0xAC, 1
    SET_MODU = 0xBE, 1
    SET_BEND = 0xD7, 2
    SET_VOLUME = 0xE0, 1
    SET_XPRESS = 0xE3, 1
    SET_PAN = 0xE8, 1
    NA_NOTE = 0x00, -1
    NA_DELTATIME = 0x80, 1
    UNK_9C = 0x9C, 1
    UNK_9D = 0x9D, 0
    UNK_A8 = 0xA8, 2
    UNK_B2 = 0xB2, 1
    UNK_B4 = 0xB4, 2
    UNK_B5 = 0xB5, 1
    UNK_BF = 0xBF, 1
    UNK_C0 = 0xC0, 0
    UNK_D0 = 0xD0, 1
    UNK_D1 = 0xD1, 1
    UNK_D2 = 0xD2, 1
    UNK_D4 = 0xD4, 3
    UNK_D6 = 0xD6, 2
    UNK_DB = 0xDB, 1
    UNK_DC = 0xDC, 5
    UNK_E2 = 0xE2, 3
    UNK_EA = 0xEA, 3
    UNK_F6 = 0xF6, 1

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(
            self, _: str, parameters: int
    ):
        # Number of parameters
        self.parameters = parameters


class SmdlEventSpecial(DseAutoString):
    def __init__(self, op: SmdlSpecialOpCode, params: List[int]):
        self.op = op
        self.params = params
        
    def __str__(self):
        amt = 0
        if len(self.params) >= 1:
            amt = self.params[0]

        if self.op == SmdlSpecialOpCode.SET_BEND:
            amt |= ((self.params[1] & 0xFF) << 8)
            # amt = (int)((short)amt)
            return f"PITCH_BEND: {amt} cents"
        elif self.op == SmdlSpecialOpCode.SET_MODU:
            return f"SET_MOD: {amt}"
        elif self.op == SmdlSpecialOpCode.SET_OCTAVE:
            return f"SET_OCTAVE: {amt}"
        elif self.op == SmdlSpecialOpCode.SET_PAN:
            return f"SET_PAN: 0x{amt:02x}"
        elif self.op == SmdlSpecialOpCode.SET_SAMPLE:
            return f"CHANGE_PROGRAM: {amt}"
        elif self.op == SmdlSpecialOpCode.SET_TEMPO:
            return f"CHANGE_TEMPO: {amt} bpm"
        elif self.op == SmdlSpecialOpCode.SET_VOLUME:
            return f"SET_VOLUME: {amt}"
        elif self.op == SmdlSpecialOpCode.SET_XPRESS:
            return f"SET_EXPRESSION: {amt}"
        elif self.op == SmdlSpecialOpCode.WAIT_1BYTE:
            return f"WAIT_1BYTE: {amt} ticks"
        elif self.op == SmdlSpecialOpCode.WAIT_2BYTE:
            amt |= ((self.params[1] & 0xFF) << 8)
            return f"WAIT_2BYTE: {amt} ticks"
        elif self.op == SmdlSpecialOpCode.WAIT_3BYTE:
            amt |= ((self.params[2] & 0xFF) << 16)
            amt |= (self.params[1] & 0xFF) << 8
            return f"WAIT_2BYTE: {amt} ticks"
        else:
            return self.op.name


SmdlEvent = Union[SmdlEventSpecial, SmdlEventPause, SmdlEventPlayNote]


class SmdlTrack(DseAutoString):
    def __init__(
            self, header: SmdlTrackHeader, data: Optional[Union[bytes, memoryview]],
            *, preamble: SmdlTrackPreamble = None
    ):
        self.header = header
        self.events: List[SmdlEvent] = []
        if data is None:
            self.preamble = preamble
            return
        self.preamble = SmdlTrackPreamble(data)
        length = header.get_initial_length()

        pnt = 4

        while pnt < length:
            op_code = dse_read_uintle(data, pnt)
            pnt += 1
            if op_code <= SmdlEventPlayNote.MAX:
                velocity = op_code
                param1 = dse_read_uintle(data, pnt)
                pnt += 1
                number_params = (param1 >> 6) & 0x3
                octave_mod = ((param1 >> 4) & 0x3) - 2
                note = param1 & 0xF
                #assert note < 0xC
                assert number_params < 4
                key_down_duration = -1
                if number_params > 0:
                    # todo: big endian?? really??
                    key_down_duration = dse_read_uintbe(data, pnt, number_params)
                pnt += number_params
                self.events.append(SmdlEventPlayNote(velocity, octave_mod, SmdlNote(note), key_down_duration))
            elif op_code <= SmdlEventPause.MAX:
                self.events.append(SmdlEventPause(SmdlPause(op_code)))
            elif op_code == 0xAB:  # skip byte
                pnt += 1
            elif op_code == 0xCB or op_code == 0xF8:  # skip 2 bytes
                pnt += 2
            else:
                op_code = SmdlSpecialOpCode(op_code)
                params = []
                for i in range(0, op_code.parameters):
                    params.append(dse_read_uintle(data, pnt))
                    pnt += 1

                self.events.append(SmdlEventSpecial(op_code, params))

            if pnt > length:
                raise ValueError("Tried to read past EOF while reading SMDL track data")

        # Padding
        padding_needed = (4 - (length % 4))
        if 0 < padding_needed < 4:
            for i in range(length, length + padding_needed):
                assert dse_read_uintle(data, i) == SmdlSpecialOpCode.TRACK_END.value

    @classmethod
    def new(cls, track_id, channel_id):
        return cls(
            SmdlTrackHeader.new(),
            None,
            preamble=SmdlTrackPreamble.new(track_id, channel_id)
        )


class Smdl:
    def __init__(self, data: Optional[bytes], *, header: SmdlHeader = None, song: SmdlSong = None, eoc: SmdlEoc = None):
        if data is None:
            self.header = header
            self.song = song
            self.tracks = []
            self.eoc = eoc
            return

        if not isinstance(data, memoryview):
            data = memoryview(data)

        self.header = SmdlHeader(data)
        self.song = SmdlSong(data[64:])

        self.tracks = []
        pnt = 128
        for i in range(0, self.song.get_initial_track_count()):
            assert pnt % 4 == 0
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

    @classmethod
    def new(cls, filename: str):
        return cls(
            None, header=SmdlHeader.new(filename), song=SmdlSong.new(), eoc=SmdlEoc.new()
        )
