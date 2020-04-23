## Make Splits

The original splits to Slakh2100 were found to have duplicate songs that span the train/test/validation splits.
Even though each song is rendered with a random set of synthesizers, the same versions of the songs appear 
more than once. This script remakes the splits such that there are no songs are duplicated in more than one
split. We hope to release a new version of Slakh soon.

```
$ python resplit_slakh.py [-h] --slakh-dir SLAKH_DIR 
                         [--new-splits-file NEW_SPLITS_FILE] 

arguments:
  -h, --help            show this help message and exit
  --slakh-dir SLAKH_DIR , -s INPUT_DIR SLAKH_DIR
                        Base path to Slakh2100 directory. (Required)
  --new-splits-file NEW_SPLITS_FILE, -n NEW_SPLITS_FILE
                        A json file that determines where each track moves. 
                        Defaults to "splits_v2.json" which is included in this repo. (Optional)

```
