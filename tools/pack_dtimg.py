#!/usr/bin/env python3
"""Build a Spreadtrum dt.img (SPRD table) the way dtbTool-sprd does.

Inverse of the SPRD branch of tools/parse_bootimg.py. Format decoded from
the device ground truth (twrp prebuilt/dtb, 0x50800 bytes, dd'd from the
phone; byte-identical to the dt.img section of the stock recovery image):

  offset 0x000  "SPRD" magic (4)
                 version u32 LE = 1
                 count   u32 LE = N
                 count x 20-byte entries:
                   [tag u32 LE][index u32 LE][flag u32 LE]
                   [slot_off u32 LE][slot_sz u32 LE]
                 (observed on device: tag=0x2666 (9830, the SoC "sc-id"),
                  index=i (slot order), flag=0x20000, slot_off=0x800+i*0x10000,
                  slot_sz=0x10000)
  offset 0x070..0x800  zero padding
  offset 0x800 + i*0x10000  slot i: raw DTB bytes, zero-padded to slot size

Each slot packs the compiled .dtb unmodified, zero-padded; parse_bootimg.py
recovers it by trimming at the DTB's declared total size.

Usage:
  pack_dtimg.py --out dt.img dtb_00.dtb dtb_01.dtb ... dtb_04.dtb
  pack_dtimg.py --out dt.img --verify-dtb tests/stock-dtb <5 dtbs>
    (--verify-dtb byte-compares every packed slot against <dir>/dtb_0N.dtb
     and exits non-zero on any mismatch - FAIL-CLOSED gate)
  pack_dtimg.py --out dt.img --compare-dtb tests/stock-dtb <5 dtbs>
    (--compare-dtb prints the same per-slot comparison but is DIAGNOSTIC
     ONLY: mismatches are reported, never fatal - for kernel-built dtbs
     that are expected to differ from the stock device dtbs)
"""

import argparse
import os
import struct
import sys

SPRD_MAGIC = b"SPRD"
VERSION = 1
DEFAULT_TAG = 0x2666  # 9830 = sprd,sc-id[0] of the SC8830/SC9830 family
DEFAULT_FLAG = 0x20000  # sc-id[2] observed on device
TABLE_BASE = 0x800  # table head + padding area size
SLOT_SIZE = 0x10000  # per-slot size on device
SLOT_STRIDE = 0x10000


def align(n, page):
    return ((n + page - 1) // page) * page


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dtbs", nargs="+", help="compiled .dtb files in slot order")
    ap.add_argument("--out", required=True, help="output dt.img path")
    ap.add_argument("--tag", type=lambda x: int(x, 0), default=DEFAULT_TAG)
    ap.add_argument("--flag", type=lambda x: int(x, 0), default=DEFAULT_FLAG)
    ap.add_argument("--slot-size", type=lambda x: int(x, 0), default=SLOT_SIZE)
    ap.add_argument(
        "--verify-dtb",
        metavar="DIR",
        help="byte-compare each packed DTB against DIR/dtb_0N.dtb; "
        "exit non-zero on any mismatch (fail-closed gate)",
    )
    ap.add_argument(
        "--compare-dtb",
        metavar="DIR",
        help="diagnostic: same per-slot comparison but non-gating - "
        "mismatches are printed in a summary, exit is always 0",
    )
    args = ap.parse_args(argv)

    if len(args.dtbs) > 128:
        sys.exit("refusing to pack >128 dtbs")

    count = len(args.dtbs)
    total = TABLE_BASE + count * args.slot_size

    blob = bytearray(total)
    blob[0:4] = SPRD_MAGIC
    struct.pack_into("<I", blob, 4, VERSION)
    struct.pack_into("<I", blob, 8, count)

    for i, path in enumerate(args.dtbs):
        dtb = open(path, "rb").read()
        if dtb[0:4] != b"\xd0\x0d\xfe\xed":
            sys.exit(f"{path}: not a DTB (magic {dtb[0:4]!r})")
        if len(dtb) > args.slot_size:
            sys.exit(f"{path}: {len(dtb)} bytes exceeds slot size 0x{args.slot_size:x}")
        base = 12 + i * 20
        struct.pack_into(
            "<IIIII",
            blob,
            base,
            args.tag,
            i,
            args.flag,
            TABLE_BASE + i * args.slot_size,
            args.slot_size,
        )
        slot = TABLE_BASE + i * args.slot_size
        blob[slot : slot + len(dtb)] = dtb

    open(args.out, "wb").write(bytes(blob))
    print(
        f"wrote {args.out}: {total} bytes, {count} slot(s)"
        f" [tag=0x{args.tag:x} flag=0x{args.flag:x} slot=0x{args.slot_size:x}]"
    )

    if args.verify_dtb or args.compare_dtb:
        ok = True
        n_same = 0
        for i, path in enumerate(args.dtbs):
            stock = os.path.join(
                args.verify_dtb or args.compare_dtb, f"dtb_{i:02d}.dtb"
            )
            if not os.path.exists(stock):
                print(f"FAIL: {stock} missing")
                ok = False
                continue
            a = open(path, "rb").read()
            b = open(stock, "rb").read()
            same = a == b
            n_same += 1 if same else 0
            d = next((o for o in range(min(len(a), len(b))) if a[o] != b[o]), None)
            print(
                f"  slot {i}: {os.path.basename(path)} vs {os.path.basename(stock)}: "
                f"{'IDENTICAL' if same else 'MISMATCH'} "
                f"({len(a)}/{len(b)} bytes"
                + ("" if same else f", first diff @ 0x{d:x}")
                + ")"
            )
            ok = ok and same
        if args.verify_dtb and not ok:
            sys.exit("dtb verification FAILED (see per-slot lines above)")
        if args.verify_dtb:
            print("dtb verification OK: all packed DTBs byte-identical to stock")
        if args.compare_dtb:
            print(
                f"dtb comparison (DIAGNOSTIC, non-gating): {n_same}/{len(args.dtbs)} "
                "slots identical to stock; mismatches are expected for kernel-built "
                "dtbs (in-tree dtc 1.2.0 vs the device's toolchain) and are reported "
                "only - job continues"
            )


if __name__ == "__main__":
    main(sys.argv[1:])
