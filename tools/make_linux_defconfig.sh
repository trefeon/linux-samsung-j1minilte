#!/bin/sh
# Regenerate arch/arm/configs/j1minilte_linux_defconfig from the vendor
# j1minilte_defconfig. Uses only the kernel's own scripts/config (pure
# shell) - no compiler needed. The committed file is the direct output of
# this script; CI then runs `make olddefconfig` to resolve any Kconfig
# dependencies (none currently - see commit message).
#
# Usage (from the kernel root):  sh tools/make_linux_defconfig.sh
set -e

cd "$(dirname "$0")/.."

cp arch/arm/configs/j1minilte_defconfig .config
./scripts/config \
    --enable DEVTMPFS \
    --enable DEVTMPFS_MOUNT \
    --enable VT \
    --enable VT_CONSOLE \
    --enable FRAMEBUFFER_CONSOLE
cp .config arch/arm/configs/j1minilte_linux_defconfig
rm -f .config

echo "wrote arch/arm/configs/j1minilte_linux_defconfig"
