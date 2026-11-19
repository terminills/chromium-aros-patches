#include <exec/memory.h>
#include <proto/exec.h>
#include <proto/debug.h>
int main(int argc,char** argv) {
 IPTR total=AvailMem(MEMF_ANY|MEMF_TOTAL),free=AvailMem(MEMF_ANY),largest=AvailMem(MEMF_ANY|MEMF_LARGEST);
 KPrintF("[CEF-CYCLE-MEM] phase=%s total=%p free=%p used=%p largest=%p\n",argc>1?argv[1]:"sample",(APTR)total,(APTR)free,(APTR)(total-free),(APTR)largest);
 return 0;
}
