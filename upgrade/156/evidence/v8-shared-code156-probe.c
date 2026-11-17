#include <proto/exec.h>
#include <proto/dos.h>
#include <proto/v8.h>
#include <exec/memory.h>
#include <clib/debug_protos.h>
#include <dos/dostags.h>
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

/* Controlled phases measure guest-wide free RAM, including app overhead.
 * They are not per-allocation attribution or a claim about full CEF. */
static int marker(const char *app, const char *phase, int write_marker) {
    char path[100];
    snprintf(path, sizeof path, "T:V8Memory-%s.%s", app, phase);
    if (write_marker) {
        FILE *f = fopen(path, "w");
        if (!f) return 0;
        fprintf(f, "%p\n", (void *)V8Base);
        return fclose(f) == 0;
    }
    BPTR lock = Lock((CONST_STRPTR)path, ACCESS_READ);
    if (!lock) return 0;
    UnLock(lock);
    return 1;
}
static int await_marker(const char *app, const char *phase) {
    for (int i = 0; i < 1200; ++i) {
        if (marker(app, phase, 0)) return 1;
        Delay(5);
    }
    printf("FAIL: timeout %s %s\n", app, phase);
    fflush(stdout);
    return 0;
}
static unsigned long long sample(const char *phase) {
    unsigned long long n = (unsigned long long)AvailMem(MEMF_ANY);
    char line[160];
    snprintf(line, sizeof line, "RAM phase=%s free_bytes=%llu\n", phase, n);
    fputs(line, stdout); KPutStr((CONST_STRPTR)line);
    fflush(stdout);
    return n;
}
static int controller(void) {
    const char *phases[] = {"ready", "release", "done"};
    char path[100];
    for (int a = 0; a < 2; ++a)
        for (int p = 0; p < 3; ++p) {
            snprintf(path, sizeof path, "T:V8Memory-%c.%s", 'A'+a, phases[p]);
            DeleteFile((CONST_STRPTR)path);
        }
    puts("V8 shared resident engine: two apps, four isolates, two CPUs");
    unsigned long long before = sample("baseline");
    if (SystemTags((CONST_STRPTR)"Run >NIL: C:V8Memory156Probe A memory >T:V8Memory-A.log",
                   SYS_Asynch, FALSE, TAG_DONE) == -1 || !await_marker("A", "ready")) return 20;
    unsigned long long first = sample("A-ready");
    if (SystemTags((CONST_STRPTR)"Run >NIL: C:V8Memory156Probe B memory >T:V8Memory-B.log",
                   SYS_Asynch, FALSE, TAG_DONE) == -1 || !await_marker("B", "ready")) {
        marker("A", "release", 1); return 21;
    }
    unsigned long long both = sample("A-and-B-ready");
    void *bases[2] = {0};
    for (int a = 0; a < 2; ++a) {
        snprintf(path, sizeof path, "T:V8Memory-%c.ready", 'A'+a);
        FILE *f = fopen(path, "r");
        if (f) { if (fscanf(f, "%p", &bases[a]) != 1) bases[a] = 0; fclose(f); }
    }
    int same = bases[0] && bases[0] == bases[1];
    printf("Resident bases A=%p B=%p same=%d\n", bases[0], bases[1], same);
    printf("Increment first_app=%lld second_app=%lld bytes\n",
           (long long)before-(long long)first, (long long)first-(long long)both);
    fflush(stdout);
    marker("A", "release", 1);
    int a_done = await_marker("A", "done");
    Delay(25); sample("A-closed-B-live");
    marker("B", "release", 1);
    int b_done = await_marker("B", "done");
    Delay(25); sample("both-closed");
    puts(same && a_done && b_done ? "PASS: same resident library, A closes before B evaluates" : "FAIL: sharing/lifecycle");
    return same && a_done && b_done ? 0 : 22;
}

int main(int argc, char **argv) {
    if (argc > 1 && strcmp(argv[1], "controller") == 0) return controller();
    puts("JOB-0254 native V8 156 engine/isolation probe"); fflush(stdout);
    printf("Application: %s\n", argc > 1 ? argv[1] : "single"); fflush(stdout);
    V8Base = OpenLibrary((CONST_STRPTR)"v8.library", 1);
    if (!V8Base) { puts("FAIL: OpenLibrary"); return 10; }
    puts("Library opened"); fflush(stdout);
    if (!V8Initialize()) { puts("FAIL: initialize"); return 11; }
    puts("Engine initialized"); fflush(stdout);
    APTR a = V8CreateIsolate(), b = V8CreateIsolate();
    if (!a || !b) { puts("FAIL: isolates"); return 12; }
    APTR ca = V8CreateContext(a), cb = V8CreateContext(b);
    if (!ca || !cb) { puts("FAIL: contexts"); return 13; }
    // Allocate and warm up independent JavaScript code before either app exits.
    if (!eval(a, ca,
        "globalThis.hot = function(x) { return x * 2 + 1; }; "
        "(() => { let n=0; for(let i=0;i<20000;++i) n+=hot(i); return n; })()",
        "400000000")) return 16;
    // Deliberately overlap separate processes in the shared-library test.
    if (argc > 2 && strcmp(argv[2], "memory") == 0) {
        if (!marker(argv[1], "ready", 1) || !await_marker(argv[1], "release")) return 15;
    } else if (argc > 1) Delay(argv[1][0] == 'B' ? 150 : 50);
    V8Cleanup();
    puts("Cleanup requested with live isolates; evaluation must remain valid");
    int ok = eval(a, ca, "hot(21)", "43");
    ok &= eval(a, ca, "globalThis.privateValue = 42; privateValue", "42");
    ok &= eval(b, cb, "typeof privateValue", "undefined");
    ok &= eval(b, cb, "globalThis.privateValue = 7; privateValue", "7");
    ok &= eval(a, ca, "privateValue", "42");
    ok &= eval(a, ca, "[1,2,3,4].map(x => x*x).join(',')", "1,4,9,16");
    V8DestroyContext(b, cb); V8DestroyIsolate(b);
    ok &= eval(a, ca, "privateValue + 1", "43");
    V8DestroyContext(a, ca); V8DestroyIsolate(a);
    V8Cleanup(); CloseLibrary(V8Base);
    puts(ok ? "PASS: JavaScript, isolated globals, independent teardown" : "FAIL: evaluation");
    if (ok && argc > 2) marker(argv[1], "done", 1);
    return ok ? 0 : 14;
}
