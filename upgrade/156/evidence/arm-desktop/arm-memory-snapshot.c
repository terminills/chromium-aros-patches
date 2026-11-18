#include <exec/memory.h>
#include <proto/exec.h>
#include <proto/debug.h>
int main(int argc, char **argv)
{
    IPTR free_bytes = AvailMem(MEMF_ANY);
    IPTR total_bytes = AvailMem(MEMF_ANY | MEMF_TOTAL);
    IPTR largest = AvailMem(MEMF_ANY | MEMF_LARGEST);
    KPrintF("[ARM-MEM] label=%s total=%p free=%p used=%p largest=%p\n",
        argc > 1 ? argv[1] : "sample", (APTR)total_bytes, (APTR)free_bytes,
        (APTR)(total_bytes - free_bytes), (APTR)largest);
    return 0;
}
