from base84numbers import convert_84
from typing import TypedDict
from pathlib import Path
import pynbs
import argparse
from colors import *

INSTRUMENT_LOOKUP = {
    0: 1,
    1: 6,
    2: 6,  # TODO: replace with drumkit layer when it exists
    3: 6,  # TODO: replace with drumkit layer when it exists
    4: 6,  # TODO: replace with drumkit layer when it exists
    5: 4,
    6: 14,
    7: 19,
    8: 3,
    9: 7,
    10: 16,
    11: 8,
    12: 11,
    13: 10,
    14: 17,
    15: 2,
}


class MyInstrument(TypedDict):
    name: str
    instrument: int  # already looked up
    volume: int  # already in 0-13
    muted: bool
    notes: list[str]


def is_array_unique(array: list) -> bool:
    return len(set(array)) == 1


def get_mapped_instrument(instr: int):
    global unknown_found

    if instr > 15:
        unknown_found += 1
        return unknown_instrument
    return INSTRUMENT_LOOKUP[instr]


def transform_volume(vol: int):
    return max(round(vol / 100 * 13 * volume_factor), 1)


def get_or_create_first_free_layer(tick: int, instrument: int, volume: int):
    for instr in tracks:
        if (
            instr["instrument"] == get_mapped_instrument(instrument)
            and instr["volume"] == transform_volume(volume)
            and (len(instr["notes"]) <= tick or instr["notes"][tick] == " ")
        ):
            return instr

    instr: MyInstrument = {
        "instrument": get_mapped_instrument(instrument),
        "volume": transform_volume(volume),
        "muted": False,
        "name": "Converted layer " + str(len(tracks) + 1),
        "notes": [],
    }
    tracks.append(instr)
    return instr


def insert_note(instrument: MyInstrument, tick: int, key: int):
    global low_found
    global high_found

    while len(instrument["notes"]) <= tick:
        instrument["notes"].append(" ")
    note = key - 3 + transpose_factor

    if note > 83:
        high_found += 1
        while note > 83:
            note -= 12

    if note < 12:
        low_found += 1
        while note < 0:
            note += 12
    instrument["notes"][tick] = convert_84(note)


tracks: list[MyInstrument] = []

parser = argparse.ArgumentParser(
    prog="./main.py",
    description="A simple converter from nbs files to my scratch music format",
)
parser.add_argument(
    "-t",
    "--transpose",
    type=int,
    help="The number to transpose the song by. There's an upper (83) and lower (0) limit",
)
parser.add_argument(
    "-o",
    "--hold",
    type=float,
    help="The length of a single note. Defaults to 0.25 scratch beats on tempo 60",
)
parser.add_argument(
    "-l",
    "--limit",
    type=int,
    help="Cut off the song prematurely at tick x. Use when the song wouldn't fit fully in the editor",
)
parser.add_argument(
    "-u",
    "--unknown-instrument",
    type=int,
    help="Assign custom instruments a scratch instrument. Default is 20",
)
parser.add_argument(
    "-v",
    "--volume",
    type=float,
    help="Multiplies the volume by this factor. Use when the result is way too loud",
)
parser.add_argument(
    "-C",
    "--no-compression",
    action="store_false",
    default=True,
    help="Skips compression. Generally not recommended",
)
parser.add_argument("path", type=Path, help="The nbs file to convert to")

args = parser.parse_args()
path: Path = args.path
transpose_factor: int = (args.transpose or 0) * 12
hold_time: float = args.hold or 0.25
volume_factor: float = args.volume or 1
cut_off: int | None = args.limit
compress: bool = args.no_compression
unknown_instrument: int = args.unknown_instrument or 20

unknown_found = 0
low_found = 0
high_found = 0

file = pynbs.read(path)

for tick, chord in file:
    tick: int = tick

    if cut_off and tick > cut_off:
        print("Cut off at", tick)
        break

    chord: list[pynbs.Note] = chord

    for note in chord:
        inst = get_or_create_first_free_layer(
            tick, note.instrument, file.layers[note.layer].volume
        )
        insert_note(inst, tick, note.key)

output = f"{round(file.header.tempo * 15)}\\{hold_time}$"
for inst in tracks:
    output += inst["name"]
    output += "|"
    output += convert_84(int(inst["muted"]))
    output += convert_84(int(inst["instrument"]))
    output += convert_84(int(inst["volume"]))

    notes = inst["notes"]
    if compress:
        while notes:
            val = notes[0]
            count = 0

            while notes and notes[0] == val:
                count += 1
                notes.pop(0)

            if count < 5:
                output += count * val
            else:
                count84 = convert_84(count)
                output += f"'{count84}~{val}"
    else:
        output += "".join(notes)

    output += "$"

new_file_name = path.name.rsplit(".nbs", 1)[0] + ".smid.txt"

with open(new_file_name, "w") as f:
    f.write(output)

if unknown_found:
    print(
        Fore.YELLOW
        + f"{unknown_found} notes were using an custom instrument. Those have been replaced with the Scratch instrument number {unknown_instrument}"
        + Style.RESET_ALL
    )

if low_found:
    print(
        Fore.YELLOW
        + f"{low_found} notes were outside the lower limit. Those have been transposed up individually, which might sound off"
        + Style.RESET_ALL
    )

if high_found:
    print(
        Fore.YELLOW
        + f"{high_found} notes were outside the upper limit. Those have been transposed down individually, which might sound off"
        + Style.RESET_ALL
    )

if low_found or high_found:
    print(
        Fore.BLUE
        + "Hint: To transpose the full song use -t | --transpose"
        + Style.RESET_ALL
    )

print(Fore.GREEN + "Saved at:", new_file_name)
print("Produced tracks: " + str(len(tracks)))

length = min(cut_off, file.header.song_length) if cut_off else file.header.song_length

print(
    f"Length: {length} notes / {round(length * (1 / file.header.tempo))} seconds"
    + Style.RESET_ALL
)
