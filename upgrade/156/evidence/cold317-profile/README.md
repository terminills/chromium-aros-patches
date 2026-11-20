# Cold-boot profile persistence

The current native x64 browser reads both synthetic localStorage and a persistent cookie after a full VM shutdown and fresh boot. The source browser closed with callbacks drained, then the test waited for background writes before powering off its private VM. The resident engine is not claimed to have shut down gracefully.

The cold guest uses a byte-identical clone of the saved disk and the same engine/client binaries. Its startup requires the existing profile directory. The test only reads: no fixture write executes during the new boot. The screenshot and serial show READ PASS for the original MASTER312 token.

This validates synthetic browser storage across reboot in native AROS QEMU. It does not validate a real account sign-in, physical hardware, or every password-manager workflow. No profile disk, keyring seed, or user credentials are published. Memory plateau, ARM browser and other RC gates remain open.
