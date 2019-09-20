#!/usr/bin/env python3
#
# This file is for making submixes from Slakh data.
# See the README about how to use.
#
# Author: Ethan Manilow

import os

import yaml
import soundfile as sf
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool
import argparse


def _file_ready_string(string):
    """
    Change a string from 'Something Like This" to "something_like_this"
    for ease of saving it as a filename or directory name.
    :param string:
    :return:
    """
    return string.replace(' ', '_').lower()


class Submixes(object):
    RESIDUALS_KEY = 'residuals'

    def __init__(self, base_dir, submix_file):

        self.base_directory = base_dir
        self.submix_name = os.path.splitext(os.path.basename(submix_file))[0]
        self.submix_data = yaml.load(open(submix_file, 'r'))
        self.submix_recipes = self.submix_data['Recipes']

        all_vals = [i for s in self.submix_recipes.values() for i in s]
        if len(set(all_vals)) != len(all_vals):
            raise LookupError('All values in submix file must be unique! A value was used more than once.')
        # invert the dictionary so the keys are program numbers and the vals are the submix name.
        self._inv_sm = self._invert_dict(self.submix_recipes)

        self.submix_key = self.submix_data['Mixing key']
        if self.RESIDUALS_KEY in self.submix_recipes.keys():
            raise ValueError('\'{}\' is a reserved submix name.'.format(self.RESIDUALS_KEY))

    def _get_all_src_dirs(self):
        return sorted([root for root, dirs, files in os.walk(self.base_directory)
                       if 'metadata.yaml' in files])

    @staticmethod
    def _invert_dict(d):
        """
        Inverts the keys and values of dictionary of lists like so:

        >>> d = {'a': [1, 2, 3], 'b': [4, 5], 'c': [6, 7]}
        >>> _invert_dict(d)
        {1: 'a', 2: 'a', 3: 'a', 4: 'b', 5: 'b', 6: 'c', 7: 'c'}

        :param d:
        :return:
        """
        return {i: k for k, v in d.items() for i in v}

    def do_all_submixes(self, n_threads=1):
        dirs = self._get_all_src_dirs()
        pool = ThreadPool(n_threads)
        pool.map(self.do_submix, dirs)

    def do_submix(self, srcs_dir):
        src_metadata = yaml.load(open(os.path.join(srcs_dir, 'metadata.yaml'), 'r'))
        submix_dir = os.path.join(srcs_dir, _file_ready_string(self.submix_name))
        os.makedirs(submix_dir, exist_ok=True)

        mix_wav, sr = sf.read(os.path.join(srcs_dir, 'mix.wav'))

        submixes_dict = {_file_ready_string(k): [] for k in self.submix_recipes.keys()}
        submixes_dict[self.RESIDUALS_KEY] = []

        # Use the file's metadata and the submix recipe to gather all the
        # sources together.
        for s in os.listdir(os.path.join(srcs_dir, 'stems')):
            src_path = os.path.join(srcs_dir, 'stems', s)
            src_wav, sr = sf.read(src_path)

            # Figure out which submix this source belongs to
            src_id = os.path.splitext(s)[0]
            src_submix_name = src_metadata[src_id][self.submix_key]
            key = self._inv_sm[src_submix_name] if src_submix_name in self._inv_sm else self.RESIDUALS_KEY
            key = _file_ready_string(key)

            if key not in submixes_dict.keys():
                # Should be in the dict already, but just to make sure
                submixes_dict[key] = []

            submixes_dict[key].append(src_wav)

        # Sum all of the sources in each submix and ready the info for the feature reader.
        for src_name, src_data in submixes_dict.items():

            # if there's no data for this submix, write a file of 0's
            if len(src_data) <= 0:
                src_data = np.zeros((1, mix_wav.shape[0]))

            # The files should already be normalized in the mix,
            # so no need to remix/renormalize them here.
            src_path = os.path.join(submix_dir, '{}.wav'.format(src_name))
            submix = np.sum(src_data, axis=0)
            sf.write(src_path, submix, sr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-submix-definition-file', '-s', type=str, required=True,
                        help='Path to yaml file to define a submix.')
    parser.add_argument('-input-dir', '-i', type=str, required=False,
                        help='Base directory to apply a submix to the whole dataset.')
    parser.add_argument('-src-dir', '-s', type=str, required=False,
                        help='Directory of a single track to create a submix for.')
    parser.add_argument('-num-threads', '-t', type=int, default=1,
                        help='Number of threads to spwan to do the submixing.')

    args = parser.parse_args()
    if args.root_dir is None and args.src_dir is None:
        raise ValueError('Must provide one of (root_dir, src_dir).')
    elif args.root_dir is not None and args.src_dir is not None:
        raise ValueError('Must provide only one of (root_dir, src_dir).')

    elif args.root_dir:
        sm = Submixes(args.input_dir, args.submix_definition)
        sm.do_all_submixes(args.num_threads)

    elif args.src_dir:
        sm = Submixes(None, args.submix_definition)
        sm.do_submix(args.src_dir)

    else:
        raise ValueError('I do not now how you got in this state, but something is broken!')
