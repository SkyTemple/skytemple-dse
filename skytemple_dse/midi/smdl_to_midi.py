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
from typing import Tuple, Dict, Iterable

from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from mido.messages import BaseMessage

from skytemple_dse.dse.smdl.model import *
LOOP_POINT = "Loop Point"


class MidiWriteState:
    def __init__(self, channel: int):
        self.tick_current = 0
        self.oct_current = 0
        self.last_note_len = 0
        self.last_wait_time = 0
        self.channel = channel


def smdl_note_to_midi(note: SmdlNote, octave: int):
    m_note = note.value + (octave * 12)
    # Right now just clips values. Probably should have a more elegant way to handle.
    if m_note < 0:
        return 0
    if m_note > 127:
        return 127
    return m_note


class TimedContainer:
    """mido uses relative timings... SMDL doesn't work like this. This container stores them absolutely and then
    returns them as messages in relative order, with relative time attributes."""
    def __init__(self):
        self.container: Dict[int, List[BaseMessage]] = {}

    def append(self, time: int, message: BaseMessage):
        if time not in self.container:
            self.container[time] = []
        self.container[time].append(message)

    def __iter__(self) -> Iterable[BaseMessage]:
        prev_time = 0
        for time, msgs in sorted(self.container.items(), key=lambda item: item[0]):
            first = msgs.pop(0)
            first.time = time - prev_time
            prev_time += first.time
            yield first
            for msg in msgs:
                msg.time = 0
                yield msg


def _read_note(event: SmdlEventPlayNote, track: TimedContainer, state: MidiWriteState):
    midi_note = smdl_note_to_midi(event.note, state.oct_current + event.octave_mod)
    n_length = event.key_down_duration
    if n_length < 0:
        n_length = state.last_note_len
    off_time = state.tick_current + n_length
    track.append(state.tick_current, Message('note_on', note=midi_note, channel=state.channel, velocity=event.velocity))
    track.append(off_time, Message('note_off', note=midi_note, channel=state.channel, velocity=event.velocity))

    state.oct_current = state.oct_current + event.octave_mod
    state.last_note_len = n_length


def _read_delta_time(event: SmdlEventPause, state: MidiWriteState):
    state.tick_current += event.value.length


def _read_loop_point_event(track: TimedContainer, state: MidiWriteState):
    track.append(state.tick_current, MetaMessage('marker', text='loop'))


def _read_pitch_bend_set(event: SmdlEventSpecial, track: TimedContainer, state: MidiWriteState):
    chan = state.channel
    sh = event.params[0]
    sl = event.params[1]
    bend = ((sh << 8) | sl) >> 2
    bend -= 16384 // 2
    track.append(state.tick_current, Message('pitchwheel', pitch=bend, channel=chan))


def _read_mod_wheel_change(event: SmdlEventSpecial, track: TimedContainer, state: MidiWriteState):
    track.append(state.tick_current, Message('control_change', control=1, value=event.params[0], channel=state.channel))


def _read_octave_set(event: SmdlEventSpecial, state: MidiWriteState):
    state.oct_current = event.params[0]


def _read_pan_change(event: SmdlEventSpecial, track: TimedContainer, state: MidiWriteState):
    track.append(state.tick_current, Message('control_change', control=10, value=event.params[0], channel=state.channel))


def _read_program_change(event: SmdlEventSpecial, track: TimedContainer, state: MidiWriteState):
    track.append(state.tick_current, Message('program_change', program=event.params[0], channel=state.channel))


def _read_tempo_set(event: SmdlEventSpecial, track: TimedContainer, state: MidiWriteState):
    mspq = 60000000 // event.params[0]
    track.append(state.tick_current, MetaMessage('set_tempo', tempo=mspq))


def _read_volume_set(event: SmdlEventSpecial, track: TimedContainer, state: MidiWriteState):
    track.append(state.tick_current, Message('control_change', control=7, value=event.params[0], channel=state.channel))


def _read_expression_set(event: SmdlEventSpecial, track: TimedContainer, state: MidiWriteState):
    track.append(state.tick_current, Message('control_change', control=11, value=event.params[0], channel=state.channel))


def _read_track_end_event(track: TimedContainer,  state: MidiWriteState):
    track.append(state.tick_current, MetaMessage('end_of_track'))


def _read_wait_event(event: SmdlEventSpecial, track: TimedContainer, state: MidiWriteState):
    if event.op == SmdlSpecialOpCode.WAIT_1BYTE:
        wait_time = event.params[0]
    elif event.op == SmdlSpecialOpCode.WAIT_2BYTE:
        wait_time = event.params[1]
        wait_time <<= 8
        wait_time |= event.params[0] & 0xFF
    elif event.op == SmdlSpecialOpCode.WAIT_3BYTE:
        wait_time = event.params[2]
        wait_time <<= 8
        wait_time = event.params[1]
        wait_time <<= 8
        wait_time |= event.params[0] & 0xFF
    elif event.op == SmdlSpecialOpCode.WAIT_ADD:
        wait_time = state.last_wait_time + event.params[0]
    elif event.op == SmdlSpecialOpCode.WAIT_AGAIN:
        wait_time = state.last_wait_time

    state.tick_current += wait_time
    state.last_wait_time = wait_time


def _read_unknown_event(event: SmdlEventSpecial, track: TimedContainer, state: MidiWriteState):
    params = ""
    for p in event.params:
        params += f"0x{p:02x} "
    track.append(state.tick_current, MetaMessage('marker', text=f'UNK 0x{event.op.value:02x} {params}'))


def _read_header_event(event: SmdlEventSpecial, track: TimedContainer, state: MidiWriteState):
    i = 2 if event.op == SmdlSpecialOpCode.SET_HEADER2 else 1
    track.append(state.tick_current, MetaMessage('marker', text=f'HEADER{i} {event.params[0]}'))


def smdl_to_midi(smdl: Smdl) -> MidiFile:
    mid = MidiFile(ticks_per_beat=smdl.song.tpqn)
    mid.filename = smdl.header.file_name
    for track in smdl.tracks:
        midi_track = MidiTrack()
        timed_track = TimedContainer()
        state = MidiWriteState(track.preamble.channel_id)
        mid.tracks.append(midi_track)
        for event in track.events:
            if isinstance(event, SmdlEventPlayNote):
                _read_note(event, timed_track, state)
            elif isinstance(event, SmdlEventPause):
                _read_delta_time(event, state)
            elif isinstance(event, SmdlEventSpecial):
                if event.op == SmdlSpecialOpCode.LOOP_POINT:
                    _read_loop_point_event(timed_track, state)
                elif event.op == SmdlSpecialOpCode.SET_BEND:
                    _read_pitch_bend_set(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.SET_MODU:
                    _read_mod_wheel_change(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.SET_OCTAVE:
                    _read_octave_set(event, state)
                elif event.op == SmdlSpecialOpCode.SET_PAN:
                    _read_pan_change(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.SET_SAMPLE:
                    _read_program_change(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.SET_TEMPO:
                    _read_tempo_set(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.SET_VOLUME:
                    _read_volume_set(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.SET_XPRESS:
                    _read_expression_set(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.TRACK_END:
                    _read_track_end_event(timed_track, state)
                elif event.op == SmdlSpecialOpCode.WAIT_1BYTE:
                    _read_wait_event(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.WAIT_2BYTE:
                    _read_wait_event(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.WAIT_3BYTE:
                    _read_wait_event(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.WAIT_ADD:
                    _read_wait_event(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.WAIT_AGAIN:
                    _read_wait_event(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.SET_HEADER1:
                    _read_header_event(event, timed_track, state)
                elif event.op == SmdlSpecialOpCode.SET_HEADER2:
                    _read_header_event(event, timed_track, state)
                else:
                    _read_unknown_event(event, timed_track, state)

        for entry in timed_track:
            midi_track.append(entry)

    return mid
