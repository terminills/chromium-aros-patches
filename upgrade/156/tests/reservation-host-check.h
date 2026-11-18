// Host-only adapter: preserve fatal checks without linking native AROS logging.
#include "partition_alloc/partition_alloc_check.h"
#include <cstdlib>
#undef PA_CHECK
#define PA_CHECK(condition) do { if (!(condition)) std::abort(); } while (0)
