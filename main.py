from base84numbers import convert_84
from typing import TypedDict
from pathlib import Path
import pynbs
import argparse
from colors import *

INSTRUMENT_LOOKUP = {
    0: 1,
    1: 6,
    2: 6,
    3: 6,
    4: 6,
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

DRUMKIT_LOOKUP = {
    2: 2,
    3: 1,
    4: 5,
}


class MyInstrument(TypedDict):
    name: str
    instrument: int  # already looked up
    volume: int  # already in 0-13
    muted: bool
    notes: list[str]


def is_array_unique(array: list) -> bool:
    return len(set(array)) == 1


def round_volume(vol: int):
    if vol >= 50:
        return 100
    return 50


def get_mapped_instrument(instr: int):
    global unknown_found

    if instr not in INSTRUMENT_LOOKUP:
        unknown_found += 1
        return unknown_instrument
    return INSTRUMENT_LOOKUP[instr]


def transform_volume(vol: int):
    return max(round(vol / 100 * 13 * volume_factor), 1)


def get_or_create_first_free_layer(tick: int, instrument: int, volume: int):
    for instr in tracks:
        if (
            instr["instrument"] == instrument
            and instr["volume"] == volume
            and (len(instr["notes"]) <= tick or instr["notes"][tick] == " ")
        ):
            return instr

    instr: MyInstrument = {
        "instrument": instrument,
        "volume": volume,
        "muted": False,
        "name": "Converted layer " + str(len(tracks) + 1),
        "notes": [],
    }
    tracks.append(instr)
    return instr


def insert_note(instrument: MyInstrument, tick: int, note: int):
    global low_found
    global high_found

    while len(instrument["notes"]) <= tick:
        instrument["notes"].append(" ")

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
    "-m",
    "--monotone",
    action="store_true",
    help="Ignores the specified volumes and use always 100%% (use --volume to change that). Use when the results has too many tracks",
)
parser.add_argument(
    "-M",
    "--map",
    type=str,
    help='Assign a Minecraft Instrument a custom scratch instrument. Format: "1:15;3:17"',
)
parser.add_argument(
    "-d",
    "--no-drumkit",
    action="store_false",
    help="Don't convert certain instruments to a drumkit layer",
)
parser.add_argument(
    "-D",
    "--drumkit-map",
    type=str,
    help='Assign a Minecraft Instrument a custom scratch drum. Pitches can\'t be converted. Format: "1:15;3:17"',
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
monotone: bool = args.monotone
cut_off: int | None = args.limit
compress: bool = args.no_compression
unknown_instrument: int = args.unknown_instrument or 20
mapping: str | None = args.map
process_drumkit: bool = args.no_drumkit
drum_mapping: str | None = args.drumkit_map


def parse_mapping(map: str | None, target: dict[int, int], type: str = "instrument"):
    if not map:
        return
    for map in map.split(";"):
        mc, scr = map.split(":")
        if not (mc and scr):
            continue

        print(
            f"Mapped Minecraft instrument {mc} to Scratch {type} {scr} instead of {target[int(mc)]}"
        )
        target[int(mc)] = int(scr)


parse_mapping(mapping, INSTRUMENT_LOOKUP)
if process_drumkit:
    parse_mapping(drum_mapping, DRUMKIT_LOOKUP, "drum")

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
        layer = file.layers[note.layer]

        if layer.lock:
            continue

        l_volume = (layer.volume * note.velocity) // 100
        volume = round_volume(l_volume) if monotone else l_volume

        instrument = get_mapped_instrument(note.instrument)
        key = note.key - 3 + transpose_factor

        if process_drumkit and note.instrument in DRUMKIT_LOOKUP:
            instrument = 22
            key = DRUMKIT_LOOKUP[note.instrument]

        track = get_or_create_first_free_layer(
            tick, instrument, transform_volume(volume)
        )
        insert_note(track, tick, key)

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

if len(tracks) >= 100:
    print(
        Fore.MAGENTA
        + f"This song is using {len(tracks)} tracks, which could cause problems with Scratches Clone Limit"
        + Style.RESET_ALL
    )

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
if len(tracks) >= 100:
    print(
        Fore.BLUE
        + "Hint: To ignore the volume to save on tracks use -m | --monotone"
        + Style.RESET_ALL
    )

print(Fore.GREEN + "Saved at:", new_file_name)
print("Produced tracks: " + str(len(tracks)))

length = min(cut_off, file.header.song_length) if cut_off else file.header.song_length

print(
    f"Length: {length} notes / {round(length * (1 / file.header.tempo))} seconds"
    + Style.RESET_ALL
)
