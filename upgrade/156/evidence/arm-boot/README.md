# AArch64 boot progress

Private QEMU 10.2.1 raspi4b boot with two active AROS cores reaches the boot logo and SD-card detection after the secondary stack-entry repair. This is emulation evidence, not a physical Raspberry Pi result. The desktop, CEF browser and application memory readings remain pending.

The diagnostic CPU-limit patch is build-only test scaffolding, not a proposed SDK policy. The baseline exposes 960 MiB through the live device tree even though QEMU is configured with 2 GiB.

The two sibling OS patches in ../../aros address GCC 16 declarations and the measured secondary-core stack transition. They are committed in the private OS checkout; they have not been pushed to upstream AROS.
