# slakh-utils
Utilities for interfacing with Slakh2100


### Set up

Before you can use any of the utils, you need python3 installed on your machine. It is 
recommended to use a new virtual environment or anaconda environment. Then download or clone the
code in this repository and install the required packages like so:

```bash
    $ pip install -r requirements.txt
```

### Converting to/from `.flac`

Slakh2100 comes compressed as .flac files. To convert every .flac file to .wav (and vice versa), use
the script provided in the `conversion/` directory called `flac_converter.py`.

```bash
    $ python flac_converter.py -i /path/to/compressed/Slakh2100 -o /output/path/Slakh2100_wav -c False
```

Full usage details:

```bash
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


### Making submixes

Makes submixes of different instruments within a mix.

Usage:

```bash
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


### Mixing


### Make Splits




