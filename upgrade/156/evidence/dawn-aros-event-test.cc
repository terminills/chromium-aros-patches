#include "src/dawn/native/ArosSystemEvent.h"
#include <cassert>
#include <atomic>
#include <thread>
#include <vector>
#include <cstdio>
using namespace dawn::native;
int main() {
  auto& wait = GetArosSystemEventWaitSet();
  ArosSystemEventState a, b;
  assert(!wait.Wait(0, [&] { return a.signaled; }));
  assert(!wait.Wait(1000000, [&] { return a.signaled; }));
  wait.Signal(a);
  assert(wait.Wait(0, [&] { return a.signaled; }));
  std::atomic<int> finished{0};
  std::vector<std::thread> threads;
  for (int i=0;i<8;++i) threads.emplace_back([&] {
    assert(wait.Wait(UINT64_MAX, [&] { return b.signaled; }));
    ++finished;
  });
  wait.Signal(b);
  for (auto& t:threads) t.join();
  assert(finished==8);
  for (int i=0;i<1000;++i) {
    ArosSystemEventState c;
    std::thread t([&] { wait.Signal(c); });
    assert(wait.Wait(UINT64_MAX, [&] { return c.signaled; }));
    t.join();
  }
  std::puts("PASS: pre-signal, zero/finite timeout, 8 waiters, 1000 signal/wait races");
}
