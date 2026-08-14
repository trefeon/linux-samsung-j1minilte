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

## Confirmed hardware identity (2026-08-14)

The target device is an **SM-J105F/DS** (Galaxy J1 Mini 4G / "J1 Nxt"),
codename `j1minilte` / `j1miniltexx`, CSC **XID (Indonesia)**, dual-SIM.

- SoC: **SC9830I** (Spreadtrum SharkLS, **SCX35L LTE family** — same silicon
  line spec sites call SC9830A), board **SP8835EB**, 1 GB RAM, 1.5 GHz.
- The `sc8830` strings (`ro.board.platform`, `ro.hardware`, cpuinfo, dmesg
  "Machine: sc8830", `SP8835EB`) are the **platform-family name shared by the
  whole SCX35(L) family** — they do NOT mean the 3G-only SC8830 chip.
- The 3G sibling (SM-J105H/B, `j1mini3g`) is a **different kernel platform**
  (`CONFIG_ARCH_SCX30G`) — its config/DTBs are NOT a base for this unit.
- The Linux-port base is correctly on the LTE/SC9830i config:
  `CONFIG_ARCH_SCX35L=y`, `CONFIG_MACH_J1MINILTE=y`, `CONFIG_MACH_SP9830I=y`,
  `CONFIG_SIPC_LTE=y`, `# CONFIG_SPRD_MODEM_TD is not set`, `CONFIG_FB_SCX35L=y`
  (see `j1minilte_linux_defconfig`).
- Evidence: `device/evidence/getprop.txt` (`ro.chipname=SC9830I`,
  `ro.product.hardware=SS_SHARKLS`, modem mode incl. TD-LTE/FDD-LTE),
  `device/evidence/byname.txt` (LTE modem partition set `l_modem`/`l_fixnv`/
  `l_runtimenv`), `device/evidence/dmesg.txt`, and the stock boot DTS
  (`sprd,sc-id = <0x2666 …>` = 9830 decimal). Full analysis:
  `docs/research/exact-model-findings.md` in the main Project_J105F repo.

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
