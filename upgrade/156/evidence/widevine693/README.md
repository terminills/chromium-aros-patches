# Native external Widevine initialization — 2026-11-27

Native x64 Chromium156 now loads the external Widevine CDM through LinuxSO and completes six CDM initializations on the HTTPS Shaka support page. Opening the demo then adds six more successful initializations (twelve in the retained log snapshot). The page reports com.widevine.alpha, cenc/cbcs, SW_SECURE_CRYPTO and SW_SECURE_DECODE. No native fault or failed mapping was observed in this capture. See runtime-result.json and native-widevine-support.png. This is initialization evidence, **not protected playback qualification**. Persistent CDM state is reported false. H.264/AAC are not enabled in the tested engine.

Apply chromium-discovery.patch after the published source602 queue (the registration file was unchanged through624). It enables local CDM directory discovery on AROS x64 even when bundled-CDM and component-updater flags are off. ARM translation compiled successfully with the x64-only feature excluded.

Apply linuxso-mapping.patch after the consolidated master682 AROS prerequisite patch, on upstream28fbd1d6. It corrects LinuxSO's reversed KrnMapGlobal success test: AROS returns nonzero on success. The earlier runtime690 reached the external module's fatal UD2 after a successful map was treated as failure. The corrected run preserves the existing 2 MiB backing chunks and does not add generic SDK mmap. Both LinuxSO compilation and the full native engine link pass.

The test uses the local external CDM version4.10.2934.0 under SYS:System/CEF/WidevineCdm/_platform_specific/linux_x64/libwidevinecdm.so, with its manifest beside the platform directory. CEF resources are rooted at SYS:System/CEF. The proprietary module is not included in this repository or release artifacts. Enable AROS_WIDEVINE_DEBUG and LINUXSO_DEBUG for the native trace; they are environment settings, not CEFHost command-line arguments.

Matched inputs: latest master674 x64 OS, CEF/V8 archives624 plus registration684, native loader691, companion binaries candidate634. Frozen SDK623 was not modified. Browser is left running privately for user playback testing. No RC release is claimed.
