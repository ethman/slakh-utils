# slakh-utils

Utilities for common tasks with the Slakh dataset.

## About Slakh
The Synthesized Lakh (Slakh) Dataset is a new dataset for audio source separation that is synthesized from the [Lakh MIDI Dataset v0.1](https://colinraffel.com/projects/lmd/) using professional-grade sample-based virtual instruments.  **Slakh2100** contains 2100 automatically mixed tracks and accompanying MIDI files synthesized using a professional-grade sampling engine. The tracks in **Slakh2100** are split into training (1500 tracks), validation (375 tracks), and test (225 tracks) subsets, totaling **145 hours** of mixtures.

Slakh is brought to you by [Mitsubishi Electric Research Lab (MERL)](http://www.merl.com/) and the [Interactive Audio Lab at Northwestern University](http://music.cs.northwestern.edu/). For more info, please visit [the Slakh website](http://www.slakh.com/)


## Table of Contents

1. [At a Glance](#at-a-glance)
2. [Metadata](#metadata)
3. [Setting Up Utils](#setting-up-utils)
4. [Converting to/from .flac](#converting-tofrom-flac)
5. [Resampling](#resampling)
6. [Make Splits](#make-splits)
7. [Making Submixes](#making-submixes)
8. [Mixing to Replicate Benchmark Experiments](#mixing-to-replicate-benchmark-experiments)

## At a Glance

- The dataset comes as a series of directories named like `TrackXXXXX`, where `XXXXX` is a number
    between `00001` and `02100`. This number is the ID of the track.
- The directory structure looks like this:

```
Track00001
   └─── all_src.mid
   └─── metadata.yaml
   └─── MIDI
   │    └─── S01.mid
   │    │    ...
   │    └─── SXX.mid
   └─── mix.flac
   └─── stems
        └─── S01.flac
        │    ...
        └─── SXX.flac 
```

<br>&emsp;&emsp;-> `all_src.mid` is the original MIDI file from Lakh that contains all of the sources.
<br>&emsp;&emsp;-> `metadata.yaml` contains metadata for this track (see below.)
<br>&emsp;&emsp;-> `MIDI` contains MIDI files separated by each instrument, the file names correspond with the stems.
<br>&emsp;&emsp;-> `mix.flac` is the mixture, made my summing up all of the audio in the `stems` directory. 
<br>&emsp;&emsp;-> `stems` contains isolated audio for each source in the mixture.
- All audio in Slakh2100 is distributed in the `.flac` format. (Scripts to batch convert below.)
- All audio is mono and was rendered at 44.1kHz, 16-bit (CD quality) before being converted to `.flac`.
- Slakh2100 is distributed as a tarball (`.tar.gz`) that must be uncompressed prior to using any of these scripts.
- Each mixture has a variable number of sources, with a minimum of 4 sources per mix. `metadata.yaml` has information about each source.
- The sources have no guaranteed ordering. See `metadata.yaml` to determine which sources are which.
- The MIDI for source XX in `all_src.mid` is not guaranteed to match `SXX.mid`, as some instrument-specific heuristics were applied to the MIDI to ensure proper synthesis. `SXX.mid` is the exact file used to synthesize `SXX.flac`, whereas entry for source XX in `all_src.mid` is a direct copy from Lakh.
- **Some MIDI files are replicated** (due to a bug). This has can be ameliorated depending on your use case. See [Make Splits](#make-splits) below.


## Metadata

All metadata is distributed as `yaml` files and are similar in structure to [MedleyDB](https://medleydb.weebly.com/)'s metadata files.

Here is an annotated overview of what is in the metadata files for these tracks. Annotations are in parentheses after each entry below:

```
UUID: 1a81ae092884234f3264e2f45927f00a (File name of the original MIDI file from Lakh, sans extension) 
audio_dir: stems (Directory name of where the stems are stored, will always be "stems")
lmd_midi_dir: lmd_matched/O/O/H/TROOHTB128F931F9DF/1a81ae092884234f3264e2f45927f00a.mid (Path to the original MIDI file from a fresh download of Lakh)
midi_dir: MIDI (Directory name of where the separated MIDI files are stored, will always be "MIDI")
normalization_factor: -13.0 (target normalization [dB] for all stems before lowering gain to avoid clipping, will always be "-13.0")
normalized: true (whether the mix and stems were normalized according to the ITU-R BS.1770-4 spec)
overall_gain: 0.18270259567062658 (gain applied to every stem to make sure mixture does not clip when stems are summed)
stems:
  S00: (name of the source on disc, so this is "stems/S01.flac")
    audio_rendered: true (whether the audio was rendered, some rare sources are skipped)
    inst_class: Guitar (MIDI instrument class)
    integrated_loudness: -12.82074180245363 (integrated loudness [dB] of this track as calculated by the ITU-R BS.1770-4 spec)
    is_drum: false (whether the "drum" flag is true for this MIDI track)
    midi_program_name: Distortion Guitar (MIDI instrument program name)
    midi_saved: true (whether the separate MIDI track was saved for this stem)
    plugin_name: elektrik_guitar.nkm (patch/plugin name that rendered this audio file)
    program_num: 30 (MIDI instrument program number)
  S01:
    ...
  S02:
    ...
    
  ...
  
  S10:
    ...
target_peak: -1.0 (target peak [dB] when applying gain to all stems after summing mixture, will always be "-1.0")
```

For a list of the MIDI program numbers and their organization see [these files](https://github.com/ethman/slakh-utils/tree/master/midi_inst_values).


## Scripts

### Setting up utils

Before you can use any of the utils, you need python3 installed on your machine. It is 
recommended to use a new virtual environment or anaconda environment. Then download or clone the
code in this repository and install the required packages like so:

```bash
    $ pip install -r requirements.txt
```

### Converting to/from `.flac`

All of the audio in Slakh2100 comes compressed as .flac files. To convert every .flac file to .wav
(and vice versa), use the script provided in the `conversion/` directory called `flac_converter.py`.

This script outputs a copy of the input Slakh with the .flac files converted to .wav files (or vice versa).
It **does not** do the conversion in place! There is a toggle to determine whether you want to compress (to .flac)
or decompress (to .wav) the audio within Slakh, and there is also an option to multithread this process. See below for 
all options.

```bash
    $ python flac_converter.py -i /path/to/flac/Slakh2100 -o /output/path/Slakh2100_wav -c False
```

Full usage details:

```
$ python flac_converter.py [-h] --input-dir INPUT_DIR --output-dir OUTPUT_DIR
                         --compress COMPRESS [--start START] [--end END]
                         [--num-threads NUM_THREADS] [--verbose VERBOSE]

arguments:
  -h, --help            show this help message and exit
  --input-dir INPUT_DIR, -i INPUT_DIR
                        Base path to input directory. (Required)
  --output-dir OUTPUT_DIR, -o OUTPUT_DIR
                        Base path to output directory. (Required)
  --compress COMPRESS, -c COMPRESS
                        If true, will convert from .wav to .flac, elsewill
                        convert from .flac to .wav. (Required)
  --start START, -s START
                        If converting a subset, the lowest Track ID.
                        (Optional)
  --end END, -e END     If converting a subset, the highest Track ID.
                        (Optional)
  --num-threads NUM_THREADS, -t NUM_THREADS
                        Number of threads to spawn to convert. (Optional)
  --verbose VERBOSE, -v VERBOSE
                        Whether to print messages while processing. (Optional)

```

### Resampling

((Documentation coming soon, for now look at the script in the `resampling` directory))


### Make Splits

The original Slakh2100 was found to have many duplicate MIDI files, some MIDI duplicates that are present
in more than one of the train/test/validation splits.
Even though each song is rendered with a random set of synthesizers, the same versions of the songs appear 
more than once. Same MIDI, different audio files. Still this can be an issue for some uses of Slakh2100.

To that end, we are releasing two additional ways to split Slakh2100. Here's the information about
all of the Slakh2100 splits. *We ask that if you use Slakh2100 in a research paper, that you conform
to this naming convention for easier reproducibility.*

**Slakh2100-orig**: This is the name for the original splits of the Slakh2100 dataset.

**Slakh2100-split2**: This is the name for the new split that *still contains all 2100 tracks*. This new split
**moves** all tracks with duplicated MIDI files such that no duplicated MIDI files are in more than one split.
There are still 1500 train tracks, 375 validation tracks, and 225 test tracks. For this configuration, use
`splits_v2.json` with the script below.

**Slakh2100-redux**: This is the name for the new split that does **not** contain all 2100 tracks. This **omits**
tracks such that each MIDI file only occurs once. As such, there are **1710 total tracks**, 1289 in train,
270 in validation, and 151 in test. For this configuration, use `redux.json` with the script below.

All of the code and json data are in the `splits/` directory of this repository.
We have included a json file that links tracks to their MIDI duplicates at `duplicates.json`. 

Additionally, we have included a script that will convert from `Slakh2100-orig` to `Slakh2100-split2` or `Slakh2100-redux`.
It will also convert `Slakh2100-split2` or `Slakh2100-redux` back to `Slakh2100-orig` using the `-r` flag.
(To convert `Slakh2100-split2` to `Slakh2100-redux`, or vice versa, you must first convert to `Slakh2100-orig`,
so `Slakh2100-split2` -> `Slakh2100-orig` -> `Slakh2100-redux`, or `Slakh2100-redux` -> `Slakh2100-orig` -> `Slakh2100-split2`).

```
usage: resplit_slakh.py [-h] --slakh-dir SLAKH_DIR [--split-file SPLIT_FILE]
                        [--reset]

optional arguments:
  -h, --help            show this help message and exit
  --slakh-dir SLAKH_DIR, -d SLAKH_DIR
                        Base directory of Slakh2100 (with train/val/test
                        subdirectories)
  --split-file SPLIT_FILE, -s SPLIT_FILE
                        Path to a json file containing split data. Either
                        splits_v2.json or redux.json
  --reset, -r           Reset Slakh2100 directory to original splits.


```

To convert `Slakh2100-orig` to `Slakh2100-split2`, run:
```
$python resplit_slakh.py -d /path/to/slakh2100/ -s split_v2.json
```

To convert `Slakh2100-orig` to `Slakh2100-redux`, run:
```
$python resplit_slakh.py -d /path/to/slakh2100/ -s redux.json
```


To convert `Slakh2100-split2` or `Slakh2100-redux` back to `Slakh2100-orig`, run:
```
$python resplit_slakh.py -d /path/to/slakh2100/ -r
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



### Mixing to Replicate Benchmark Experiments


((Documentation and code coming soon.)) 


