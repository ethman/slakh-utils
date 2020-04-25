## Make Splits

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
