# Native Chromium156 HTTP transport validation — 2026-11-18

Native x86-64 AROS QEMU, one CPU, 4 GiB, PCnet with user networking. Same integrated CEF image SHA e4cfdcd88c9c1a582455aa38f66f598d24c94de818ff0c3707e0d9ee457de6d5 and shared V8 as the preceding memory/worker runs.

Run76 starts AROSTCP with its native IPv4/IPv6 modules, then loads http://10.0.2.2:40255/. The retained host fixture serves HTML, JSON and a worker script; all three HTTP requests return200. The page fetches the JSON marker, loads the worker, and verifies that its WebAssembly export returns42. Native serial and screenshot both report AROS_HTTP_ENGINE_PASS. Browser close and full CEFShutdown return. An unrelated favicon request returns404.

First paint uses1539.82MiB measured by native Exec AvailMem across the whole guest, including TCP stack and desktop; not exclusive engine residency or host RSS. Raw private logs are retained; public serial is normalized only for CRLF/trailing whitespace.

The preceding run75 intentionally retained here failed before transport: Run redirected to DEBUG: reports filesystem action type unknown, WaitForPort returns5, bsdsocket.library is unavailable and Chromium shows ERR_INTERNET_DISCONNECTED (-106). Run76 redirects stack output to a RAM file and reads it separately, allowing AROSTCP to start. This diagnostic-launch correction does not change the Chromium or SDK networking implementation.

This run proves local HTTP transport through the native guest stack. It does not qualify external DNS/TLS, arbitrary websites, ARM networking, profile isolation, Widevine or production sandboxing. Separate HTTPS evidence will be recorded if tested.

Run77 separately loads https://example.com/ using native DNS/TCP/TLS, reports HTTP200 and returns from full CEFShutdown. Startup and client use no certificate-bypass flag. The actual guest screenshot shows the external page; some non-Latin glyphs are absent from the installed fonts. This is one external-site test, not broad browser or TLS conformance.
