# Corrected-engine encrypted playback validation

The source749 engine completed an uninterrupted 733.999-second encrypted VP9/Vorbis replay in native x86-64 AROS under QEMU, with audio enabled. The browser used the external Widevine 4.10.3112.0 module through linuxso and the graphics741 WaitTOF correction.

The replay advanced from 0.256665 seconds to the endpoint without another seek or pause command. Periodic samples show 17,606 additional frames and 200 additional dropped frames. No harness error or native fault marker was observed during that interval. The earlier session included seeking and a background-tab pause; those are not included in this full-replay claim.

The live audio capture contains 75,835,054 nonzero signed 16-bit samples across the session, with peak magnitude 16,384. This proves generated guest PCM, not physical audio output. Memory samples are whole-guest usage, filtered for internally consistent counters; they are not engine-only measurements.

![Encrypted playback in native AROS](playing747.png)

![Replay reaches the endpoint](replay747.png)

## Other checks and limits

- The independent native HTTP range/cache fixture completed 40 content-verified requests, including overlapping ranges and concurrent requests.
- ARM751 completes the full archive and native link for source749. Its new runtime test is still pending; this is build proof only.
- Intermittent real-stream cache errors remain. A later private diagnostic build identifies a blockfile range query while another sparse operation is active; the fix is still under investigation.
- Encrypted H.264 playback is under separate testing and is not included in this full-film result.
- No proprietary CDM, profiles, audio or RAM dumps are redistributed. This is validation evidence for an in-progress port, not an RC release.
