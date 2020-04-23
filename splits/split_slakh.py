#!/usr/bin/env python3
import json
import os
import argparse
import shutil


def do_all_moves(slakh_base_dir, new_splits_file):
    with open(new_splits_file) as f:
        new_splits = json.load(f)

    for track_id, track_dict in new_splits.items():
        if track_dict['moved']:
            source_dir = track_dict['source_split']
            source_path = os.path.join(slakh_base_dir, source_dir, track_id)
            dest_dir = track_dict['destination_split']
            dest_path = os.path.join(slakh_base_dir, dest_dir, track_id)
            shutil.move(source_path, dest_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--slakh-dir', '-s', type=str, help='Base directory of Slakh2100 '
                                                            '(with train/val/test subdirectories)')
    parser.add_argument('--new-splits-file', '-n', type=str, help='Path to splits_v2.json',
                        default='splits_v2.json')
    args = parser.parse_args()
    do_all_moves(args.slakh_dir, args.new_splits_file)
