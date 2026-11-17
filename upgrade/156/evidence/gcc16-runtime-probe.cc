#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>
#include <string>
int main() {
  std::vector<std::uint64_t> values{9, 2, 7, 1};
  std::ranges::sort(values);
  const std::vector<std::uint64_t> prefix{1, 2};
  const bool ok = std::ranges::starts_with(values, prefix) && std::to_string(values.back()) == "9";
  std::printf("GCC %s native C++23 vector/sort/starts_with/string: %s\n", __VERSION__, ok ? "PASS" : "FAIL");
  return ok ? 0 : 20;
}
