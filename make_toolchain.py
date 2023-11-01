#!/usr/bin/env python
"""Fake an ARM toolchain directory for InfiniTime."""
import argparse
import sys
import pathlib
import shutil
import subprocess


def eprint(*args):
    print(*args, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument('--output-dir',
                        help='Directory of the faked ARM toolchain.',
                        required=True,
                        type=pathlib.Path)
    args = parser.parse_args()
    args.output_dir.mkdir()


if __name__ == '__main__':
    main()
