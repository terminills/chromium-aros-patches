#!/usr/bin/env bash
# Apply committed queues in a dedicated, prepared Chromium checkout.
set -euo pipefail
SRC=$(cd "${1:?usage: apply.sh <chromium-src>}" && pwd)
HERE=$(cd "$(dirname "$0")" && pwd)
# Complete preflight before creating any branch. Never reset an existing aros.
while IFS=$'\t' read -r path url base; do
  repo=$SRC; [ "$path" = src ] || repo=$SRC/$path
  [ -e "$repo/.git" ] || { echo "missing repository: $repo" >&2; exit 2; }
  git -C "$repo" diff --quiet --ignore-submodules=all &&
    git -C "$repo" diff --cached --quiet --ignore-submodules=all || {
      echo "$path: tracked edits; use a clean dedicated checkout" >&2; exit 2;
    }
  if git -C "$repo" show-ref --verify --quiet refs/heads/aros; then
    echo "$path: branch aros already exists; refusing to reset it" >&2; exit 2
  fi
  for state in rebase-apply rebase-merge MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD; do
    state_path=$(git -C "$repo" rev-parse --git-path "$state")
    [[ "$state_path" = /* ]] || state_path="$repo/$state_path"
    [ ! -e "$state_path" ] || { echo "$path: unfinished Git operation" >&2; exit 2; }
  done
  while IFS= read -r patch; do
    [ -f "$HERE/$path/$patch" ] || { echo "$path: missing $patch" >&2; exit 2; }
  done < "$HERE/$path/series"
done < "$HERE/PINS"
while IFS=$'\t' read -r path url base; do
  repo=$SRC; [ "$path" = src ] || repo=$SRC/$path
  git -C "$repo" cat-file -e "$base^{commit}" 2>/dev/null \
    || git -C "$repo" fetch -q "$url" "$base" \
    || { echo "$path: cannot fetch pinned base $base" >&2; exit 2; }
  git -C "$repo" checkout -q -b aros "$base"
  n=0
  while IFS= read -r patch; do
    git -C "$repo" am -q --keep-cr "$HERE/$path/$patch"
    n=$((n + 1))
  done < "$HERE/$path/series"
  echo "$path: $n patches on $base"
done < "$HERE/PINS"
