import random
from enum import IntEnum, Enum, auto
from typing import List, Union, Tuple, BinaryIO


class MIDIWritingError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NoteLength(IntEnum):
    WHOLE = 0x8f00
    HALF = 0x8740
    QUARTER = 0x8360
    EIGHTH = 0x8170
    SIXTEENTH = 0x7880
    TH32 = 0x3C80
    TH64 = 0x1E80


class NoteValue(IntEnum):
    A = 0x39
    As = Bf = 0x3A
    B = Cf = 0x3B
    Bs = C = 0x3C
    Cs = Df = 0x3D
    D = 0x3E
    Ds = Ef = 0x3F
    E = Ff = 0x40
    F = Es = 0x41
    Fs = Gf = 0x42
    G = 0x43
    Gs = Af = 0x44


class Interval(Enum):
    UNISON = auto()
    MINOR_SECOND = auto()
    MAJOR_SECOND = auto()
    MINOR_THIRD = auto()
    MAJOR_THIRD = auto()
    PERFECT_FOURTH = auto()
    AUGMENTED_FOURTH = DIMINISHED_FIFTH = auto()
    PERFECT_FIFTH = auto()
    MINOR_SIXTH = auto()
    MAJOR_SIXTH = auto()
    MINOR_SEVENTH = auto()
    MAJOR_SEVENTH = auto()
    OCTAVE = auto()


class Scale(Enum):
    NATURAL_MINOR_SCALE = [Interval.UNISON, Interval.MAJOR_SECOND, Interval.MINOR_THIRD, Interval.PERFECT_FOURTH,
                           Interval.PERFECT_FIFTH, Interval.MINOR_SIXTH, Interval.MINOR_SEVENTH, Interval.OCTAVE]
    HARMONIC_MINOR_SCALE = [Interval.UNISON, Interval.MAJOR_SECOND, Interval.MINOR_THIRD, Interval.PERFECT_FOURTH,
                            Interval.PERFECT_FIFTH, Interval.MINOR_SIXTH, Interval.MAJOR_SEVENTH, Interval.OCTAVE]
    MAJOR_SCALE = [Interval.UNISON, Interval.MAJOR_SECOND, Interval.MAJOR_THIRD, Interval.PERFECT_FOURTH,
                   Interval.PERFECT_FIFTH, Interval.MAJOR_SIXTH, Interval.MAJOR_SEVENTH, Interval.OCTAVE]

    MINOR_PENTATONIC_SCALE = [Interval.UNISON, Interval.MINOR_THIRD, Interval.PERFECT_FOURTH, Interval.PERFECT_FIFTH,
                              Interval.MINOR_SEVENTH]

    MAJOR_PENTATONIC_SCALE = [Interval.UNISON, Interval.MAJOR_SECOND, Interval.MAJOR_THIRD, Interval.PERFECT_FIFTH,
                              Interval.MAJOR_SIXTH]


class Note:
    def __init__(self, note: NoteValue):
        self.value = note

    def get_minor_second(self) -> int:
        return self.value + 1

    def get_major_second(self) -> int:
        return self.value + 2

    def get_minor_third(self) -> int:
        return self.value + 3

    def get_major_third(self) -> int:
        return self.value + 4

    def get_perfect_fourth(self) -> int:
        return self.value + 5

    def get_diminished_fifth(self) -> int:
        return self.value + 6

    def get_augmented_fourth(self) -> int:
        return self.get_diminished_fifth()

    def get_perfect_fifth(self) -> int:
        return self.value + 7

    def get_minor_sixth(self) -> int:
        return self.value + 8

    def get_major_sixth(self) -> int:
        return self.value + 9

    def get_minor_seventh(self) -> int:
        return self.value + 10

    def get_major_seventh(self) -> int:
        return self.value + 11

    def get_perfect_octave(self) -> int:
        return self.value + 12

    def get_relative_note(self, interval: Interval) -> int:
        if interval == Interval.MINOR_SECOND:
            return self.get_minor_second()
        elif interval == Interval.MAJOR_SECOND:
            return self.get_major_second()
        elif interval == Interval.MINOR_THIRD:
            return self.get_minor_third()
        elif interval == Interval.MAJOR_THIRD:
            return self.get_major_third()
        elif interval == Interval.PERFECT_FOURTH:
            return self.get_perfect_fourth()
        elif interval == Interval.AUGMENTED_FOURTH:
            return self.get_augmented_fourth()
        elif interval == Interval.PERFECT_FIFTH:
            return self.get_perfect_fifth()
        elif interval == Interval.MINOR_SIXTH:
            return self.get_minor_sixth()
        elif interval == Interval.MAJOR_SIXTH:
            return self.get_major_sixth()
        elif interval == Interval.MINOR_SEVENTH:
            return self.get_minor_seventh()
        elif interval == Interval.MAJOR_SEVENTH:
            return self.get_major_seventh()
        elif interval == Interval.OCTAVE:
            return self.get_perfect_octave()
        elif interval == Interval.UNISON:
            return self.value.value


class Riff:
    def __init__(self, scale: Scale = None, root: NoteValue = None, number_notes: int = None,
                 allowed_rhythm: List[NoteLength] = None):

        self.number_notes = random.randint(1, 16) if not number_notes else number_notes

        if not scale or not root:
            self.allowed_notes: List[int] = [note.value for note in NoteValue]
        else:
            note = Note(root)
            self.allowed_notes: List[int] = [note.get_relative_note(interval) for interval in scale.value]

        self.rhythm_allowed: List[NoteLength] = [value for value in NoteLength] if not allowed_rhythm else \
            allowed_rhythm
        self.notes: Union[List[Tuple[int, int]], None] = None

    def populate(self):
        self.notes = [(random.choice(self.allowed_notes), random.choice(self.rhythm_allowed))
                      for x in range(self.number_notes)]

    def size(self) -> int:
        return len(self.notes) * 8


def write(riff: Riff, file: BinaryIO):
    write_mthd(file)
    write_mtrk(riff, file)
    # write_useless_mtrk(file)


def write_mthd(file: BinaryIO):
    res = file.write(bytes([0x4d, 0x54, 0x68, 0x64, 0x00, 0x00, 0x00, 0x06, 0x00, 0x01, 0x00, 0x01, 0x01, 0xe0]))
    if res != 14:
        raise MIDIWritingError("Error when writing MTHD chunk! Wrote {} bytes instead of 14".format(res))


def write_mtrk(riff: Riff, file: BinaryIO):
    # MTRK identifier
    written = file.write(bytes([0x4d, 0x54, 0x72, 0x6b]))
    if written != 4:
        raise MIDIWritingError("Error when writing MTRK identifier! Wrote {} bytes instead of 4".format(written))

    # Size of the riff
    written = file.write(riff.size().to_bytes(4, 'big'))
    if written != 4:
        raise MIDIWritingError("Error when writing MTRK data size! Wrote {} bytes instead of 4".format(written))

    for note in riff.notes:
        written = file.write(bytes([0x00]))
        written += file.write(bytes([0x90]))
        written += file.write(bytes([note[0]]))
        written += file.write(bytes([0x40]))
        written += file.write(note[1].to_bytes(2, 'big'))
        written += file.write(bytes([note[0]]))
        written += file.write(bytes([0x00]))
        if written != 8:
            raise MIDIWritingError("Error on writing note {}. Wrote {} bytes instead of 8".format(bytes([note[0]]),
                                                                                                  written))

    # End of main track
    written = file.write(bytes([0x01, 0xff, 0x2f, 0x00]))
    if written != 4:
        raise MIDIWritingError("Error when writing MTRK end! Wrote {} bytes instead of 4".format(written))


def write_useless_mtrk(file: BinaryIO):
    written = file.write(bytes([0x4d, 0x54, 0x72, 0x6b, 0x00, 0x00, 0x00, 0x0b, 0x00, 0xff, 0x03, 0x00, 0x00, 0xc0,
                                0x00, 0x00, 0xff, 0x2f, 0x00, 0x00]))
    if written != 20:
        raise MIDIWritingError("Error when writing useless MTRK! Wrote {} bytes instead of 20".format(written))
