#include "tensorflow/lite/delegates/xnnpack/mmap_handle.h"
#include <cassert>
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>

static int mode;
static int calls;
extern "C" ssize_t __real_pread(int, void*, size_t, off_t);
extern "C" ssize_t __wrap_pread(int fd, void* data, size_t size, off_t offset) {
  ++calls;
  if (mode == 1 && calls == 1) { errno = EINTR; return -1; }
  if (mode == 2 && calls > 1) return 0;
  if (size > 3) size = 3;
  return __real_pread(fd, data, size, offset);
}
int main() {
  using namespace tflite::xnnpack;
  char path[] = "/tmp/aros-file-snapshot-XXXXXX";
  int fd = mkstemp(path);
  assert(fd >= 0);
  unlink(path);
  const char bytes[] = "0123456789abcdef";
  assert(write(fd, bytes, 16) == 16);
  assert(lseek(fd, 7, SEEK_SET) == 7);
  FileDescriptorView view(fd);
  MMapHandle map;
  mode = 1; calls = 0;
  assert(map.Map(view, 2));
  assert(map.size() == 14 && memcmp(map.data(), bytes + 2, 14) == 0);
  assert(lseek(fd, 0, SEEK_CUR) == 7);
  assert(!map.Resize(32));
  assert(!MarkMemoryNotNeeded(map.data(), map.size()));
  map.UnMap();
  mode = 2; calls = 0;
  assert(!map.Map(view));
  assert(!map.IsMapped() && map.size() == 0);
  assert(lseek(fd, 0, SEEK_CUR) == 7);
  assert(!map.Map(view, 17));
  assert(!map.Map(FileDescriptorView(-1)));
  mode = 0; calls = 0;
  assert(map.Map(view));
  assert(map.size() == 16 && memcmp(map.data(), bytes, 16) == 0);
  close(fd);
  puts("PASS: snapshot contents, short reads, EINTR, cursor, EOF, invalid offset/fd, retry, no discard/resize");
}
