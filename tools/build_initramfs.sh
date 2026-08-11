#!/bin/sh
# Build the milestone-1 debug initramfs: static armv7 busybox + initramfs/init.
#
# Requires (CI installs these): gcc-arm-linux-gnueabi, cpio, bzip2, curl
# (or wget), make, and a host gcc for busybox's host tools.
#
# Usage:  sh tools/build_initramfs.sh            (from kernel root)
# Output: ramdisk.cpio.gz  (kernel root)  +  build_initramfs/ work dir
set -e

VERSION=1.36.1
# sha512 measured locally on download and cross-checked against the
# official busybox.net sha256 sidecar (b8cc24c9...e47de314).
SHA512=8c0c754c9ae04b5e6b23596283a7d3a4ef96225fe179f92d6f6a99c69c0caa95b1aa56c267f52d7c807f6cc69e1f0b7dd29a8ac624098f601738f8c0c57980d4
URL=https://busybox.net/downloads/busybox-$VERSION.tar.bz2

ROOT=$(cd "$(dirname "$0")/.." && pwd)
WORK=${1:-$ROOT/build_initramfs}
STAGE=$WORK/rootfs
OUT=$ROOT/ramdisk.cpio.gz

mkdir -p "$WORK"
cd "$WORK"

# --- fetch + verify -----------------------------------------------------
if [ ! -f busybox-$VERSION.tar.bz2 ]; then
    echo "== downloading $URL"
    (curl -fsSL -o busybox-$VERSION.tar.bz2 "$URL") || \
        (wget -q -O busybox-$VERSION.tar.bz2 "$URL") || {
        echo "ERROR: could not download busybox"; exit 1; }
fi
echo "== verifying sha512 of busybox-$VERSION.tar.bz2"
echo "$SHA512  busybox-$VERSION.tar.bz2" | sha512sum -c -

# --- build --------------------------------------------------------------
rm -rf busybox-$VERSION "$STAGE"
tar xjf busybox-$VERSION.tar.bz2
cd busybox-$VERSION

echo "== configuring busybox (defconfig + CONFIG_STATIC)"
make defconfig >/dev/null
# busybox 1.36.1 no longer ships scripts/config; enable STATIC via .config
sed -i 's/^# CONFIG_STATIC is not set$/CONFIG_STATIC=y/' .config
grep -q '^CONFIG_STATIC=y' .config || echo 'CONFIG_STATIC=y' >> .config
# busybox 1.36.1 kconfig has no olddefconfig target; pipe defaults.
yes "" | make oldconfig >/dev/null
grep -q '^CONFIG_STATIC=y' .config || {
    echo "ERROR: CONFIG_STATIC not enabled in .config"; exit 1; }
echo "CONFIG_STATIC=y confirmed in .config"

echo "== building busybox (static, arm-linux-gnueabi)"
make -j"$(nproc)" CROSS_COMPILE=arm-linux-gnueabi-

echo "== installing to staging root"
make CONFIG_PREFIX="$STAGE" install

# --- assemble initramfs -------------------------------------------------
cp "$ROOT/initramfs/init" "$STAGE/init"
chmod +x "$STAGE/init"

echo "== packing ramdisk.cpio.gz"
cd "$STAGE"
find . -print | cpio -o -H newc 2>/dev/null | gzip -9 > "$OUT"

echo "== done"
ls -la "$OUT"
echo "busybox version: $VERSION ($($STAGE/bin/busybox --version 2>/dev/null || echo n/a))"
