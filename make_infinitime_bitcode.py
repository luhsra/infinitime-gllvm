#!/usr/bin/env python
"""Build bitcode for InfiniTime."""

from build_tools import run, Builder


class InfinitimeBuilder(Builder):
    """Build bitcode for InfiniTime."""
    def __init__(self):
        super().__init__(with_cmake=True, with_target=True)

    def do_build(self):
        self._make_new(self.args.build_dir)

        env = self._get_gllvm_env()

        cmake_cmd = [
            self.args.cmake_program,
            str(self.args.src_dir.absolute()), '-GNinja'
        ] + ['-D' + x for x in self.args.cmake_args]
        run('Executing CMake', cmake_cmd, cwd=self.args.build_dir, env=env)

        ninja_cmd = [self.args.ninja_program, self.args.target, '--verbose']
        run('Executing Ninja', ninja_cmd, cwd=self.args.build_dir, env=env)

        image = self.args.build_dir / 'src' / self.args.target
        assert image.is_file()

        self._get_bc(image, env)


if __name__ == '__main__':
    builder = InfinitimeBuilder()
    builder.do_build()
