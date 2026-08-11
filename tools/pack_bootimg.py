#!/usr/bin/env python3
"""Pack an ANDROID! boot image (mkbootimg v0 format) for the SM-J105F.

Layout (decoded from the stock recovery/boot images of this device):
  [header 2048][kernel][pad to 2048][ramdisk][pad to 2048][dt.img][SEANDROIDENFORCE][pad to 2048]

Header fields (all little-endian, v0 header, 48 bytes + name[16] + cmdline[512] + id[20]):
  magic "ANDROID!", kernel_size, kernel_addr=0x00008000, ramdisk_size,
  ramdisk_addr=0x01000000, second_size=0, second_addr=0x00F00000,
  tags_addr=0x00000100, page_size=2048, dt_size=<len(dt.img)>, unused=0,
  name zeros, cmdline "console=ttyS1,115200n8", id[20].

dt.img (SPRD table, see pack_dtimg.py) is appended directly after the
page-aligned ramdisk. The 20-byte id at header offset 576 is the SHA1
computed exactly like the era's mkbootimg (omnirom android-6.0
system/core, the tool that built this device's recovery image):
  sha1(kernel || LE32(kernel_size) || ramdisk || LE32(ramdisk_size)
       || second || LE32(second_size) || dt || LE32(dt_size))

With --seandroid (default) the literal string "SEANDROIDENFORCE" is
appended after dt.img and the whole image is zero-padded to the page
boundary, matching Samsung's stock boot images. The stock recovery image
carries no SEANDROIDENFORCE, so the packer's round-trip test uses
--no-seandroid.

Usage:
  pack_bootimg.py --kernel zImage --ramdisk ramdisk.cpio.gz --dt dt.img --out boot.img
  pack_bootimg.py --kernel zImage --ramdisk ramdisk.cpio.gz --dt dt.img \
      --out boot.img --no-seandroid   # recovery-style, no suffix
"""

import argparse
import hashlib
import struct
import sys

PAGE = 2048
HEADER_FMT = "<8sIIIIIIIIII16s512s20s"  # magic + 10 u32 + name + cmdline + id
MAGIC = b"ANDROID!"
DEFAULT_CMDLINE = b"console=ttyS1,115200n8"
SEANDROID = b"SEANDROIDENFORCE"


def align(n, page=PAGE):
    return ((n + page - 1) // page) * page


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kernel", required=True, help="zImage path")
    ap.add_argument("--ramdisk", required=True, help="ramdisk (cpio.gz) path")
    ap.add_argument("--dt", required=True, help="dt.img path (SPRD table)")
    ap.add_argument("--out", required=True, help="output boot.img path")
    ap.add_argument(
        "--cmdline",
        default=DEFAULT_CMDLINE.decode(),
        help="kernel cmdline (default: console=ttyS1,115200n8)",
    )
    ap.add_argument("--page", type=int, default=PAGE)
    ap.add_argument("--kernel-addr", type=lambda x: int(x, 0), default=0x00008000)
    ap.add_argument("--ramdisk-addr", type=lambda x: int(x, 0), default=0x01000000)
    ap.add_argument("--second-addr", type=lambda x: int(x, 0), default=0x00F00000)
    ap.add_argument("--tags-addr", type=lambda x: int(x, 0), default=0x00000100)
    ap.add_argument(
        "--no-seandroid",
        action="store_true",
        help="do NOT append SEANDROIDENFORCE + page padding",
    )
    args = ap.parse_args(argv)

    kernel = open(args.kernel, "rb").read()
    ramdisk = open(args.ramdisk, "rb").read()
    dtimg = open(args.dt, "rb").read()
    if ramdisk[:2] != b"\x1f\x8b":
        sys.exit(f"{args.ramdisk}: not gzip (magic {ramdisk[:2]!r})")
    if dtimg[:4] not in (b"SPRD", b"\xd7\xb7\xab\x1e"):
        sys.exit(f"{args.dt}: unknown dt.img magic {dtimg[:4]!r}")

    cmdline = args.cmdline.encode() + b"\0"
    if len(cmdline) > 512:
        sys.exit("cmdline too long")

    # id = sha1(kernel||szk||ramdisk||szr||second||szs||dt||szd), exactly
    # like the mkbootimg that built this device's recovery image.
    h = hashlib.sha1()
    h.update(kernel)
    h.update(struct.pack("<I", len(kernel)))
    h.update(ramdisk)
    h.update(struct.pack("<I", len(ramdisk)))
    h.update(b"")
    h.update(struct.pack("<I", 0))
    h.update(dtimg)
    h.update(struct.pack("<I", len(dtimg)))
    img_id = h.digest()

    header = struct.pack(
        HEADER_FMT,
        MAGIC,
        len(kernel),
        args.kernel_addr,
        len(ramdisk),
        args.ramdisk_addr,
        0,
        args.second_addr,  # second_size, second_addr
        args.tags_addr,
        args.page,
        len(dtimg),  # dt_size, as on the device images
        0,  # unused
        b"\0" * 16,
        cmdline,
        img_id,
    )
    assert len(header) == 48 + 16 + 512 + 20

    img = bytearray(align(len(header), args.page))
    img[0 : len(header)] = header
    img += kernel
    img += b"\0" * (align(len(kernel), args.page) - len(kernel))
    img += ramdisk
    img += b"\0" * (align(len(ramdisk), args.page) - len(ramdisk))
    img += dtimg

    if not args.no_seandroid:
        img += SEANDROID
        img += b"\0" * (align(len(img), args.page) - len(img))

    open(args.out, "wb").write(bytes(img))
    suffix = ", SEANDROIDENFORCE suffix)" if not args.no_seandroid else ")"
    print(
        f"wrote {args.out}: {len(img)} bytes"
        f" (kernel {len(kernel)}, ramdisk {len(ramdisk)}, dt.img {len(dtimg)}{suffix}"
    )


if __name__ == "__main__":
    main(sys.argv[1:])
