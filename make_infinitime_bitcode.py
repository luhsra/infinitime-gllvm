#!/usr/bin/env python
"""Fake an ARM toolchain directory for InfiniTime."""
import argparse
import sys
import pathlib
import os
import shutil
import subprocess


def eprint(*args):
    """Error print"""
    print(*args, file=sys.stderr)


def run(message, cmd, **kwargs):
    """Print and execute a command."""
    env_fmt = ''
    if 'env' in kwargs:
        env_diff = set(kwargs['env'].items()) - set(os.environ.items())
        env_fmt = ' '.join([f"{key}='{val}'" for key, val in env_diff])
    eprint(message + ':', env_fmt, ' '.join([f"'{x}'" for x in cmd]))
    subprocess.run(cmd, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument('--cmake-builddir',
                        help='Directory for the CMake build.',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--infinitime-dir',
                        help='Directory for InfiniTime.',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--cmake-program',
                        help='CMake executable.',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--ninja-program',
                        help='Ninja executable.',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--get-bc-program',
                        help='get-bc executable.',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--llvm-objcopy-program',
                        help='llvm-objcopy executable.',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--llvm-ld-program',
                        help='lld executable.',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--target',
                        help='Ninja target.',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--output',
                        help='Bitcode output file.',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--llvm-bindir',
                        help='Directory that contains the LLVM tools.',
                        required=True,
                        type=pathlib.Path)
    parser.add_argument('--cmake-args',
                        help='CMake arguments (given as "foo=bar")',
                        required=True,
                        nargs='*')
    args = parser.parse_args()
    if args.cmake_builddir.is_dir():
        shutil.rmtree(args.cmake_builddir)

    args.cmake_builddir.mkdir()

    assert args.infinitime_dir.is_dir()
    assert args.cmake_program.is_file()
    assert args.ninja_program.is_file()
    assert args.get_bc_program.is_file()
    assert args.llvm_objcopy_program.is_file()
    assert args.llvm_ld_program.is_file()
    assert args.llvm_bindir.is_dir()

    cmake_env = {**os.environ}
    cmake_env['LLVM_COMPILER_PATH'] = str(args.llvm_bindir.absolute())
    cmake_env['GLLVM_OBJCOPY'] = str(args.llvm_objcopy_program.absolute())
    cmake_env['GLLVM_LD'] = str(args.llvm_ld_program.absolute())
    # cmake_env['WLLVM_OUTPUT_LEVEL'] = 'DEBUG'
    cmake_cmd = [
        args.cmake_program,
        str(args.infinitime_dir.absolute()), '-GNinja'
    ] + ['-D' + x for x in args.cmake_args]
    run('Executing CMake', cmake_cmd, cwd=args.cmake_builddir, env=cmake_env)

    ninja_cmd = [args.ninja_program, args.target, '--verbose']
    run('Executing Ninja', ninja_cmd, cwd=args.cmake_builddir, env=cmake_env)

    image = args.cmake_builddir / 'src' / args.target
    assert image.is_file()

    get_bc_cmd = [args.get_bc_program, '-o', args.output.absolute(), image]
    run('Executing get-bc', get_bc_cmd, cwd=args.cmake_builddir, env=cmake_env)


if __name__ == '__main__':
    main()
