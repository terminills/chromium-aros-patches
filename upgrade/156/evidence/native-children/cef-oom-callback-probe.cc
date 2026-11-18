// Links the actual candidate's PartitionAlloc OOM-callback object.
// Does not induce OOM or qualify renderer ownership/SMP races.
#include "partition_alloc/oom_callback.h"
extern "C" {
#include <clib/debug_protos.h>
}
static unsigned calls;
static void Callback() { ++calls; }
int main() {
  partition_alloc::internal::RunPartitionAllocOomCallback();
  if (calls != 0) return 1;
  partition_alloc::SetPartitionAllocOomCallback(Callback);
  for (unsigned i = 0; i < 1000; ++i)
    partition_alloc::internal::RunPartitionAllocOomCallback();
  KPrintF("[CEF-OOM-CALLBACK] calls=%lu %s\n", (unsigned long)calls,
          calls == 1000 ? "PASS" : "FAIL");
  return calls != 1000;
}
