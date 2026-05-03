# NBS to Scratch TabMidi

A small program to convert NBS songs to the format for my [Scratch-based MIDI-Editor](https://scratch.mit.edu/projects/1311570943/).

## "Disclaimer"

Technically it can convert Rush E, but the song can't be imported in the Scratch Player, as it hits the max character limit in Ask-Blocks.

## Usage

0. Create a venv: `python -m venv nbs-venv`
1. Activate the venv:
   UNIX-based things: `source nbs-venv/bin/activate`
   Windows: `nbs-venv\bin\Activate.ps1` in PowerShell
2. Install the dependencies: `pip install -r requirements.txt`
3. Grab a NBS song (maybe from [Note Block World](https://noteblock.world/))
4. Convert it: `python main.py path/to/my/song.nbs`
5. Import the created text file into the Scratch project