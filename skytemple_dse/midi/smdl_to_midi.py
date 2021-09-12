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
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

from skytemple_dse.dse.smdl.model import *


def smdl_note_to_midi(note: SmdlNote, current_octave: int, octave_mod: int):
    base = 60
    octave_mod -= 2
    return note.value + base + ((octave_mod + current_octave) * 12)


def smdl_to_midi(smdl: Smdl) -> MidiFile:
    # i have no idea what i'm doing. let's go!!!
    current_octave = 0
    last_pause_time = 0
    tick = 0
    mid = MidiFile()
    for track in smdl.tracks:
        midi_track = MidiTrack()
        mid.tracks.append(midi_track)
        for event in track.events:
            if isinstance(event, SmdlEventPlayNote):
                # TODO: ??? What if not specified?
                held_time = event.key_down_duration if event.key_down_duration is not None else 0
                note = smdl_note_to_midi(event.note, current_octave, event.octave_mod)
                midi_track.append(Message('note_on', note=note, velocity=event.velocity, time=tick))
                tick += held_time
                midi_track.append(Message('note_off', note=note, velocity=event.velocity, time=tick))
            elif isinstance(event, SmdlEventPause):
                last_pause_time = event.value.length
                tick += last_pause_time
            elif isinstance(event, SmdlEventSpecial):
                if event.op == SmdlSpecialOpCode.REPEAT_LAST_PAUSE:
                    tick += last_pause_time
                elif event.op == SmdlSpecialOpCode.ADD_TO_LAST_PAUSE:
                    last_pause_time += event.params[0]
                    tick += last_pause_time
                elif event.op == SmdlSpecialOpCode.PAUSE8_BITS \
                        or event.op == SmdlSpecialOpCode.PAUSE16_BITS \
                        or event.op == SmdlSpecialOpCode.PAUSE24_BITS:
                    last_pause_time = event.params[0]
                    tick += last_pause_time
                elif event.op == SmdlSpecialOpCode.PAUSE_UNTIL_RELEASE:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.END_OF_TRACK:
                    midi_track.append(MetaMessage('end_of_track'))
                elif event.op == SmdlSpecialOpCode.LOOP_POINT:
                    # todo
                    midi_track.append(MetaMessage('marker', text='loop'))
                elif event.op == SmdlSpecialOpCode.UNK_0x9C:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0x9D:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0x9E:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.SET_TRACK_OCTAVE:
                    current_octave = event.params[0]
                elif event.op == SmdlSpecialOpCode.ADD_TO_TRACK_OCTAVE:
                    current_octave += event.params[0]
                elif event.op == SmdlSpecialOpCode.SET_TEMPO or event.op == SmdlSpecialOpCode.SET_TEMPO2:
                    midi_track.append(MetaMessage('set_tempo', tempo=bpm2tempo(event.params[0])))
                elif event.op == SmdlSpecialOpCode.UNK_0xA8:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.SET_UNK1:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.SET_UNK2:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.SKIP_NEXT_BYTE:
                    raise ValueError("Meta opcode should not exist.")
                elif event.op == SmdlSpecialOpCode.SET_PROGRAM:
                    midi_track.append(Message('program_change', program=event.params[0], time=tick))
                elif event.op == SmdlSpecialOpCode.UNK_0xAF:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xB0:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xB1:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xB2:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xB3:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xB4:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xB5:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xB6:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xBC:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.SET_MODULATION:
                    midi_track.append(Message('control_change', control=1, value=event.params[0], time=tick))
                elif event.op == SmdlSpecialOpCode.UNK_0xBF:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xC0:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xC3:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.SKIP_NEXT2_BYTES:
                    raise ValueError("Meta opcode should not exist.")
                elif event.op == SmdlSpecialOpCode.UNK_0xD0:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xD1:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xD2:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xD3:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xD4:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xD5:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xD6:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.PITCH_BEND:
                    # TODO
                    warnings.warn(f'Not implemented: {event.op}')
                    continue
                    midi_track.append(Message('pitchwheel', pitch=event.params[0], time=tick))
                elif event.op == SmdlSpecialOpCode.UNK_0xD8:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xDB:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xDC:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xDD:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xDF:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.SET_TRACK_VOLUME:
                    midi_track.append(Message('control_change', control=7, value=event.params[0], time=tick))
                elif event.op == SmdlSpecialOpCode.UNK_0xE1:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xE2:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.SET_TRACK_EXPRESSION:
                    midi_track.append(Message('control_change', control=11, value=event.params[0], time=tick))
                elif event.op == SmdlSpecialOpCode.UNK_0xE4:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xE5:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xE7:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.SET_TRACK_PAN:
                    midi_track.append(Message('control_change', control=10, value=event.params[0], time=tick))
                elif event.op == SmdlSpecialOpCode.UNK_0xE9:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xEA:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xEC:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xED:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xEF:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xF0:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xF1:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xF2:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xF3:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.UNK_0xF6:
                    # todo
                    warnings.warn(f'Not implemented: {event.op}')
                elif event.op == SmdlSpecialOpCode.SKIP_NEXT2_BYTES2:
                    raise ValueError("Meta opcode should not exist.")
                else:
                    raise ValueError(f"Invalid code: {event.op}")

    return mid
