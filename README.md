# Build InfiniTime with gllvm

Needs a working ARM Toolchain and Clang/LLVM 14.

To deploy on Gentoo, install an 'arm-none-eabi' Toolchain and call with:
```
echo "[binaries]\nllvm_config = '/usr/lib/llvm/14/bin/llvm-config'" > native.txt
meson setup build -D toolchains:arm_libs=/usr/arm-none-eabi --native-file native.txt
cd build; meson compile pinetime-app -v
```
