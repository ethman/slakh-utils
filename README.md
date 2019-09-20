# slakh-utils

Utilities for common tasks with the Slakh dataset.

### About Slakh
The Synthesized Lakh (Slakh) Dataset is a new dataset for audio source separation that is synthesized from the [Lakh MIDI Dataset v0.1](https://colinraffel.com/projects/lmd/) using professional-grade sample-based virtual instruments.  **Slakh2100** contains 2100 automatically mixed tracks and accompanying MIDI files synthesized using a professional-grade sampling engine. The tracks in **Slakh2100** are split into training (1500 tracks), validation (375 tracks), and test (225 tracks) subsets, totaling **145 hours** of mixtures.

Slakh is brought to you by [Mitsubishi Electric Research Lab (MERL)](http://www.merl.com/) and the [Interactive Audio Lab at Northwestern University](http://music.cs.northwestern.edu/). For more info, please visit [the Slakh website](www.slakh.com/).


### At a glance

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
   │    └─── S10.mid
   └─── mix.flac
   └─── stems
        └─── S01.flac
        │    ...
        └─── S10.flac 
```

<br>&emsp;- `all_src.mid` is the original MIDI file from Lakh that contains all of the sources.
<br>&emsp;- `metadata.yaml` contains metadata for this track (see below.)
<br>&emsp;- `MIDI` contains MIDI files separated by each instrument, the file names correspond with the stems.
<br>&emsp;- `mix.flac` is the mixture, made my summing up all of the audio in the `stems` directory. 
<br>&emsp;- `stems` contains isolated audio for each source in the mixture.
- All audio in Slakh2100 is distributed in the `.flac` format. (Scripts to batch convert below.)
- All audio was rendered at 44.1kHz, 16-bit (CD quality) before being converted to `.flac`.
- Slakh2100 is distributed as a tarball (`.tar.gz`) that must be uncompressed prior to using any of these scripts.


### Metadata

All metadata is distributed as `yaml` files and are similar in structure to [MedleyDB](https://medleydb.weebly.com/)'s metadata files.

Here is an annotated overview of what is in the metadata files for these tracks. Annotations are in parentheses after the entry below:

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
target_peak: -1.0 (target peak [dB] when applying gain to all stems after summing mixture)
```

For a list of the MIDI program numbers and their organization see [these files](https://github.com/ethman/slakh-utils/tree/master/midi_inst_values).



## Setting up utils

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
It *does not* do the conversion in place! There is a toggle to determine whether you want to compress (to .flac)
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


### Making Submixes

Makes submixes of different instruments within a mix.

Usage:

```
$ python submixes.py [-h] -submix-definition-file SUBMIX_DEFINITION_FILE
                   -input-dir INPUT_DIR -output-dir OUTPUT_DIR -num-threads
                   NUM_THREADS

arguments:
  -h, --help            show this help message and exit
  -submix-definition-file SUBMIX_DEFINITION_FILE, -s SUBMIX_DEFINITION_FILE
                        Path to yaml file to define a submix.
  -input-dir INPUT_DIR, -i INPUT_DIR
                        Base directory to apply a submix to the whole dataset.
  -output-dir OUTPUT_DIR, -o OUTPUT_DIR
                        Directory to apply a submix to one individual set of
                        sources/mixture.
  -num-threads NUM_THREADS, -t NUM_THREADS
                        Number of threads to spwan to do the submixing.

```


### Resampling


### Mixing to Replicate Benchmark Experiments


### Make Splits




