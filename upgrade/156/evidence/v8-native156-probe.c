#include <proto/exec.h>
#include <proto/dos.h>
#include <proto/v8.h>
#include <stdio.h>
#include <string.h>

struct Library *V8Base;
static int eval(APTR isolate, APTR context, const char *script, const char *want) {
    char result[256] = {0};
    LONG rc = V8Eval(isolate, context, (CONST_STRPTR)script,
                     (STRPTR)result, sizeof result);
    printf("Eval: rc=%ld result=%s expected=%s\n", (long)rc, result, want);
    fflush(stdout);
    return rc == 0 && strcmp(result, want) == 0;
}
int main(int argc, char **argv) {
    puts("JOB-0254 native V8 156 engine/isolation probe"); fflush(stdout);
    printf("Application: %s\n", argc > 1 ? argv[1] : "single"); fflush(stdout);
    V8Base = OpenLibrary("v8.library", 1);
    if (!V8Base) { puts("FAIL: OpenLibrary"); return 10; }
    puts("Library opened"); fflush(stdout);
    if (!V8Initialize()) { puts("FAIL: initialize"); return 11; }
    puts("Engine initialized"); fflush(stdout);
    APTR a = V8CreateIsolate(), b = V8CreateIsolate();
    if (!a || !b) { puts("FAIL: isolates"); return 12; }
    APTR ca = V8CreateContext(a), cb = V8CreateContext(b);
    if (!ca || !cb) { puts("FAIL: contexts"); return 13; }
    // Deliberately overlap separate processes in the shared-library test.
    if (argc > 1) Delay(argv[1][0] == 'B' ? 150 : 50);
    V8Cleanup();
    puts("Cleanup requested with live isolates; evaluation must remain valid");
    int ok = eval(a, ca, "globalThis.privateValue = 42; privateValue", "42");
    ok &= eval(b, cb, "typeof privateValue", "undefined");
    ok &= eval(b, cb, "globalThis.privateValue = 7; privateValue", "7");
    ok &= eval(a, ca, "privateValue", "42");
    ok &= eval(a, ca, "[1,2,3,4].map(x => x*x).join(',')", "1,4,9,16");
    V8DestroyContext(b, cb); V8DestroyIsolate(b);
    ok &= eval(a, ca, "privateValue + 1", "43");
    V8DestroyContext(a, ca); V8DestroyIsolate(a);
    V8Cleanup(); CloseLibrary(V8Base);
    puts(ok ? "PASS: JavaScript, isolated globals, independent teardown" : "FAIL: evaluation");
    return ok ? 0 : 14;
}
