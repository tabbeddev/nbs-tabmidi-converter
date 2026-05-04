# NBS to Scratch TabMidi

A small program to convert [NBS songs](https://noteblock.studio/) to the format for my [Scratch-based MIDI-Editor](https://scratch.mit.edu/projects/1311570943/) ([Turbowarp](https://turbowarp.org/1311570943/fullscreen)).

## "Disclaimer"

Technically it can convert Rush E, but the song can't be fully imported in the Scratch Player, as it hits the max character limit in Ask-Blocks.

## Usage

0. Create a venv: `python -m venv nbs-venv`
1. Activate the venv:  
   UNIX-based things: `source nbs-venv/bin/activate`  
   Windows: `nbs-venv\bin\Activate.ps1` in PowerShell
2. Install the dependencies: `pip install -r requirements.txt`
3. Grab a NBS song (maybe from [Note Block World](https://noteblock.world/))
4. Convert it: `python main.py path/to/my/song.nbs`
5. Import the created text file into the Scratch project

## Tips and tricks

### 1. Cut off songs / Song data is too long

You can tell if a song fits fully in the import limit by looking at the last character. If it is an `$` the song will be fully imported.  
If not it will be cut off somewhere. Either tracks are missing or ending prematurely.

You can sortoff fix this by using the `--limit | -l` argument to cut off the song earlier.

### 2. My song doesn't sound fluent

If the notes aren't held long enough, you can use the `--hold | -o` argument to specify a longer time to hold the note.

### 3. The pitch is too high or low / Some limit has been hit

Use the argument `--transpose | -t` to transpose your song by a given amount of octaves.  
Keep in mind, that there's an upper and lower limit. The script will try to fix it, when the limit has been hit (a warning will be displayed), but the song might sound off.

### 4. My song is too quiet or loud

Use the argument `--volume | -v` to multiply the volume of the song. `0.5` will half the volume, while `2.0` will double the volume.

### 5. My song uses a lot of unknown instruments and they sound weird

By default an unknown instrument uses the Scratch instrument 20. This can be changed using the argument `--unknown-instrument | -u`.