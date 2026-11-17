/* JOB-0254: direct AROS task placement and synchronization, no pthreads. */
#include <exec/types.h>
#include <exec/tasks.h>
#include <exec/semaphores.h>
#include <dos/dostags.h>
#include <proto/exec.h>
#include <proto/dos.h>
#include <proto/kernel.h>
#include <proto/task.h>
#include <stdio.h>

APTR KernelBase;
APTR TaskResBase;
struct Worker {
  unsigned expected, observed, errors;
  unsigned long checksum;
};
static struct Worker workers[8];
static struct SignalSemaphore lock;
static unsigned ready, done;
static LONG slot;
static void worker(void) {
  struct Worker *w = FindTask(NULL)->tc_UserData;
  w->observed = KrnGetCPUNumber();
  if (!SetTaskStorageSlot(slot, (IPTR)w)) ++w->errors;
  ObtainSemaphore(&lock);
  ++ready;
  ReleaseSemaphore(&lock);
  for (unsigned i = 0; i < 1000000; ++i) {
    w->checksum += i ^ w->expected;
    if ((i & 65535) == 0 && (GetTaskStorageSlot(slot) != (IPTR)w ||
        KrnGetCPUNumber() != w->expected)) ++w->errors;
  }
  ObtainSemaphore(&lock);
  ++done;
  ReleaseSemaphore(&lock);
}
int main(void) {
  KernelBase = OpenResource((CONST_STRPTR)"kernel.resource");
  TaskResBase = OpenResource((CONST_STRPTR)"task.resource");
  if (!KernelBase || !TaskResBase) return 20;
  unsigned count = KrnGetCPUCount();
  if (count > 8) count = 8;
  if (count < 2) { puts("FAIL: need multiple AROS CPUs"); return 20; }
  slot = AllocTaskStorageSlot();
  if (slot < 0) return 20;
  InitSemaphore(&lock);
  unsigned launched = 0;
  for (unsigned i = 0; i < count; ++i) {
    APTR mask = KrnAllocCPUMask();
    if (!mask) break;
    KrnGetCPUMask(i, mask);
    workers[i].expected = i;
    if (!CreateNewProcTags(NP_Entry, (IPTR)worker,
        NP_Name, (IPTR)"CEF native multicore probe", NP_UserData,
        (IPTR)&workers[i], NP_StackSize, 65536, NP_Affinity, (IPTR)mask,
        NP_NotifyOnDeath, TRUE, TAG_DONE)) {
      KrnFreeCPUMask(mask); break;
    }
    ++launched;
  }
  for (unsigned i = 0; i < launched; ++i) {
    struct ETask *child = (struct ETask *)ChildWait(0);
    ChildFree(child->et_UniqueID);
  }
  unsigned errors = launched != count || ready != count || done != count;
  for (unsigned i = 0; i < launched; ++i) {
    printf("Native worker %u: CPU %u errors %u checksum %lu\n", i,
           workers[i].observed, workers[i].errors, workers[i].checksum);
    errors += workers[i].errors + (workers[i].observed != i);
  }
  FreeTaskStorageSlot(slot);
  puts(errors ? "Native AROS multicore FAIL" : "Native AROS multicore PASS");
  return errors ? 20 : 0;
}
