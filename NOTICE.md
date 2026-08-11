# NOTICE — Linux kernel source provenance

This repository contains the Linux kernel source for the Samsung Galaxy J1 Mini
(SM-J105F, codename "j1minilte"), imported for the Project J105F Linux port
(kernel foundation milestone M3.x).

## Source lineage

- Vendor: Samsung Electronics opensource release for SM-J105F (Android 5.1.x,
  kernel 3.10.x), redistributed via community mirrors (NotNoelChannel /
  MayuriLabs) — GPL-2.0.
- Imported blob-identical from the Project J105F TWRP repository
  (trefeon/twrp_j1minilte @ 4908f45a, path kernel/samsung/j1minilte), where it
  is already committed and CI-proven: its 5 SP8835EB device-tree blobs are
  byte-identical to the device's stock DTBs.
- The archived postmarketOS recipe `linux-samsung-j1mini3g` (postmarketOS,
  GPL-2.0, source IKGapirov/android_kernel_samsung_j1mini3g @ 6a377f7) is the
  reference for GCC-compat and SPRD framebuffer patches applied in later
  milestones. See `docs/plans/linux-kernel-foundation-plan.md` (main repo).

## Vendor CI workflow

`.github/workflows/main.yml` is the upstream vendor CI ("CyanogenMod Kernel
CI", manual `workflow_dispatch` only) and is retained for provenance. The
Project J105F build workflow is `.github/workflows/kernel.yml` (added by the
project; see README.md).

## Windows NTFS note

13 paths (12 case-variant headers/sources + `drivers/gpu/drm/nouveau/core/
subdev/i2c/aux.c`, an NTFS reserved name) are tracked with the skip-worktree
bit in the local index on Windows only. They exist as regular files in the
committed tree; Linux/CI checkouts are unaffected.

## License

The kernel is GPL-2.0. See `COPYING` in the tree. No proprietary or
unreviewed vendor blobs are included; only kernel source.
