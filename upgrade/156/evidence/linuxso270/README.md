# Native x64 LinuxSO prerequisite on current master

The full x64 Chromium build against frozenSDK243 exposed a missing `linuxso.h` prerequisite. The existing native Widevine-loading path uses this static library to load Linux x86-64 shared objects; it was present in the earlier local port but absent from the newer AROS checkout.

The source was an untracked13-file snapshot in the old port. Its hashes and exact origin are recorded; it is not claimed to be part of the old91c96ef9 commit or an upstream merge. The included patch carries that snapshot onto private AROS master commit45657721 (parent e2331300), without modifying its implementation.

Its public header and static library build successfully against the newer master/toolchain. SDK270 retains SDK243 unchanged and adds only `include/linuxso.h` and `lib/liblinuxso.a`. No global SDK mmap implementation was added. The first two-target parallel MMAKE invocation raced makefile generation; the retained successful retry serialized those targets.

This establishes source and cross-build availability. It does not qualify native Widevine CDM loading, playback, DRM compatibility, or redistribution of proprietary CDM binaries. Chromium's existing detailed loader tracing remains enabled by its diagnostic settings. ARM does not use this x86-64 loader.
