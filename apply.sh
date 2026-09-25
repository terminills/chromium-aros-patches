#!/usr/bin/env bash
# apply.sh <chromium-src>
#
# Apply the AROS patch queue to a Chromium checkout. Each directory here is a
# repository inside <chromium-src> ("src" is the checkout itself); PINS gives
# the upstream commit each queue applies to. For every repository this checks
# out that commit on a branch named aros, then applies the queue in `series`
# order with `git am`, so the result carries the original authorship and
# messages. Stops at the first patch that does not apply.
set -euo pipefail
SRC=$(cd "${1:?usage: apply.sh <chromium-src>}" && pwd)
HERE=$(cd "$(dirname "$0")" && pwd)
while IFS=$'\t' read -r path url base; do
  repo=$SRC; [ "$path" = src ] || repo=$SRC/$path
  [ -d "$repo/.git" ] || [ -f "$repo/.git" ] || { echo "missing repository: $repo" >&2; exit 2; }
  git -C "$repo" cat-file -e "$base^{commit}" 2>/dev/null \
    || git -C "$repo" fetch -q "$url" "$base" \
    || { echo "$path: cannot fetch pinned base $base" >&2; exit 2; }
  git -C "$repo" checkout -q -B aros "$base"
  n=0
  while read -r p; do
    git -C "$repo" am -q --keep-cr "$HERE/$path/$p"; n=$((n + 1))
  done < "$HERE/$path/series"
  echo "$path: $n patches on $base"
done < "$HERE/PINS"
