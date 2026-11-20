# Native task lifetime diagnosis and ARM link

Source287 / engine288 ten-cycle diagnostic318 identifies two additional native PerfettoTrace tasks per later cycle, each retaining a 2 MiB stack. Task-resource unique IDs and retained guest memory match base::Thread objects to the exact native Task address. Stack scanning supplies candidate addresses, not a validated backtrace. The full private memory dump is retained locally and is not published.

After host exit, 26 PerfettoTrace threads and one CacheThread_BlockFile remain. This attributes 4 MiB per-cycle stack growth; it does not explain all whole-guest growth or establish a memory plateau. Candidate319 joins auxiliary owner trace threads while retaining the engine-global tracing runner and backend/TLS objects. Both320 cross archives pass; native link and regression acceptance are pending. This candidate is not the release source snapshot.

ARM314 engine native link and all289 native clients pass. Fresh294 current-master desktop and native icon checks pass, but facade opening fails before browser initialization. Its image omitted gl.library and vulkan.library. Both current-master dependencies now build successfully in321; fresh322 retest is pending. The screenshot shows the desktop and About, not a working browser.

No RC binaries are published. Existing native x64 UI, isolation and cold-profile results remain available in native316-x64 and cold317-profile.
