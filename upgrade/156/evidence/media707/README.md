# Native media cleanup and playback verification

Runtime704 uses the media703 x64 engine, current674 OS, resolver697, e1000,
two CPUs, 4 GiB RAM and emulated HDA output. Engine hash and commands are in
`x64-build.json`.

## Fix and replay

Shaka4032 means unsupported codecs/container. Separately, renderer shutdown
aborted in InterfaceEndpointClient because MojoCodecFactory was destroyed on
the renderer main sequence. The patch releases GPU media factories on their
media sequence after Blink isolate retirement while the scheduler survives.

Apply `renderer-media-cleanup.patch` with git apply to the current156 Chromium
source after the existing patches. Exact replay against the pre-change file,
x64 CEF archive/native linking, and ARM renderer translation compilation pass.
ARM compilation is not ARM native playback evidence.

## Native x64 results

- VP9 MSE playback, seek to0.5s and replay:164 frames,30 dropped.
- VP8 MSE playback, seek and replay:152 frames,27 dropped.
- Closing the former video tab releases factories on the media sequence without
  the earlier fatal abort.
- Opus MSE playback, seek and replay complete. A user-gesture unmute produces
  nonzero HDA output samples captured by QEMU; audio-sample-check.json records a
  bounded snapshot. The WAV is retained privately.
- Capability probes: VP8/VP9/Opus supported; H264/AAC unsupported.

Chromium media/test/data fixtures are hashed in fixtures.json. VP9 came from
public Chromium main; the other fixtures came from the pinned local source.
Console excerpts and screenshots are included.

## Limits

QEMU evidence only: no physical hardware, ARM playback, performance qualification
or protected Widevine playback claim. Dropped frames remain significant. An
older VM without a sound card stalled Opus at metadata. H264/AAC integration is
a separate unfinished build and is not part of this fix. No RC is claimed.
