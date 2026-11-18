# Native AArch64 desktop in Raspberry Pi 4 emulation

Wanderer and About AROS boot on the private two-active-core kernel based on master 51de4166, with private OS fixes through bfdbbd7c. This is QEMU evidence, not a physical Pi result.

The idle Exec AvailMem sample records 1,000,279,888 bytes total, 987,211,296 free and 13,068,592 used. This is system-wide accounting; no Chromium memory measurement or ARM first-paint claim is made here.

The first browser launcher failed because stdcio.library had not been included in the staged runtime. The subsequent dependency audit also identified posixc.library and the ARM-specific debug.library under boot/raspi-smp/Libs. All three are staged for replay 8; first paint remains pending. task.resource is already linked into core.elf; it must not be added again as a standalone BSP module.

The staging script now writes the architecture signature AROS.boot. It preserves the AUX mountlist under S: so AROS can create its reserved DOS filename during startup (mtools rejects AUX). The temporary DOS/SD diagnostic source patch is retained here and was removed from the source after identifying the staging issue; the captured guest used the diagnostic BSP.

Replay 10 corrects the private QEMU device tree to advertise the upper GiB that the emulator already allocates. Native Exec accounting reports 2,074,013,344 bytes usable, 2,059,877,568 free and 14,135,776 used with Wanderer and About open. This is still desktop accounting, not a browser footprint. The QEMU physical map and read-back verification confirmed the diagnostic range before boot. No AROS memory-discovery source change was required.

The original ARM engine contains CALL26/JUMP26 displacements around 237 MB, exceeding the 128 MiB instruction limit. A private final-link experiment using LLVM PIC veneers and a compact native relocatable image loads successfully in replay 11: the CEF shared heap installs, cef_execute_process returns -1 for the browser process, and the client window opens. The module file is 495,681,888 bytes; that is a disk artifact size, not RAM usage. Full page rendering is still unproven.

Replay 11 then faults in the AHI unit process at MMIO address 0xfef20010, which the emulated Pi does not implement. Replay 12 moves only the private guest's RPIHDMI/RPII2S/RPIPWM mode files into Storage; physical-hardware drivers and source remain unchanged. The retained failure screenshot is a client window plus an audio fault, not Chromium first paint.

## Replay 13: native ARM page rendering

Integrated ARM-only linker/compact-image support is published in `aros-web` commit `3197f26`. Replay 13 uses that build (module SHA256 `38414baff7981b490af790f8052760517ba1d2474f0c7abde60c20b4010a6abb`). The native image fixture passes, CEF initializes, the browser is created, the 960x540 first-paint callback fires, and the local data-URL page completes with status 200. The screenshot is the CEF test browser using Chromium 156; it is not the full Chrome user interface or Internet access validation.

Replay 12 exposed a separate packaging requirement: DOS had cached a null debug.library base before the library became available on disk, so V8 symbol enumeration visited zero symbols. Replay 13 includes debug.library in the BSP using the existing build option `PKG_LIBS_ARCH='expansion debug'`. Native enumeration now visits 311025 symbols and indexes 272298. No SDK or kernel source change was needed for that requirement.

Native Exec AvailMem reports 1977.93 MiB usable, 1396.26 MiB used and 581.67 MiB free after rendering, versus 14.09 MiB used at the desktop baseline. These are whole-guest measurements including diagnostic symbol metadata and shared libraries; they are not exclusive application attribution. Usage is effectively unchanged from the 180s through 480s samples. The module's 472.7 MiB file size is a separate disk measurement.

About AROS is open behind the browser in this capture. ARM input, complete teardown, physical Pi execution, and network access remain unqualified at this evidence point. Earlier failures and screenshots above are retained as historical stages, not current first-paint blockers.
