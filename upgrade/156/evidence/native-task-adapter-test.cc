#include "src/base/platform/aros-native-task.h"
#include <proto/exec.h>
#include <proto/kernel.h>
#include <cstdlib>
#include <cstdio>
#include <string>
struct Result { unsigned cpu, errors; } results[8];
ArosNativeTask* tasks[8];
static thread_local unsigned tls_value;
static void work(void* arg) {
  auto* r = static_cast<Result*>(arg);
  APTR KernelBase = OpenResource((CONST_STRPTR)"kernel.resource");
  r->cpu = KrnGetCPUNumber();
  if (tls_value != 0) ++r->errors;
  tls_value = 0x100 + (r - results);
  std::string text(1024, 'a');
  auto* allocation = static_cast<unsigned*>(std::malloc(4096));
  if (!allocation) { ++r->errors; return; }
  for (unsigned i = 0; i < 1024; ++i) allocation[i] = i;
  for (unsigned i = 0; i < 1024; ++i) if (allocation[i] != i) ++r->errors;
  if (text.size() != 1024 || tls_value != 0x100 + (r - results)) ++r->errors;
  std::free(allocation);
}
static void join_other_creator(void*) {
  for (auto* task : tasks) ArosNativeTaskJoin(task);
}
int run_cycle() {
  unsigned errors = 0;
  for (unsigned i = 0; i < 8; ++i) {
    tasks[i] = ArosNativeTaskStart(work, &results[i], 262144, "Native CEF worker", 0);
    if (!tasks[i]) ++errors;
  }
  auto* joiner = ArosNativeTaskStart(join_other_creator, nullptr, 262144,
                                   "Native cross-task join", 0);
  if (joiner) ArosNativeTaskJoin(joiner);
  else { ++errors; join_other_creator(nullptr); }
  for (unsigned i = 0; i < 8; ++i) {
    printf("Native worker %u CPU %u CRT/TLS errors %u\n", i, results[i].cpu, results[i].errors);
    errors += results[i].errors;
  }
  puts(errors ? "Native task adapter FAIL" : "Native task adapter PASS: cross-task joins complete");
  return errors ? 20 : 0;
}

int main() {
  for (unsigned cycle = 0; cycle < 10; ++cycle) {
    printf("Native lifecycle cycle %u\n", cycle);
    for (auto& result : results) result = {};
    if (run_cycle()) return 20;
  }
  puts("PASS: 10 native lifecycle cycles, 80 workers, 10 cross-task joiners");
  return 0;
}
