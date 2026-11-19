#include <exec/memory.h>
#include <exec/libraries.h>
#include <proto/exec.h>
#include <proto/dos.h>
#include <proto/debug.h>

/* Diagnostic cold-load ordering: no engine initialization or profile changes. */
int main(void)
{
    struct Library *v8, *cef;
    LONG error;
    KPrintF("[CEF-LOAD] before-v8 free=%p largest=%p\n",
        (APTR)AvailMem(MEMF_ANY), (APTR)AvailMem(MEMF_ANY | MEMF_LARGEST));
    v8 = OpenLibrary("v8.library", 1);
    error = v8 ? 0 : IoErr();
    KPrintF("[CEF-LOAD] v8=%p ioerr=%ld free=%p largest=%p\n", v8, error,
        (APTR)AvailMem(MEMF_ANY), (APTR)AvailMem(MEMF_ANY | MEMF_LARGEST));
    if (!v8) return 20;
    cef = OpenLibrary("cef.library", 3);
    error = cef ? 0 : IoErr();
    KPrintF("[CEF-LOAD] cef=%p ioerr=%ld free=%p largest=%p\n", cef, error,
        (APTR)AvailMem(MEMF_ANY), (APTR)AvailMem(MEMF_ANY | MEMF_LARGEST));
    if (cef) CloseLibrary(cef);
    CloseLibrary(v8);
    KPrintF("[CEF-LOAD] sequential-open %s\n", cef ? "PASS" : "FAIL");
    return cef ? 0 : 20;
}
