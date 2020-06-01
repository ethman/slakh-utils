#!/usr/bin/env python3

import json
import os
import argparse
import shutil


def do_all_updates(slakh_base_dir, new_splits_file):
    with open(new_splits_file) as f:
        new_splits = json.load(f)

    for track_id, track_dict in new_splits.items():
        action = track_dict['action']

        if action:
            source_dir = track_dict['source_split']
            source_path = os.path.join(slakh_base_dir, source_dir, track_id)

            if action == 'move':
                dest_dir = track_dict['destination_split']
                dest_path = os.path.join(slakh_base_dir, dest_dir, track_id)

            elif action == 'omit':
                omit_dir = os.path.join(slakh_base_dir, 'omitted')
                os.makedirs(omit_dir, exist_ok=True)
                dest_path = os.path.join(omit_dir, track_id)

            else:
                raise ValueError(f"Unknown action: \'{action}\'")

            shutil.move(source_path, dest_path)


def reset(slakh_base_dir):
    split_dirs = ['train', 'validation', 'test', 'omitted']

    track_dirs = []
    for split in split_dirs:
        split_path = os.path.join(slakh_base_dir, split)
        if not os.path.isdir(split_path):
            continue
        for track in os.listdir(split_path):
            track_path = os.path.join(split_path, track)
            if os.path.isdir(track_path) and track[:5] == 'Track':
                track_dirs.append(track_path)

    for track_path in track_dirs:
        track_id = os.path.basename(track_path)
        if track_id <= 'Track01500':
            dest_path = os.path.join(slakh_base_dir, 'train', track_id)
        elif track_id <= 'Track01875':
            dest_path = os.path.join(slakh_base_dir, 'validation', track_id)
        else:
            dest_path = os.path.join(slakh_base_dir, 'test', track_id)

        if dest_path != track_path:
            shutil.move(track_path, dest_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--slakh-dir', '-d', type=str, help='Base directory of Slakh2100 '
                                                            '(with train/val/test subdirectories)',
                        required=True)
    parser.add_argument('--split-file', '-s', type=str, help='Path to a json file containing '
                                                             'split data. Either splits_v2.json '
                                                             'or redux.json',
                        default='[[PLEASE PROVIDE SPLIT JSON FILE]]')
    parser.add_argument('--reset', '-r', action='store_true', help='Reset Slakh2100 directory to '
                                                                   'original splits.')
    args = parser.parse_args()
    if args.reset:
        reset(args.slakh_dir)
    else:
        do_all_updates(args.slakh_dir, args.split_file)
