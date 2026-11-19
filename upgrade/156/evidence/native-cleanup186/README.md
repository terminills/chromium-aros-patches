# Native cleanup and remaining RC failures

The x64 186 TLS cleanup candidate completes ten browser cycles, twenty renderer heap retirements and all twenty-two child exits. Independent native child files agree with serial. Whole-guest memory still grows by 130.27 MiB between cycles 1 and 10; this is not memory plateau acceptance.

ARM70 renders the local JavaScript/WebAssembly/worker fixture but fails bounded host exit. Offline child files confirm utility task67 never recorded exit. Three renderer heaps retired, one deferred. Screenshots prove paint, not complete lifecycle.

Installed-layout tests189 and190 both fault in V8 Object::CallAsConstructor while invoking custom-element reactions. Test190 omits preceding invalid-argument tests and still fails. This does not establish resource relocation as the cause. Captured189 stack and source review identified process-global CEReactionsScope state. The retained candidate changes only AROS to per-task TLS. A controlled host test using actual sources and mocked V8/DOM dependencies fails before and passes after, including nested scope restoration. Native qualification is pending. Test190 detailed alert registers were not captured before the scheduled186 run replaced that VM; its screenshot and raw serial remain retained privately.

The complete replay-checked186v2 source snapshot is in ../native-worker-tls186-v2/source. Apply custom-element191.patch on top for this unqualified candidate. No RC or complete feature claim is made.
