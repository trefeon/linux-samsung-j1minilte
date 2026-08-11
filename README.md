# linux-samsung-j1minilte

Samsung Galaxy J1 Mini (SM-J105F, "j1minilte") Linux kernel — vendor 3.10.x
source for the Project J105F Linux port (kernel foundation milestone M3.x).

## Status

- Milestone M3.1 (reproducible kernel build + DTB byte-match gate): in progress.
- The kernel already boots on this device as part of the custom TWRP recovery
  (see trefeon/twrp_j1minilte): its 5 SP8835EB DTBs are byte-identical to the
  device's stock DTBs.
- This tree is the Linux-port kernel: same vendor source, with the Linux
  bring-up config deltas (framebuffer console, devtmpfs) applied on top.

## Layout

- `arch/arm/configs/j1minilte_defconfig` — device config (baseline).
- `tests/stock-dtb/` — stock device DTBs (5, SP8835EB), used by CI as the
  byte-compare gate for the built `dt.img`.
- `.github/workflows/kernel.yml` — project build workflow (builds zImage +
  dt.img + busybox initramfs + boot.img, verifies, publishes artifacts).
- `.github/workflows/main.yml` — upstream vendor CI, retained for provenance
  (manual trigger only).

## Building (CI)

See `.github/workflows/kernel.yml`. Toolchain: AOSP `arm-eabi-4.8`
(android-5.1.1_r38 prebuilt, same as the TWRP CI). Artifacts: `zImage`,
`dt.img`, `ramdisk.cpio.gz` (initramfs), `boot.img`, `.config`, `SHA256SUMS`,
`BUILD_INFO.txt`.

## Windows NTFS note

13 paths are skip-worktree in the local index (NTFS case/reserved-name
limitations); they are normal files in the committed tree — CI/Linux
checkouts unaffected. See NOTICE.md.

## License

GPL-2.0 (see COPYING). Vendor source attribution in NOTICE.md.
