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
