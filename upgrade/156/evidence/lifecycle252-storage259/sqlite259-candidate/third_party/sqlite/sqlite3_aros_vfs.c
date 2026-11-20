// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#if defined(__AROS__)
#include <proto/dos.h>
#include <string.h>
#include <unistd.h>

// AROS FAT can leave the native handle cursor beyond EOF after shrinking.
// posixc then cannot query that cursor, even to perform an absolute seek.
// Keep SQLite's cursor inside the new extent before truncating. This is a
// private VFS operation, not a replacement for POSIX ftruncate semantics.
int chromiumArosSqliteTruncate(int fd, off_t length) {
  if (length >= 0) {
    off_t current = lseek(fd, 0, SEEK_CUR);
    if (current < 0) return -1;
    if (current > length && lseek(fd, length, SEEK_SET) < 0) return -1;
  }
  return ftruncate(fd, length);
}

// SQLite's Unix walker prefixes getcwd() to native assigns and inserts '/'
// before volume names. Resolve through DOS locks instead, including the parent
// of a database which has not been created yet. This belongs to Chromium's
// SQLite VFS, not to the SDK's global path policy.
int chromiumArosFullPathname(const char* input, int capacity, char* out) {
  char path[4096];
  size_t length = strlen(input);
  if (!length || length >= sizeof(path) || capacity <= 0) return 14;
  if (input[0] == '/') {
    const char* start = input + 1;
    const char* slash = strchr(start, '/');
    size_t volume = slash ? (size_t)(slash - start) : strlen(start);
    if (!volume) return 14;
    // Accept both /T/foo and /T:/foo at the local boundary.
    if (start[volume - 1] == ':') --volume;
    if (!volume || volume + 2 + (slash ? strlen(slash + 1) : 0) > sizeof(path))
      return 14;
    memcpy(path, start, volume);
    path[volume] = ':';
    strcpy(path + volume + 1, slash ? slash + 1 : "");
  } else {
    memcpy(path, input, length + 1);
  }
  BPTR lock = Lock(path, SHARED_LOCK);
  if (lock) {
    int ok = NameFromLock(lock, out, capacity);
    UnLock(lock);
    return ok ? 0 : 14;
  }
  char* leaf = FilePart(path);
  char filename[4096];
  if (!*leaf) return 14;
  strcpy(filename, leaf);
  *leaf = 0;
  lock = Lock(path, SHARED_LOCK);
  if (!lock) return 14;
  int ok = NameFromLock(lock, out, capacity);
  UnLock(lock);
  if (!ok || !AddPart(out, filename, capacity)) return 14;
  return 0;
}

#endif  // defined(__AROS__)
