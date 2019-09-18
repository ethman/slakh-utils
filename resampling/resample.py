#!/usr/bin/env python3

import os
import shutil
import sys

import yaml
import json
import soundfile as sf
import numpy as np
import stempeg
import librosa
import argparse
from multiprocessing.dummy import Pool as ThreadPool

from loguru import logger


def get_args(parser):
    parser.add_argument('--input-dir', '-i', required=True, type=str, help='Input base directory.')
    parser.add_argument('--output-dir', '-o', required=False, type=str,
                        help='Output base directory.')
    parser.add_argument('--dataset', '-d', required=True, type=str, help='Dataset to resample')
    parser.add_argument('--sample_rate', '-sr', required=True, type=int, help='Target sample rate')
    parser.add_argument('--n-threads', '-t', required=True, type=int, help='Number of threads to run in parallel.')
    args = parser.parse_args()
    return args


@logger.catch
def main():
    args = get_args(argparse.ArgumentParser())
    dataset = args.dataset.lower().replace('-', '_')
    sample_rate = args.sample_rate
    output_dir = args.output_dir
    base_dir = args.input_dir
    n_threads = args.n_threads

    logger.remove()
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                                  "<level>{level: <8}</level> | "
                                  "<level>{message}</level>")

    logger.info('Starting resampling...')
    if dataset in ['slakh', 'flakh']:
        slakh_resample(base_dir, sample_rate, output_dir, n_threads)
    elif dataset == 'musdb':
        musdb_decode_and_resample(base_dir, sample_rate, output_dir, n_threads)
    else:
        raise ValueError(f'Cannot resample {dataset}')

    logger.info('Completed resampling.')


def resample_wav(in_path, out_path, sr):
    wav, input_sr = sf.read(in_path)
    wav = librosa.resample(wav, input_sr, sr, scale=False)
    sf.write(out_path, wav, sr)


def slakh_resample(input_dir, target_sr, output_dir, n_threads=1):

    pool = ThreadPool(n_threads)
    track_dirs = sorted([track_dir for track_dir in os.listdir(input_dir)
                         if os.path.isdir(os.path.join(input_dir, track_dir))
                         and 'metadata.yaml' in os.listdir(os.path.join(input_dir, track_dir))])

    def _resamp(track_dir):
        logger.info(f'Resampling {track_dir} stems...')
        input_track_dir = os.path.join(input_dir, track_dir)
        output_track_dir = os.path.join(output_dir, track_dir)
        os.makedirs(output_track_dir, exist_ok=True)

        in_mix_path = os.path.join(input_track_dir, 'mix.wav')
        out_mix_path = os.path.join(output_track_dir, 'mix.wav')
        resample_wav(in_mix_path, out_mix_path, target_sr)

        shutil.copy(os.path.join(input_track_dir, 'metadata.yaml'),
                    os.path.join(output_track_dir, 'metadata.yaml'))
        shutil.copy(os.path.join(input_track_dir, 'all_src.mid'),
                    os.path.join(output_track_dir, 'all_src.mid'))
        if not os.path.isdir(os.path.join(output_track_dir, 'MIDI')):
            shutil.copytree(os.path.join(input_track_dir, 'MIDI'),
                            os.path.join(output_track_dir, 'MIDI'))

        in_stems_dir = os.path.join(input_track_dir, 'stems')
        out_stems_dir = os.path.join(output_track_dir, 'stems')
        os.makedirs(out_stems_dir, exist_ok=True)
        for src in os.listdir(in_stems_dir):
            if os.path.splitext(src)[-1] != '.wav':
                continue
            in_src_path = os.path.join(in_stems_dir, src)
            out_src_path = os.path.join(out_stems_dir, src)
            resample_wav(in_src_path, out_src_path, target_sr)

    pool.map(_resamp, track_dirs)


def musdb_decode_and_resample(input_dir, target_sr, output_dir, n_threads):
    """
    Reads MUSDB18 .stem.mp4 files, splits them into .wav files at `target_sr`.
    Sums the stereo files to mono TODO: option to not sum to mono
    :param input_dir:
    :param target_sr:
    :param output_dir:
    :param n_threads:
    :return:
    """
    stem_labels = ['mixture', 'drums', 'bass', 'other', 'vocals']

    pool = ThreadPool(n_threads)

    for split in ['train', 'test']:
        in_dir = os.path.join(input_dir, split)
        if not os.path.isdir(in_dir):
            logger.warning(f'Looking for f{in_dir}, but not found!')
            continue

        out_dir = os.path.join(output_dir, split)
        os.makedirs(out_dir, exist_ok=True)
        stempeg_paths = [f for f in os.listdir(in_dir)
                         if os.path.isfile(os.path.join(in_dir, f))
                         if os.path.splitext(f)[1] == '.mp4']

        def _resamp(stempeg_filename):
            stempeg_path = os.path.join(in_dir, stempeg_filename)
            stempeg_filename_stub = stempeg_filename.replace('.stem.mp4', '').replace(' ', '')
            output_wav_dir = os.path.join(out_dir, stempeg_filename_stub)
            os.makedirs(output_wav_dir, exist_ok=True)

            # read stempeg format
            stem, input_sr = stempeg.read_stems(stempeg_path)
            for i, name in enumerate(stem_labels):
                wav = np.sum(stem[i, ...], axis=1)  # sum to mono
                wav = librosa.resample(wav, input_sr, target_sr)
                out_path = os.path.join(output_wav_dir, f'{name}.wav')
                sf.write(out_path, wav, target_sr)

        pool.map(_resamp, stempeg_paths)


if __name__ == '__main__':
    main()