project('InfiniTime-gllvm', 'c',
  version : '0.1',
  default_options : ['warning_level=3'])

cmake = import('cmake')
fs = import('fs')

toolchains = subproject('toolchains', default_options: {'enable_arm': 'enabled'})

# fake toolchain directory
py3_mod = import('python')
py3_inst = py3_mod.find_installation('python3')
make_toolchain = [py3_inst, files('make_toolchain.py')]
arm_fake_toolchain = meson.current_build_dir() / 'arm_fake_toolchain'
run_command(make_toolchain, '--output-dir', arm_fake_toolchain)

# nrf5-sdk
nrf5_sdk = subproject('nrf5-sdk')
patched_sdk = nrf5_sdk.get_variable('patched_sdk')

# lv_font_conv
lv_font_conv = find_program('lv_font_conv', required: false)
if not lv_font_conv.found()
  if get_option('offline')
    error('lv_font_conv not found and not allowed to download.')
  else
    # download lv_font_conv
    external_programs = meson.current_build_dir() / 'external_programs'
    npm = find_program('npm', required: true)
    run_command(npm, 'install', '--global', '--prefix', external_programs, 'lv_font_conv', check: true)
    lv_font_conv = find_program(external_programs / 'bin' / 'lv_font_conv')
    assert(lv_font_conv.found(), 'Could not download lv_font_conv')
  endif
endif


infinitime_opts = cmake.subproject_options()
# svf_opts.append_compile_args('cpp', '-Wno-unused-parameter')
infinitime_opts.add_cmake_defines({'ARM_NONE_EABI_TOOLCHAIN_PATH': arm_fake_toolchain,

                                   'NRF5_SDK_PATH': '@0@'.format(patched_sdk),
                                   'LV_FONT_CONV': lv_font_conv.full_path()})
infinitime = cmake.subproject('InfiniTime', options: infinitime_opts)

# cmake .. -GNinja -DARM_NONE_EABI_TOOLCHAIN_PATH="something" -DNRF5_SDK_PATH="~/src/nrf5-sdk/build/nrf5_sdk_patched" -DLV_FONT_CONV="$PWD/something/bin/lv_font_conv" -DCMAKE_C_COMPILER="/usr/bin/arm-none-eabi-gcc"
