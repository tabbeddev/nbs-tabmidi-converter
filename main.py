from typing import TypedDict
from pathlib import Path
import pynbs
import argparse

NUMBERS_LOOKUP = "0123456789abcdefghijklmnopqrstuvwxyzâĉêĝĥîĵôŝûŵŷẑáćéǵíjḱĺḿńóṕŕ!§%&/()=?{[]}+*-,.;:_#"
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


def get_mapped_instrument(instr: int):
    if instr > 15:
        return 0
    return INSTRUMENT_LOOKUP[instr]


def get_or_create_first_free_layer(tick: int, instrument: int, volume: int):
    for instr in tracks:
        if (
            instr["instrument"] == get_mapped_instrument(instrument)
            and instr["volume"] == round(volume / 100 * 13 * volume_factor)
            and (len(instr["notes"]) <= tick or instr["notes"][tick] == " ")
        ):
            return instr

    instr: MyInstrument = {
        "instrument": get_mapped_instrument(instrument),
        "volume": round(volume / 100 * 13 * volume_factor),
        "muted": False,
        "name": "Converted layer",
        "notes": [],
    }
    tracks.append(instr)
    return instr


def insert_note(instrument: MyInstrument, tick: int, key: int):
    while len(instrument["notes"]) <= tick:
        instrument["notes"].append(" ")
    note = key - 3 + transpose_factor

    if note > 83:
        print(f"Upper limit hit with {note} on tick {tick}")
        while note > 83:
            note -= 12

    if note < 12:
        print(f"Lower limit hit with {note} on tick {tick}")
        while note < 0:
            note += 12
    instrument["notes"][tick] = NUMBERS_LOOKUP[note]


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
    "-v",
    "--volume",
    type=float,
    help="Multiplies the volume by this factor. Use when the result is way too loud.",
)
parser.add_argument("path", type=Path, help="The nbs file to convert to")

args = parser.parse_args()
path: Path = args.path
transpose_factor: int = (args.transpose or 0) * 12
hold_time: float = args.hold or 0.25
volume_factor: float = args.volume or 1
cut_off: int | None = args.limit

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

output = f"{round(file.header.tempo * 15)}\\{str(hold_time).removeprefix('0')}$"
for inst in tracks:
    output += inst["name"]
    output += "|"
    output += NUMBERS_LOOKUP[int(inst["muted"])]
    output += NUMBERS_LOOKUP[int(inst["instrument"])]
    output += NUMBERS_LOOKUP[int(inst["volume"])]
    output += "".join(inst["notes"])
    output += "$"

new_file_name = path.name.rsplit(".nbs", 1)[0] + ".smid.txt"

with open(new_file_name, "w") as f:
    f.write(output)

print("Saved at:", new_file_name)
