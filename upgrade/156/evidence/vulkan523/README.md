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
Vulkan and EGL module builds524 pass on both architectures. Native CEF527 linking now passes on both architectures. Full-browser Vulkan,
physical RADV/NVK rendering and performance are not yet validated.
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

Matching refreshed-SDK V8 archives and native V8 images are being built as527.

## Native software Vulkan execution

Run533 adds the retained native Lavapipe module from packed198's OS staging
tree (Mesa26.2.7, LLVM20.1.0) to the diagnostic runtime. The loader exposes Vulkan
1.4.354, enumerates one CPU device and 165 device extensions, and completes
instance creation/destruction. ANGLE initializes EGL1.5 and reads the expected
RGBA pixel (64,128,191,255). Both probes return and the script finishes.

Run536 additionally renders four colour bars through ANGLE's Vulkan window
surface into a real Intuition window; SwapBuffers succeeds, the screenshot
captures the output, and normal cleanup returns after the 60-second display.
The retained driver and retained boot modules make this a diagnostic software
Vulkan result, not a fresh whole-platform build or hardware GPU qualification.

Companion aros-web commit `9507685` removes CEFHost's unconditional GPU-disable
flags. Native Ozone capability selection is the default; `--software-rendering`
retains an explicit diagnostic override. Both native host cross-links pass.
The rebuilt full browser with this default still requires runtime validation.

## Provisional full browser Vulkan checks

Companion `4cd6088` additionally selects ANGLE/Vulkan and passes the existing
AROS compositing opt-in, avoiding the separate legacy process-model GPU-disable
default. Both host541 cross-links pass. Software rendering remains explicit.

Run542 renders Chromium's New Tab page. Its GPU report identifies
`(gl=egl-angle,angle=vulkan)`, `ANGLE_VULKAN`, and Vulkan1.4.354 on llvmpipe26.2.7.
Compositing, Canvas and WebGL are enabled. The report's hardware-accelerated
labels describe Chromium's graphics path; this CPU Lavapipe run does not prove
physical GPU acceleration. Its separate Vulkan status is disabled because
the direct Vulkan path is not selected; ANGLE uses Vulkan underneath GL.

Run544 passes browser WebGL1 and WebGL2 shader compilation, linking, draw and
readPixels checks, each returning RGBA32/191/96/255. The fixture, console output
and screenshot are retained. The first fixture attempt543 exceeded the existing
2047-character launcher URL limit;544 uses a native file URL instead.

These browser runs intentionally use retained native490 V8 and master229 facade
and clients while matched-SDK V8 builds527 continue. They establish provisional
CEF527/host541 graphics integration, not a complete matched-build release.
Memory values are whole-guest samples for these particular pages and include
the software driver; neither browser RSS nor memory-plateau acceptance.
