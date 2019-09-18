#!/usr/bin/env python3
#
# This file contains utilities to convert Slakh2100 and Flakh2100
# to and from .flac
#
# Author: Ethan Manilow

import os
import ffmpeg
import argparse
import shutil
import numpy as np
import soundfile as sf
import uuid
from multiprocessing.dummy import Pool as ThreadPool
import threading
from distutils.util import strtobool


def _wav_to_flac(input_path, output_dir, verbose=False):
    """
    Converts one file from wav to flac. Reads input wav file from disk and outputs
    flac file with the same basename into `output_dir`
    :param input_path (str): full path to wav file. Assumes ends in `.wav`
    :param output_dir (str): directory to output the converted flac file.
        The name will be `input_path` with `.wav` replaced with `.flac.`
    :param verbose:
    """
    basename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, basename + '.flac')
    ffmpeg.input(input_path).output(output_path).run_async(overwrite_output=not verbose)


def _flac_to_wav(input_path, output_dir, verbose=False):
    """
    Converts one file from flac to wav. Reads input flac file from disk and outputs
    wav file with the same basename into `output_dir`
    :param input_path (str): full path to flac file. Assumes ends in `.flac`
    :param output_dir (str): directory to output the converted wav file. The name will be
        `input_path` with `.flac` replaced with `.wav.`
    :param verbose:
    """
    basename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, basename + '.wav')
    ffmpeg.input(input_path).output(output_path).run_async(overwrite_output=not verbose)


def _make_track_subset(input_dir, start=None, end=None):
    """
    Reduces list of tracks to a subset if `start` or `end` are not `None`, else returns full list of
    track directories.
    :param input_dir:
    :param start:
    :param end:
    :return:
    """
    track_directories = sorted([os.path.join(input_dir, d)
                                for d in os.listdir(input_dir)
                                if os.path.isdir(os.path.join(input_dir, d))])

    if start is not None and end is not None:
        track_directories = track_directories[start-1:end-1]
    elif start is not None:
        track_directories = track_directories[start-1:]
    elif end is not None:
        track_directories = track_directories[:end-1]

    return track_directories


def _convert_folder(in_track_dir, mix_name, output_base_dir, ffmpeg_func, verbose=False):
    track_dir_basename = os.path.basename(in_track_dir)
    in_mix_path = os.path.join(in_track_dir, mix_name)
    out_track_dir = os.path.join(output_base_dir, track_dir_basename)
    out_stems_dir = os.path.join(out_track_dir, 'stems')
    os.makedirs(out_stems_dir, exist_ok=True)

    shutil.copy(os.path.join(in_track_dir, 'metadata.yaml'),
                os.path.join(out_track_dir, 'metadata.yaml'))
    shutil.copy(os.path.join(in_track_dir, 'all_src.mid'),
                os.path.join(out_track_dir, 'all_src.mid'))
    shutil.copytree(os.path.join(in_track_dir, 'MIDI'),
                    os.path.join(out_track_dir, 'MIDI'))

    ffmpeg_func(in_mix_path, out_track_dir)

    in_stems_dir = os.path.join(in_track_dir, 'stems')
    for src in os.listdir(in_stems_dir):
        src_path = os.path.join(in_stems_dir, src)
        ffmpeg_func(src_path, out_stems_dir, verbose=verbose)


def _apply_ffmpeg(base_dir, output_dir, compress=True, start=None, end=None, n_threads=1,
                  verbose=False):

    if compress:
        ffmpeg_func = _wav_to_flac
        mix_name = 'mix.wav'
    else:
        ffmpeg_func = _flac_to_wav
        mix_name = 'mix.flac'

    track_directories = _make_track_subset(base_dir, start, end)
    pool = ThreadPool(n_threads)

    # Make a closure because mix_name, output_dir, and ffmpeg_func are unchanging at this point
    def _apply_convert_dir(in_track_dir):
        _convert_folder(in_track_dir, mix_name, output_dir,
                        ffmpeg_func, verbose=verbose)

    pool.map(_apply_convert_dir, track_directories)


def to_flac(base_dir, output_dir, start=None, end=None, n_threads=1, verbose=False):
    """
    Convert all wav files in all folders (or a subset thereof) to flac files.
    :param base_dir: (str) path to dataset with uncompressed files
    :param output_dir: (str) new location for compressed dataset
    :param start: (int) index/id of the starting folder to compress
    :param end: (int) index/id of the end folder to compress
    :param n_threads: (int) number of threads to spawn for this task
    :param verbose: (str) display ffmpeg output
    """
    _apply_ffmpeg(base_dir, output_dir, compress=True, start=start, end=end,
                  n_threads=n_threads, verbose=verbose)


def to_wav(base_dir, output_dir, start=None, end=None, n_threads=1, verbose=False):
    """
    Convert all flac files in all folders (or a subset thereof) to wav files.
    :param base_dir: (str) path to dataset with compressed files
    :param output_dir: (str) new location for uncompressed dataset
    :param start: (int) index/id of the starting folder to decompress
    :param end: (int) index/id of the end folder to decompress
    :param n_threads: (int) number of threads to spawn for this task
    :param verbose: (str) display ffmpeg output
    """
    _apply_ffmpeg(base_dir, output_dir, compress=False, start=start, end=end,
                  n_threads=n_threads, verbose=verbose)


def _read_flac_to_numpy2(filename, aformat='s16be', sr=44100):
    """
    I WISH THIS WORKED BECAUSE IT'S SO SLICK BUT IT DOES NOT!!!

    ~~leaving this here with the hope that it will be useful in the future~~

    Essentially, this tries to convert the flac to wav with the output
    being the std pipe. It should then parse the binary data in the pipe
    into a numpy array. BUT this produces garbage on my machine.

    Use command `ffmpeg -formats | grep PCM` to determine what PCM audio
    formats are available on your machine.
    """
    raise NotImplementedError('This doesn\'t work! Use `read_flac_to_numpy()` instead.')
    codec = 'pcm_' + aformat
    out, err = ffmpeg.input(filename).output('pipe:',
                                             format=aformat,
                                             acodec=codec,
                                             ar=sr).run(capture_stdout=True)
    return np.frombuffer(out)


def read_flac_to_numpy(filename):
    """
    Reads a single flac file to memory as a numpy array.
    Converts the flac file to uniquely named temp wav using ffmpeg, then reads that into memory
    and deletes the temp file.
    :param filename: (str) path to the flac file to read
    :return: (np.ndarray, int) numpy array of the data and sample rate, respectively.
    """
    try:
        thread_id = threading.get_ident()
    except:
        thread_id = threading.current_thread().ident

    # this file temp_name is unique AF
    temp_name = '{}_{}_{}.wav'.format(str(uuid.uuid4()), os.getpid(), thread_id)
    ffmpeg.input(filename).output(temp_name).run()
    wav, sr = sf.read(temp_name)
    os.remove(temp_name)
    return wav, sr


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', '-i', type=str, required=True,
                        help='Base path to input directory. (Required)')
    parser.add_argument('--output-dir', '-o', type=str, required=True,
                        help='Base path to output directory. (Required)')
    parser.add_argument('--compress', '-c', type=lambda x:bool(strtobool(x)), required=True,
                        help='If true, will convert from .wav to .flac, else'
                             'will convert from .flac to .wav. (Required)')
    parser.add_argument('--start', '-s', type=int, default=None, required=False,
                        help='If converting a subset, the lowest Track ID. (Optional)')
    parser.add_argument('--end', '-e', type=int, default=None, required=False,
                        help='If converting a subset, the highest Track ID. (Optional)')
    parser.add_argument('--num-threads', '-t', type=int, default=1, required=False,
                        help='Number of threads to spawn to convert. (Optional)')
    parser.add_argument('--verbose', '-v', type=lambda x:bool(strtobool(x)), default=False,
                        required=False,
                        help='Whether to print messages while processing. (Optional)')

    args = parser.parse_args()
    _apply_ffmpeg(args.input_dir, args.output_dir, args.compress, args.start,
                  args.end, args.num_threads, args.verbose)
