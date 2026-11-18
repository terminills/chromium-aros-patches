#include "partition_alloc/internal/reservation_offset_table_internal.h"
#include <cassert>
#include <cstdio>
using namespace partition_alloc::internal;
int main(int argc, char**) {
  auto table = ReservationOffsetTable::Get(kRegularPoolHandle);
  if (argc > 1) {
    table.SetNormalBucketsTag(256ull << 30);
    return 99;
  }
  const uintptr_t probes[] = {0, 0x100000000ull, 0x13e400000ull,
                             (256ull << 30) - kSuperPageSize};
  for (auto address : probes) {
    table.SetNormalBucketsTag(address);
    assert(table.IsManagedByNormalBuckets(address));
    table.SetNotAllocatedTag(address, kSuperPageSize);
    assert(!table.IsManagedByNormalBucketsOrDirectMap(address));
  }
  const uintptr_t start = 0x140000000ull;
  table.SetDirectMapReservationStart(start, 3 * kSuperPageSize);
  for (unsigned i = 0; i < 3; ++i)
    assert(table.GetDirectMapReservationStart(start + i * kSuperPageSize) == start);
  table.SetNotAllocatedTag(start, 3 * kSuperPageSize);
  puts("PASS: high-address normal buckets, direct maps, and release tags");
}
