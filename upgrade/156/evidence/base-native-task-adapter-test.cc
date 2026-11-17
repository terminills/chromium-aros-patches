#include "base/threading/aros_native_task.h"
#include <proto/exec.h>
#include <proto/kernel.h>
#include <proto/dos.h>
#include <proto/task.h>
#include <resources/task.h>
#include <cstdlib>
#include <cstdio>
#include <string>
struct Result { unsigned cpu, errors; Task* task; ULONG id; } results[8];
ArosPlatformTask* tasks[8];
static thread_local unsigned tls_value;
static unsigned completed;
static void work(void* arg) {
  auto* r = static_cast<Result*>(arg);
  APTR KernelBase = OpenResource((CONST_STRPTR)"kernel.resource");
  r->cpu = KrnGetCPUNumber();
  r->task = FindTask(nullptr);
  r->id = r->task->tc_UnionETask.tc_ETask->et_UniqueID;
  if (!ArosPlatformTaskCurrentHandle()) ++r->errors;
  if (tls_value != 0) ++r->errors;
  tls_value = 0x100 + (r - results);
  std::string text(1024, 'a');
  auto* allocation = static_cast<unsigned*>(std::malloc(4096));
  if (!allocation) { ++r->errors; return; }
  for (unsigned i = 0; i < 1024; ++i) allocation[i] = i;
  for (unsigned i = 0; i < 1024; ++i) if (allocation[i] != i) ++r->errors;
  if (text.size() != 1024 || tls_value != 0x100 + (r - results)) ++r->errors;
  std::free(allocation);
  __atomic_fetch_add(&completed, 1u, __ATOMIC_RELEASE);
}
static void join_other_creator(void*) {
  for (auto* task : tasks) ArosPlatformTaskJoin(task);
}
int run_cycle() {
  unsigned errors = 0;
  for (unsigned i = 0; i < 8; ++i) {
    tasks[i] = ArosPlatformTaskStart(work, &results[i], 262144, "Native CEF worker", 0);
    if (!tasks[i]) ++errors;
  }
  auto* joiner = ArosPlatformTaskStart(join_other_creator, nullptr, 262144,
                                   "Native cross-task join", 0);
  if (joiner) ArosPlatformTaskJoin(joiner);
  else { ++errors; join_other_creator(nullptr); }
  for (unsigned i = 0; i < 8; ++i) {
    printf("Native worker %u CPU %u CRT/TLS errors %u\n", i, results[i].cpu, results[i].errors);
    errors += results[i].errors;
  }
  puts(errors ? "Native task adapter FAIL" : "Native task adapter PASS: cross-task joins complete");
  return errors ? 20 : 0;
}

int detached_cycle() {
  APTR TaskResBase = OpenResource((CONST_STRPTR)"task.resource");
  __atomic_store_n(&completed, 0u, __ATOMIC_RELAXED);
  for (auto& result : results) result = {};
  for (unsigned i = 0; i < 8; ++i) {
    auto* task = ArosPlatformTaskStart(work, &results[i], 262144,
                                     "Native detached worker", 0);
    if (!task) return 20;
    ArosPlatformTaskDetach(task);
  }
  for (unsigned tick = 0; tick < 1000; ++tick) {
    if (__atomic_load_n(&completed, __ATOMIC_ACQUIRE) == 8) {
      bool alive = false;
      TaskList* list = LockTaskList(LTF_ALL);
      if (list) {
        while (Task* task = NextTaskEntry(list, LTF_ALL)) {
          for (const auto& r : results)
            if (task == r.task && task->tc_UnionETask.tc_ETask->et_UniqueID == r.id)
              alive = true;
        }
        UnLockTaskList(list, LTF_ALL);
        if (!alive) {
          for (const auto& r : results) if (r.errors) return 20;
          return 0;
        }
      }
    }
    Delay(1);
  }
  puts("FAIL: detached native tasks did not exit");
  return 20;
}

int main() {
  for (unsigned cycle = 0; cycle < 10; ++cycle) {
    printf("Native lifecycle cycle %u\n", cycle);
    for (auto& result : results) result = {};
    if (run_cycle()) return 20;
  }
  puts("PASS: 10 native lifecycle cycles, 80 workers, 10 cross-task joiners");
  for (unsigned cycle = 0; cycle < 10; ++cycle) {
    printf("Native detached lifecycle cycle %u\n", cycle);
    if (detached_cycle()) return 20;
  }
  puts("PASS: 80 detached workers removed by native AROS");
  return 0;
}
