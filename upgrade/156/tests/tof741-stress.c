#include <exec/types.h>
#include <exec/tasks.h>
#include <graphics/gfxbase.h>
#include <utility/tagitem.h>
#include <dos/dos.h>
#include <proto/exec.h>
#include <proto/dos.h>
#include <proto/graphics.h>
#include <proto/kernel.h>
#include <stdio.h>
#include <stdint.h>
struct GfxBase *GfxBase;
APTR KernelBase;
#define WORKERS 16
#define FRAMES 3000
struct Worker { ULONG count; ULONG done; ULONG cpu_mask; };
static struct Worker workers[WORKERS];
static struct Task *tasks[WORKERS];
static __attribute__((noinline)) void reuse_stack(ULONG seed) {
 volatile uintptr_t scratch[128];
 for(unsigned i=0;i<128;i++)scratch[i]=(uintptr_t)seed+i+0xa5a50000;
 (void)scratch[0];
}
static void worker(void) {
 struct Worker *w=FindTask(NULL)->tc_UserData;
 for(ULONG i=0;i<FRAMES;i++) {
  WaitTOF();
  reuse_stack(i);
  __atomic_fetch_or(&w->cpu_mask,1UL<<KrnGetCPUNumber(),__ATOMIC_RELAXED);
  __atomic_store_n(&w->count,i+1,__ATOMIC_RELAXED);
 }
 __atomic_store_n(&w->done,1,__ATOMIC_RELEASE);
 Wait(0);
}
int main(void) {
 KernelBase=OpenResource((CONST_STRPTR)"kernel.resource");
 GfxBase=(struct GfxBase *)OpenLibrary((CONST_STRPTR)"graphics.library",0);
 if(!KernelBase||!GfxBase){printf("TOF741 setup failed\n");return 20;}
 ULONG cpus=KrnGetCPUCount();if(cpus<2){printf("TOF741 requires two CPUs\n");return 20;}
 unsigned spawned=0;
 for(unsigned i=0;i<WORKERS;i++) {
  cpumask_t *m=KrnAllocCPUMask();if(!m)break;
  KrnClearCPUMask(m);KrnGetCPUMask(i%2,m);
  tasks[i]=NewCreateTask(TASKTAG_NAME,(IPTR)"TOF741 worker",TASKTAG_PRI,5,TASKTAG_PC,(IPTR)worker,TASKTAG_STACKSIZE,32768,TASKTAG_USERDATA,(IPTR)&workers[i],TASKTAG_AFFINITY,(IPTR)m,TAG_DONE);
  if(!tasks[i]){KrnFreeCPUMask(m);break;}spawned++;
 }
 printf("TOF741 start workers=%u cpus=%lu frames=%u\n",spawned,(unsigned long)cpus,FRAMES);fflush(stdout);
 unsigned done=0;
 for(unsigned ticks=0;ticks<6000;ticks++) {
  done=0;ULONG total=0,mask=0;
  for(unsigned i=0;i<spawned;i++){done+=__atomic_load_n(&workers[i].done,__ATOMIC_ACQUIRE)!=0;total+=__atomic_load_n(&workers[i].count,__ATOMIC_RELAXED);mask|=__atomic_load_n(&workers[i].cpu_mask,__ATOMIC_RELAXED);}
  if(ticks%250==0||done==spawned){printf("TOF741 progress ticks=%u done=%u count=%lu cpu_mask=%lu\n",ticks,done,(unsigned long)total,(unsigned long)mask);fflush(stdout);}
  if(done==spawned)break;
  Delay(1);
 }
 if(done!=spawned){printf("TOF741 FAIL timeout; retaining waiting tasks\n");fflush(stdout);Wait(0);}
 Delay(2);for(unsigned i=0;i<spawned;i++)RemTask(tasks[i]);
 int pass=spawned==WORKERS&&done==WORKERS;
 printf("TOF741 %s\n",pass?"PASS":"FAIL");fflush(stdout);CloseLibrary((struct Library *)GfxBase);return pass?0:20;
}
