#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

BINARY="$ROOT_DIR/target/release/arclight"
SNAPSHOT_DIR="$ROOT_DIR/snapshots"
TEXT_DIR="$SNAPSHOT_DIR/text"
JSON_DIR="$SNAPSHOT_DIR/json"
TMP_DIR="$ROOT_DIR/target/arclight-pilot"

CASES=(
  collatz-1000
  control-system
  deep-taxonomy-100000
  delfour
  euler-identity
  fibonacci
  goldbach-1000
  gps
  kaprekar-6174
  path-discovery
  polynomial
)

usage() {
  cat <<'EOF'
Usage: ./pilot.sh [check|refresh|show CASE [text|json]]

Commands:
  check          Build Arclight, regenerate fresh output into a temp folder,
                 and diff it against checked-in snapshots.
  refresh        Build Arclight and overwrite the checked-in snapshots.
  show CASE      Print one case directly using the built release binary.
                 Add a third argument of 'json' to see structured output.

Snapshot layout:
  snapshots/text/<case>.txt
  snapshots/json/<case>.json
  snapshots/text/all.txt
  snapshots/json/all.json
  snapshots/text/list.txt
EOF
}

build_release() {
  cargo build --release
}

write_snapshots() {
  local out_root="$1"
  mkdir -p "$out_root/text" "$out_root/json"

  "$BINARY" --list > "$out_root/text/list.txt"
  "$BINARY" --all > "$out_root/text/all.txt"
  "$BINARY" --all --format json > "$out_root/json/all.json"

  local case
  for case in "${CASES[@]}"; do
    "$BINARY" "$case" > "$out_root/text/$case.txt"
    "$BINARY" "$case" --format json > "$out_root/json/$case.json"
  done
}

require_snapshots() {
  local missing=0
  local case

  for case in "${CASES[@]}"; do
    [[ -f "$TEXT_DIR/$case.txt" ]] || { echo "missing snapshot: $TEXT_DIR/$case.txt" >&2; missing=1; }
    [[ -f "$JSON_DIR/$case.json" ]] || { echo "missing snapshot: $JSON_DIR/$case.json" >&2; missing=1; }
  done

  [[ -f "$TEXT_DIR/all.txt" ]] || { echo "missing snapshot: $TEXT_DIR/all.txt" >&2; missing=1; }
  [[ -f "$JSON_DIR/all.json" ]] || { echo "missing snapshot: $JSON_DIR/all.json" >&2; missing=1; }
  [[ -f "$TEXT_DIR/list.txt" ]] || { echo "missing snapshot: $TEXT_DIR/list.txt" >&2; missing=1; }

  if [[ "$missing" -ne 0 ]]; then
    echo >&2
    echo "Run './pilot.sh refresh' to generate the initial snapshots." >&2
    exit 1
  fi
}

check_snapshots() {
  rm -rf "$TMP_DIR"
  mkdir -p "$TMP_DIR"
  write_snapshots "$TMP_DIR"

  local failed=0
  local expected actual

  while IFS= read -r -d '' expected; do
    actual="$TMP_DIR/${expected#"$SNAPSHOT_DIR"/}"
    if [[ ! -f "$actual" ]]; then
      echo "missing generated snapshot: $actual" >&2
      failed=1
      continue
    fi
    if ! diff -u "$expected" "$actual"; then
      failed=1
    fi
  done < <(find "$TEXT_DIR" "$JSON_DIR" -type f ! -name '.gitkeep' -print0 | sort -z)

  if [[ "$failed" -ne 0 ]]; then
    echo >&2
    echo "Snapshot drift detected. Review the diff, then run './pilot.sh refresh' if the change is intentional." >&2
    exit 1
  fi

  echo "All snapshots match."
}

command="${1:-check}"
case "$command" in
  check)
    build_release
    require_snapshots
    check_snapshots
    ;;
  refresh)
    build_release
    mkdir -p "$TEXT_DIR" "$JSON_DIR"
    write_snapshots "$SNAPSHOT_DIR"
    echo "Snapshots refreshed under $SNAPSHOT_DIR"
    ;;
  show)
    build_release
    case_name="${2:-}"
    if [[ -z "$case_name" ]]; then
      usage
      exit 1
    fi
    mode="${3:-text}"
    if [[ "$mode" == "json" ]]; then
      exec "$BINARY" "$case_name" --format json
    else
      exec "$BINARY" "$case_name"
    fi
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "Unknown command: $command" >&2
    echo >&2
    usage
    exit 1
    ;;
esac
