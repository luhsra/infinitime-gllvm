project('InfiniTime-gllvm', 'c', 'cpp',
  version : '0.1',
  default_options : ['warning_level=3'])

cmake = import('cmake')
fs = import('fs')

llvm_version = ['>=14', '<15']
llvm_dep = dependency('llvm', method: 'config-tool', version: llvm_version, include_type: 'system')

toolchains = subproject('toolchains', default_options: {'enable_arm': 'enabled'})
assert(toolchains.get_variable('arm_enabled'), 'We need a functional ARM toolchain for InfiniTime')
llvm_bindir = toolchains.get_variable('llvm_bindir')
gcc_arm_version = toolchains.get_variable('gcc_arm_version')
arm_cxx_dir = toolchains.get_variable('arm_cxx_dir')
arm_triple = toolchains.get_variable('arm_triple')
arm_libgcc_dir = toolchains.get_variable('arm_libgcc_dir')
arm_include_path = toolchains.get_variable('arm_include_path')
arm_link_path = toolchains.get_variable('arm_link_path')
llvm_objcopy = toolchains.get_variable('llvm_objcopy')
llvm_dis = toolchains.get_variable('llvm_dis')
llvm_ld = toolchains.get_variable('llvm_ld')
tools = ['gcc', 'ar', 'ranlib', 'c++', 'size', 'objcopy']

# fake toolchain directory
py3_mod = import('python')
py3_inst = py3_mod.find_installation('python3')

tools_cmds = []
foreach tool : tools
  set_variable('arm_' + tool.underscorify(), toolchains.get_variable('arm_' + tool.underscorify()))
endforeach

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
    lv_font_conv = find_program(external_programs / 'bin' / 'lv_font_conv', required: false)
    if not lv_font_conv.found()
      npm = find_program('npm', required: true)
      run_command(npm, 'install', '--global', '--prefix', external_programs, 'lv_font_conv', check: true)
      lv_font_conv = find_program(external_programs / 'bin' / 'lv_font_conv')
    endif
  endif
endif

# gllvm/wllvm
gllvm_meson = subproject('gllvm-meson')
gclang = gllvm_meson.get_variable('gclang')
gclang_cpp = gllvm_meson.get_variable('gclang_cpp')
get_bc = gllvm_meson.get_variable('get_bc')

build_tools_env = gllvm_meson.get_variable('build_tools_env')

# Loading the CMake targets within Meson does not work, so call it directly.
# See https://github.com/mesonbuild/meson/issues/12451

infinitime = subproject('InfiniTime')
infinitime_dir = infinitime.get_variable('infinitime_dir')

cmake_tool = find_program('cmake')
ninja = find_program('ninja')
make_infinitime_bitcode = [py3_inst, files('make_infinitime_bitcode.py')]

arm_mode = 'thumb' / 'v7e-m+fp' / 'hard'
cflags = [
  f'-I@arm_include_path@',
  f'-L@arm_link_path@' / arm_mode,
  f'-L@arm_libgcc_dir@' / arm_mode,
]
cxx_libs = ' '.join([
  arm_cxx_dir,
  arm_cxx_dir / arm_triple / arm_mode,
])
pinetime_app_bc = custom_target('pinetime-app-bc',
  output:['pinetime-app-0.15.0.out.bc'],
  env: build_tools_env,
  command: [
    make_infinitime_bitcode,
    '--build-dir', meson.current_build_dir() / 'infinitime_build',
    '--src-dir', infinitime_dir,
    '--llvm-bindir', llvm_bindir,
    '--target', 'pinetime-app-0.15.0.out',
    '--cmake-program', cmake_tool.full_path(),
    '--ninja-program', ninja.full_path(),
    '--get-bc-program', get_bc.full_path(),
    '--llvm-objcopy-program', llvm_objcopy.full_path(),
    '--llvm-ld-program', llvm_ld.full_path(),
    '--output', '@OUTPUT@',
    '--cmake-args', [ 'USE_CLANG=1',
                      'ARM_GCC_VERSION=' + gcc_arm_version,
                      f'NRF5_SDK_PATH=@patched_sdk@',
                      'ARM_NONE_EABI_TOOLCHAIN_PATH=this-directory-does-not-exist',
                      'USE_JLINK=0',
                      'USE_CLANG=1',
                      'USE_GDB_CLIENT=1',
                      'GDB_CLIENT_TARGET_REMOTE=/dev/null',  # we do not use it currently
                      'CMAKE_C_FLAGS=@0@'.format(' '.join(cflags)),
                      'CMAKE_CXX_FLAGS=@0@'.format(' '.join(cflags)),
                      f'CXX_STDLIB=@cxx_libs@',
                      'CMAKE_OBJCOPY=' + arm_objcopy.full_path(),
                      'CMAKE_C_COMPILER=' + gclang.full_path(),
                      'CMAKE_CXX_COMPILER=' + gclang_cpp.full_path(),
                      'CMAKE_ASM_COMPILER=' + arm_gcc.full_path(),
                      'CMAKE_AR=' + arm_ar.full_path(),
                      'CMAKE_RANLIB=' + arm_ranlib.full_path(),
                      'CMAKE_SIZE_UTIL=' + arm_size.full_path(),
                      'CMAKE_BUILD_TYPE=Debug',
    ],
  ],
)

pinetime_app = custom_target('pinetime-app',
  output: 'pinetime-app-0.15.0.ll',
  command: [
    llvm_dis, '-o', '@OUTPUT@', pinetime_app_bc,
  ], build_by_default: true
)

freertos_config = fs.copyfile(infinitime.get_variable('freertos_config'), 'FreeRTOSConfig.h')
