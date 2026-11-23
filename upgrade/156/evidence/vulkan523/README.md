# Native AROS Vulkan integration (source519 / snapshot523)

Mesa and Vulkan are baseline AROS infrastructure. ANGLE now creates AROS Vulkan
window surfaces, links the native Vulkan import library, and is selected through
AROS Ozone. Device format capabilities come from the selected Vulkan device;
there is no forced llvmpipe/Lavapipe selection.

The Android/Linux sync-file polling helper is excluded on AROS. Normal Vulkan
fence waits remain in use, and the Android native-fence extension is not advertised.

## Verified

- x64 ANGLE Vulkan backend and both changed Ozone objects compile against SDK510.
- Native Vulkan loader ABI probe cross-links against SDK510.
- ARM514 targeted backend/Ozone compilation passes for preceding source511.
- The x64 ANGLE Vulkan pbuffer probe521 cross-links with source519.
- GCC atomic adapter passes a four-thread host test of aligned/misaligned 16-byte CAS. The native object imports only memcpy/memcmp; this is not native atomic runtime proof.
- The refreshed x64 kernel builds after removing five invalid native SMP ExecBase mappings from the private 68k shadow table.
- The source snapshot replays against all 21 recorded repository bases.

Source519 additionally resolves optional surface extension queries per Vulkan instance,
builds driver-version parsing, and adapts compiler-rt atomics to native GCC builtins.
The GN standalone shared-library test target reaches only an unresolved main: AROS
uses its native library packaging instead. Probe521 supplies a real EGL/pbuffer
entry point and links successfully. Full CEF526 archives pass on both architectures after generating the missing
credentials-library SDK exports (native module builds525 also pass). Native Mesa,
Vulkan and EGL module builds524 pass on both architectures. Native Vulkan engine linking,
presentation, physical RADV/NVK rendering and performance are not yet validated.
This is development source, not an RC or binary release.

## Separate existing software-rendering results

Native490 x64 run497 passes 100 renderer retirements and independent native child
entry/exit accounting. Whole-guest memory grows 150.830 MiB from cycles 30 to 100;
there is no memory-plateau pass. Native490 ARM run501 times out during repeated
sessions without a recorded native fault. These results do not validate source511
or Vulkan rendering. The older visual ARM494 proof remains in candidate508.

## Native runtime controls (November 23)

The fresh-master528 overlay stops during boot with a TLSF free-list diagnostic,
before either graphics probe. This is retained as a failed OS integration run.

On the retained bootable master247 OS, with fresh graphics libraries, run530
reaches both probes. The native loader reports API 1.0.0 and instance creation
returns VK_ERROR_INCOMPATIBLE_DRIVER (-9). ANGLE returns EGL_NOT_INITIALIZED
(0x3001). Both probes return to the shell and About AROS opens afterward; no native
fault appears in the captured serial. The standard VGA QEMU setup has no qualified
Vulkan device. This is negative capability/error handling evidence, not successful
Vulkan rendering or qualification of the new OS build.

Matching refreshed-SDK V8 archives and native CEF/V8 images are being built as527.
