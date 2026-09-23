#!/usr/bin/env bash
# make_zip.sh — build the submission archive: the task folder alone, at the archive root.
# Usage: [TASK_DIR=task-g308] tools/make_zip.sh [out.zip]   (run from anywhere)
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASK_DIR="${TASK_DIR:-task}"          # e.g. TASK_DIR=task-g308 tools/make_zip.sh
cd "$REPO"
NAME="$(sed -n 's/^name = "obi\/\(.*\)"/\1/p' "$TASK_DIR/task.toml")"
OUT="${1:-$REPO/${NAME:-$TASK_DIR}.zip}"
find "$TASK_DIR" -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
find "$TASK_DIR" -name .DS_Store -delete 2>/dev/null || true
rm -rf $TASK_DIR/.pytest_cache
rm -rf $TASK_DIR/solution/files/.oracle_logs
# LF only: the QC lint rejects CRLF scripts, and Windows checkouts may have converted them
find "$TASK_DIR" -path $TASK_DIR/evaluations -prune -o -type f \( -name '*.sh' -o -name '*.py' -o -name '*.md' \
     -o -name '*.csv' -o -name '*.toml' -o -name '*.json' -o -name 'Dockerfile' \) -print0 \
  | xargs -0 sed -i 's/\r$//'

echo "== preflight =="
fail=0
for f in $TASK_DIR/task.toml $TASK_DIR/instruction.md $TASK_DIR/tests/manifest.json $TASK_DIR/solution/golden_trajectory.json \
         $TASK_DIR/README.md $TASK_DIR/review.csv; do
  [ -f "$f" ] && echo "ok   $f" || { echo "MISSING $f"; fail=1; }
done
grep -lI $'\r' $TASK_DIR/tests/test.sh $TASK_DIR/solution/solve.sh $TASK_DIR/environment/Dockerfile 2>/dev/null && { echo "CRLF in an entrypoint script"; fail=1; }
grep -qE '^FROM [^ ]+@sha256:[0-9a-f]{64}' $TASK_DIR/environment/Dockerfile && echo "ok   Dockerfile FROM pinned by digest" || { echo "Dockerfile FROM not pinned by digest"; fail=1; }
[ -f $TASK_DIR/qc_report.html ] && echo "ok   $TASK_DIR/qc_report.html" || echo "note $TASK_DIR/qc_report.html absent (fine for the FIRST gate run only)"
[ -f $TASK_DIR/tests/verifier.json ] || { echo "MISSING $TASK_DIR/tests/verifier.json"; fail=1; }
cmp -s $TASK_DIR/tests/verifier.json $TASK_DIR/tests/manifest.json && echo "ok   verifier.json == manifest.json" || { echo "tests/verifier.json and tests/manifest.json differ"; fail=1; }
for d in oracle nop platform; do [ -d "$TASK_DIR/evaluations/$d" ] && { echo "DISALLOWED $TASK_DIR/evaluations/$d"; fail=1; }; done
[ -d $TASK_DIR/evaluations/difficulty ] && [ "$(ls $TASK_DIR/evaluations/difficulty | wc -l)" -eq 4 ] && echo "ok   4 difficulty runs" || { echo "difficulty/ does not hold exactly 4 runs"; fail=1; }
[ -d $TASK_DIR/evaluations/solvability/r1 ] && echo "ok   solvability/r1" || echo "note no solvability/r1 (only valid in the 0/4 case)"
loose=$(find $TASK_DIR/evaluations -maxdepth 1 -type f | wc -l); [ "$loose" -eq 0 ] || { echo "LOOSE files under evaluations/"; fail=1; }
head -1 $TASK_DIR/review.csv 2>/dev/null | grep -qx 'review_check,status,review_notes,change_made,what_to_record' && echo "ok   review.csv header" || { echo "review.csv header wrong"; fail=1; }
[ $fail -eq 0 ] || { echo "preflight failed"; exit 1; }

rm -f "$OUT"
# archive root is the task name (the accepted bundles are laid out this way; the platform
# reads the task id from the root folder), whatever the repo folder is called
STAGE="$(mktemp -d)"; cp -r "$TASK_DIR" "$STAGE/${NAME:-$TASK_DIR}"
( cd "$STAGE" && zip -qr "$OUT" "${NAME:-$TASK_DIR}" -x '*/__pycache__/*' )
rm -rf "$STAGE"
echo "== wrote $OUT"; unzip -l "$OUT" | tail -1
