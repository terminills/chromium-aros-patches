# Native AArch64 desktop in Raspberry Pi 4 emulation

Wanderer and About AROS boot on the private two-active-core kernel based on master 51de4166, with private OS fixes through bfdbbd7c. This is QEMU evidence, not a physical Pi result.

The idle Exec AvailMem sample records 1,000,279,888 bytes total, 987,211,296 free and 13,068,592 used. This is system-wide accounting; no Chromium memory measurement or ARM first-paint claim is made here.

The first browser launcher failed because stdcio.library had not been included in the staged runtime. The subsequent dependency audit also identified posixc.library and the ARM-specific debug.library under boot/raspi-smp/Libs. All three are staged for replay 8; first paint remains pending. task.resource is already linked into core.elf; it must not be added again as a standalone BSP module.

The staging script now writes the architecture signature AROS.boot. It preserves the AUX mountlist under S: so AROS can create its reserved DOS filename during startup (mtools rejects AUX). The temporary DOS/SD diagnostic source patch is retained here and was removed from the source after identifying the staging issue; the captured guest used the diagnostic BSP.
