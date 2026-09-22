#!/usr/bin/env bash
# make_zip.sh — build the submission archive: the task folder alone, at the archive root.
# Usage: tools/make_zip.sh [out.zip]     (run from anywhere)
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$REPO/bus-mg-bus-b7-a4-same-day-power-cord-sourcing.zip}"

cd "$REPO"
find task -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
find task -name .DS_Store -delete 2>/dev/null || true
rm -rf task/.pytest_cache
rm -rf task/solution/files/.oracle_logs

echo "== preflight =="
fail=0
for f in task/task.toml task/instruction.md task/tests/manifest.json task/solution/golden_trajectory.json \
         task/README.md task/review.csv; do
  [ -f "$f" ] && echo "ok   $f" || { echo "MISSING $f"; fail=1; }
done
[ -f task/qc_report.html ] && echo "ok   task/qc_report.html" || echo "note task/qc_report.html absent (fine for the FIRST gate run only)"
[ -e task/tests/verifier.json ] && { echo "STALE task/tests/verifier.json still present"; fail=1; }
for d in oracle nop platform; do [ -d "task/evaluations/$d" ] && { echo "DISALLOWED task/evaluations/$d"; fail=1; }; done
[ -d task/evaluations/difficulty ] && [ "$(ls task/evaluations/difficulty | wc -l)" -eq 4 ] && echo "ok   4 difficulty runs" || { echo "difficulty/ does not hold exactly 4 runs"; fail=1; }
[ -d task/evaluations/solvability/r1 ] && echo "ok   solvability/r1" || echo "note no solvability/r1 (only valid in the 0/4 case)"
loose=$(find task/evaluations -maxdepth 1 -type f | wc -l); [ "$loose" -eq 0 ] || { echo "LOOSE files under evaluations/"; fail=1; }
head -1 task/review.csv 2>/dev/null | grep -qx 'review_check,status,review_notes,change_made,what_to_record' && echo "ok   review.csv header" || { echo "review.csv header wrong"; fail=1; }
[ $fail -eq 0 ] || { echo "preflight failed"; exit 1; }

rm -f "$OUT"
zip -qr "$OUT" task -x 'task/**/__pycache__/*'
echo "== wrote $OUT"; unzip -l "$OUT" | tail -1
