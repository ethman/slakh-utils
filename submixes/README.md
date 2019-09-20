
## Setting up utils

Before you can use any of the utils, you need python3 installed on your machine. It is 
recommended to use a new virtual environment or anaconda environment. Then download or clone the
code in this repository and install the required packages like so:

```bash
    $ pip install -r requirements.txt
```


### Making Submixes

This is a script that makes submixes by combining sets of instruments within a mix. It is possible to define
customizable submixes by providing a submix definition file. A few examples of submix definition files are provided 
[here](https://github.com/ethman/slakh-utils/tree/master/submixes/example_submixes).

To use this script you can either provide the base path to all of Slakh to make submixes for every track,
or you can provide it a single track to make a submix for only the provided track. Submix output
is put into the `TrackXXXXX/stems/` directory with the name of the submix definition file. For example,
for a submix definition file named `band.yaml`, the output of this script will go into `TraackXXXXX/stems/band/`.

Full usage details:

```
$ python submixes.py [-h] -submix-definition-file SUBMIX_DEFINITION_FILE
                   [-input-dir INPUT_DIR] [-src-dir SRC_DIR] 
                   [-num-threads NUM_THREADS]

arguments:
  -h, --help            show this help message and exit
  -submix-definition-file SUBMIX_DEFINITION_FILE, -s SUBMIX_DEFINITION_FILE
                        Path to yaml file to define a submix.
  -input-dir INPUT_DIR, -i INPUT_DIR
                        Base directory to apply a submix to the whole dataset.
  -src-dir SRC_DIR, -s SRC_DIR
                        Directory of a single track to create a submix for
  -num-threads NUM_THREADS, -t NUM_THREADS
                        Number of threads to spwan to do the submixing.

```

The submix definition files are `yaml` files that contain "recipes" about which types of isolated sources get
mixed together into submix sources. Inside the yaml file is a dictionary that contains two elements, 
a `Mixing Key` and the `Recipes` list. 


The `Mixing key` tells the script what part of the [metadata](https://github.com/ethman/slakh-utils#metadata) to look at to define submix
sources (that get mixed together). Options for `Mixing key` could *technically* be any entry under the
source name in `metadata.yaml`, but most common `Mixing key`s are (ordered from most to least
general) `inst_class`, `program_num` (equivalent to `midi_program_name`), and `plugin_name`.

The `Recipes` list is a list of dictionaries that define what isolated sources get mixed into submix
sources. The key of each dictionary is the name of the source (and its name on disc after the script is run),
and the value is a list of possible entries that make the source. **Everything that is encountered that
isn't defined by a recipe will be put into a file called** `residuals.wav`.

Here's an example. If we want to make a submix with every piano except harpsichord and clavinet, 
first we look at the [MIDI instrument chart](https://github.com/ethman/slakh-utils/blob/master/midi_inst_values/general_midi_inst_0based.txt):

```
- Piano
0 Acoustic Grand Piano
1 Bright Acoustic Piano
2 Electric Grand Piano
3 Honky-tonk Piano
4 Electric Piano 1
5 Electric Piano 2
6 Harpsichord
7 Clavinet

- Chromatic Percussion
8 Celesta
9 Glockenspiel
10 Music Box
...
```

`- Piano` defines the MIDI instrument class (`inst_class` in the metadata), and the eight values
below it are the instrument program number (`program_num`) and instrument program name (`midi_program_name`).

So it looks like we want MIDI program numbers \[0-5]. So we set our mixing key to `program_num`, and
make a recipe called `Piano` with our values:

```yaml
Mixing key: "program_num"
Recipes:
  Favorite Piano Sounds:
    - 0
    - 1
    - 2
    - 3
    - 4
    - 5
``` 

Let's name this file `my_pianos.yaml`. When give this submix definition to `submixes.py` it will
make a new folder in the `stems` directory of every track called `my_pianos/`. Inside `my_pianos/`
will be a file called `favorite_piano_sounds.wav` containing every track that has those MIDI instrument
values and another file called `residuals.wav` containing everything else.
