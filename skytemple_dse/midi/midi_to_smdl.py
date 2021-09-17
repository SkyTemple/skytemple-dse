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
import re
from enum import Enum, auto
from typing import Tuple, List, Iterable, Optional

from mido import MidiFile, Message, MetaMessage
from mido.messages import BaseMessage

from skytemple_dse.dse.smdl.model import Smdl, SmdlTrack, SmdlEventPlayNote, SmdlEventSpecial, SmdlSpecialOpCode, \
    SmdlNote
PATTERN_MATCH_MARKER = re.compile(r'UNK 0x([0-9a-fA-F][0-9a-fA-F]?) (?:0x([0-9a-fA-F][0-9a-fA-F]?))?' + \
                                  ('(?: 0x([0-9a-fA-F][0-9a-fA-F]?))?' * 7) + ' ?')
EXPRESSION_DEFAULT = 113


class MidiExportState:
    def __init__(self):
        self.previous_tick = 0
        self.current_pause = 0
        self.current_octave = -1


class SmdlConvertWarningReason(Enum):
    NOT_IMPLEMENTED = auto()
    UNKNOWN_MARKER = auto()
    UNKNOWN_CONTROL = auto()
    HEADER_EVENTS_AUTOGEN = auto()
    SET_XPRESS_AUTOGEN = auto()


class SmdlConvertWarning:
    def __init__(
            self, track_id: int, message: Optional[BaseMessage], reason=SmdlConvertWarningReason.NOT_IMPLEMENTED
    ):
        self.track_id = track_id
        self.message = message
        self.reason = reason

    def __str__(self):
        if self.reason == SmdlConvertWarningReason.NOT_IMPLEMENTED:
            return f'Warning: Skipped importing a message: ' \
                   f'{type(self.message).__name__} type {self.message.type} not implemented.'
        if self.reason == SmdlConvertWarningReason.UNKNOWN_MARKER:
            return f'Warning: Skipped importing a message: ' \
                   f'Marker "{self.message.text}" has no representation.'
        if self.reason == SmdlConvertWarningReason.UNKNOWN_CONTROL:
            return f'Warning: Skipped importing a message: ' \
                   f'Control "{self.message.control}" has no representation.'
        if self.reason == SmdlConvertWarningReason.HEADER_EVENTS_AUTOGEN:
            return f'Warning: Automatically generated header set values.'  # todo better message?
        if self.reason == SmdlConvertWarningReason.SET_XPRESS_AUTOGEN:
            return f'Warning: Automatically generated expression set command as first message.'  # todo better message?


def _correct_octave(smdl_track: SmdlTrack, midi_note: int, s: MidiExportState):
    octave = midi_note // 12
    mods = [s.current_octave - 2, s.current_octave - 1, s.current_octave, s.current_octave + 1]
    if s.current_octave == -1 or octave not in mods:
        s.current_octave = octave
        smdl_track.events.append(SmdlEventSpecial(SmdlSpecialOpCode.SET_OCTAVE, params=[octave]))
        return 0
    return octave - s.current_octave


def _insert_pause(smdl_track: SmdlTrack, event: BaseMessage, s: MidiExportState):
    pause_in_ticks = event.abs_time - s.previous_tick
    #if pause_in_ticks > 0xFFFFFF:
    #    # TODO: We could technically still encode this.
    #    raise ValueError("The MIDI contains a VERY long pause, this is currently not supported.")
    #elif pause_in_ticks > 0xFFFF:
    #    params = list(int.to_bytes(pause_in_ticks, 3, byteorder='little', signed=False))
    #    smdl_track.events.append(SmdlEventSpecial(SmdlSpecialOpCode.WAIT_3BYTE, params=params))
    while pause_in_ticks > 0xFFFF:
        smdl_track.events.append(SmdlEventSpecial(SmdlSpecialOpCode.WAIT_2BYTE, params=[0xFF, 0xFF]))
        pause_in_ticks -= 0xFFFF
    if pause_in_ticks > 0xFF:
        params = list(int.to_bytes(pause_in_ticks, 2, byteorder='little', signed=False))
        smdl_track.events.append(SmdlEventSpecial(SmdlSpecialOpCode.WAIT_2BYTE, params=params))
    elif pause_in_ticks > 0:
        smdl_track.events.append(SmdlEventSpecial(SmdlSpecialOpCode.WAIT_1BYTE, params=[pause_in_ticks]))
    elif pause_in_ticks < 0:
        raise ValueError("Internal MIDI timing error.")

    s.previous_tick = event.abs_time


def _read_note(smdl_track: SmdlTrack, event_on: Message, event_off: Message, s: MidiExportState):
    hold_duration = event_off.abs_time - event_on.abs_time
    _insert_pause(smdl_track, event_on, s)
    octave_mod = _correct_octave(smdl_track, event_on.note, s)
    s.current_octave += octave_mod
    s.last_note_hold_time = hold_duration
    smdl_track.events.append(SmdlEventPlayNote(
        event_on.velocity, octave_mod, SmdlNote(event_on.note % 12), hold_duration
    ))


def _read_program_change(smdl_track: SmdlTrack, event: Message, s: MidiExportState):
    _insert_pause(smdl_track, event, s)
    smdl_track.events.append(SmdlEventSpecial(
        SmdlSpecialOpCode.SET_SAMPLE, params=[event.program]
    ))


def _read_control_change(smdl_track: SmdlTrack, event: Message, s: MidiExportState, warnings: List[SmdlConvertWarning]):
    _insert_pause(smdl_track, event, s)
    if event.control == 1:
        smdl_track.events.append(SmdlEventSpecial(
            SmdlSpecialOpCode.SET_MODU, params=[event.value]
        ))
    elif event.control == 7:
        smdl_track.events.append(SmdlEventSpecial(
            SmdlSpecialOpCode.SET_VOLUME, params=[event.value]
        ))
    elif event.control == 10:
        smdl_track.events.append(SmdlEventSpecial(
            SmdlSpecialOpCode.SET_PAN, params=[event.value]
        ))
    elif event.control == 11:
        smdl_track.events.append(SmdlEventSpecial(
            SmdlSpecialOpCode.SET_XPRESS, params=[event.value]
        ))
    else:
        warnings.append(SmdlConvertWarning(smdl_track.preamble.track_id, event, SmdlConvertWarningReason.UNKNOWN_CONTROL))


def _read_pitchwheel(smdl_track: SmdlTrack, event: Message, s: MidiExportState):
    _insert_pause(smdl_track, event, s)

    bend = event.pitch
    bend += (16384 // 2)
    bend <<= 2
    sh = (bend & 0xFF00) >> 8
    sl = bend & 0xFF

    smdl_track.events.append(SmdlEventSpecial(
        SmdlSpecialOpCode.SET_BEND, params=[sh, sl]
    ))


def _read_marker(smdl_track: SmdlTrack, event: MetaMessage, s: MidiExportState, warnings: List[SmdlConvertWarning]):
    _insert_pause(smdl_track, event, s)
    if 'loop' in event.text.lower() and event.text.lower() != 'loopstart':
        smdl_track.events.append(SmdlEventSpecial(
            SmdlSpecialOpCode.LOOP_POINT, params=[]
        ))
        return
    if event.text.startswith('HEADER1 '):
        val = int(event.text[8:])
        smdl_track.events.append(SmdlEventSpecial(
            SmdlSpecialOpCode.SET_HEADER1, params=[val]
        ))
        return
    if event.text.startswith('HEADER2 '):
        val = int(event.text[8:])
        smdl_track.events.append(SmdlEventSpecial(
            SmdlSpecialOpCode.SET_HEADER2, params=[val]
        ))
        return
    try:
        match = PATTERN_MATCH_MARKER.match(event.text)
        assert match
        groups = list(match.groups())
        groups.pop()
        op = int(groups.pop(0), 16)
        params = []
        if len(groups) > 0:
            g = groups.pop(0)
            while g is not None:
                params.append(int(g, 16))
                if len(groups) <= 0:
                    break
                g = groups.pop()
        smdl_track.events.append(SmdlEventSpecial(
            SmdlSpecialOpCode(op), params=params
        ))
    except:
        warnings.append(
            SmdlConvertWarning(smdl_track.preamble.track_id, event, SmdlConvertWarningReason.UNKNOWN_MARKER)
        )


def _read_end_of_track(smdl_track: SmdlTrack, event: MetaMessage, s: MidiExportState):
    _insert_pause(smdl_track, event, s)
    smdl_track.events.append(SmdlEventSpecial(
        SmdlSpecialOpCode.TRACK_END, params=[]
    ))


def _read_set_tempo(smdl_track: SmdlTrack, event: MetaMessage, s: MidiExportState):
    _insert_pause(smdl_track, event, s)
    smdl_track.events.append(SmdlEventSpecial(
        SmdlSpecialOpCode.SET_TEMPO, params=[60000000 // event.tempo]
    ))


def times_to_absolute(msgs: Iterable[BaseMessage]) -> List[BaseMessage]:
    l = []
    tick = 0
    for m in msgs:
        tick += m.time
        vars(m)['abs_time'] = tick
        l.append(m)
    return l


# TODO: Convert using Channels, not Tracks
def midi_to_smdl(midi: MidiFile, header1val, header2val) -> Tuple[Smdl, List[SmdlConvertWarning]]:
    smdl = Smdl.new(midi.filename.split('/')[-1][0:15])
    warnings = []

    free_channels = list(range(0, 16))
    max_channel = 0

    for track_id, track in enumerate(midi.tracks):
        # Assert, that all messages are on the same channel
        channel = -1
        track = times_to_absolute(track)
        for event in track:
            if channel == -1:
                if hasattr(event, 'channel'):
                    channel = event.channel
                    assert channel > -1
                    max_channel = max(max_channel, channel)
                else:
                    continue
            elif hasattr(event, 'channel') and event.channel != channel:
                raise ValueError("To convert a MIDI to an SMDL, all messages on the MIDI "
                                 "track must play on the same channel.")

        if channel == -1:
            channel = 0

        if channel not in free_channels:
            if channel == 0 and track_id == 1:
                # We allow duplicate channel 0 in this case
                pass
            else:
                if len(free_channels) < 1:
                    raise ValueError("The MIDI uses too many channels. Please limit to 16.")
                channel = free_channels.pop(0)
        else:
            free_channels.remove(channel)

        smdl_track = SmdlTrack.new(track_id, channel)
        smdl.tracks.append(smdl_track)

        s = MidiExportState()

        # Check if first message is setting expression, otherwise generate.
        if not isinstance(track[0], Message) or track[0].type != 'control_change' or track[0].control != 11:
            warnings.append(SmdlConvertWarning(track_id, None, SmdlConvertWarningReason.SET_XPRESS_AUTOGEN))
            m = Message('control_change', control=11, value=EXPRESSION_DEFAULT)
            vars(m)['abs_time'] = 0
            track.insert(0, m)

        for ei, event in enumerate(track):
            if isinstance(event, Message):
                if event.type == 'note_on':
                    # Look ahead for note_off
                    event_on = event
                    event_off = None
                    for evt in track[ei:]:
                        if isinstance(event, Message) and evt.type == 'note_off':
                            if evt.channel == event_on.channel \
                                    and evt.note == event_on.note:
                                event_off = evt
                                break
                    if event_off is None:
                        raise ValueError("Invalid MIDI. A played note was never released.")
                    _read_note(smdl_track, event_on, event_off, s)
                elif event.type == 'program_change':
                    _read_program_change(smdl_track, event, s)
                elif event.type == 'control_change':
                    _read_control_change(smdl_track, event, s, warnings)
                    if event.control == 11 and ei == 0 and track_id != 0:
                        # Look ahead. If first message, not first track and next message does
                        # not set HEADER1, auto generate
                        evt = track[ei + 1]
                        if not isinstance(evt, MetaMessage) or evt.type != 'marker' or not evt.text.startswith('HEADER1 '):
                            warnings.append(SmdlConvertWarning(track_id, None, SmdlConvertWarningReason.HEADER_EVENTS_AUTOGEN))
                            smdl_track.events.append(SmdlEventSpecial(
                                SmdlSpecialOpCode.SET_HEADER1, params=[header1val]
                            ))
                            smdl_track.events.append(SmdlEventSpecial(
                                SmdlSpecialOpCode.SET_HEADER2, params=[header2val]
                            ))
                elif event.type == 'pitchwheel':
                    _read_pitchwheel(smdl_track, event, s)
                elif event.type != 'note_off':
                    warnings.append(SmdlConvertWarning(track_id, event))
            elif isinstance(event, MetaMessage):
                if event.type == 'marker':
                    _read_marker(smdl_track, event, s, warnings)
                elif event.type == 'end_of_track':
                    _read_end_of_track(smdl_track, event, s)
                elif event.type == 'set_tempo':
                    _read_set_tempo(smdl_track, event, s)
                else:
                    warnings.append(SmdlConvertWarning(track_id, event))

    smdl.song.tpqn = midi.ticks_per_beat
    smdl.song.nbchans = max_channel + 1

    return smdl, warnings
