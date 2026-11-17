#include <algorithm>
#include <cstdint>
#include <array>
static_assert(__GNUC__ == 16);
static_assert(std::ranges::starts_with(std::array{1,2,3}, std::array{1,2}));
int main(){std::uint64_t v=42; return v==42 ? 0 : 1;}
