from concurrent import futures
import torch as th
import numpy as np
from pathlib import Path
import soundfile
from tqdm import tqdm
import shutil
import subprocess as sp
import argparse


def load_flac_and_save(flac_path):
    audio, sr = soundfile.read(str(flac_path), dtype=np.int16)
    save_path = flac_path.parent / (flac_path.stem + '.raw')
    with open(str(save_path), 'wb') as f:
        f.write(audio.tobytes())


def wav_to_flac(wav_path, samplerate, postfix, overwrite):
    assert wav_path.suffix == '.wav'
    save_path = wav_path.parent / (wav_path.stem + postfix + '.flac')
    overwrite_str = '-y' if overwrite else '-n'
    exec_txt = f'ffmpeg {overwrite_str} -i "{str(wav_path)}" \
        -af aformat=s16:{samplerate} -threads 1 "{str(save_path)}"'
    sp.run(exec_txt, shell=True)


def flac_to_16k(flac_path):
    raise NotImplementedError('ffmpeg sometimes trim flac when resampling. \
        use direct conversion from wav_to_flac')
    save_path = flac_path.parent / (flac_path.stem + '_16k.flac')
    exec_txt = f'ffmpeg -i "{str(flac_path)}" -af aformat=s16:16000 -threads 1 "{str(save_path)}"'
    sp.run(exec_txt, shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser('converter')
    parser.add_argument('-slakh', type=Path)
    parser.add_argument('-samplerate', type=int)
    parser.add_argument('-glob_regexp', type=str,
                        help='regular expression to glob target files. \
                            will slakh.glob(glob_regexp) \
                            ex) "**/5stem_inst/*.wav"')
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--postfix', type=str, default='')

    args = parser.parse_args()


    SLAKH_PATH = '/home/svcapp/userdata/musicai/slakh2100_flac'
    wavs = sorted(Path(SLAKH_PATH).glob(args.glob_regexp)

    with futures.ProcessPoolExecutor(args.workers) as pool:
        for wav in tqdm(wavs):
            pool.submit(wav_to_flac,
                        wav, args.samplerate, args.postfix, args.overwrite)
