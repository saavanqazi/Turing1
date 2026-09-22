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
# LF only: the QC lint rejects CRLF scripts, and Windows checkouts may have converted them
find task -path task/evaluations -prune -o -type f \( -name '*.sh' -o -name '*.py' -o -name '*.md' \
     -o -name '*.csv' -o -name '*.toml' -o -name '*.json' -o -name 'Dockerfile' \) -print0 \
  | xargs -0 sed -i 's/\r$//'

echo "== preflight =="
fail=0
for f in task/task.toml task/instruction.md task/tests/manifest.json task/solution/golden_trajectory.json \
         task/README.md task/review.csv; do
  [ -f "$f" ] && echo "ok   $f" || { echo "MISSING $f"; fail=1; }
done
grep -lI $'\r' task/tests/test.sh task/solution/solve.sh task/environment/Dockerfile 2>/dev/null && { echo "CRLF in an entrypoint script"; fail=1; }
grep -qE '^FROM [^ ]+@sha256:[0-9a-f]{64}' task/environment/Dockerfile && echo "ok   Dockerfile FROM pinned by digest" || { echo "Dockerfile FROM not pinned by digest"; fail=1; }
[ -f task/qc_report.html ] && echo "ok   task/qc_report.html" || echo "note task/qc_report.html absent (fine for the FIRST gate run only)"
[ -f task/tests/verifier.json ] || { echo "MISSING task/tests/verifier.json"; fail=1; }
cmp -s task/tests/verifier.json task/tests/manifest.json && echo "ok   verifier.json == manifest.json" || { echo "tests/verifier.json and tests/manifest.json differ"; fail=1; }
for d in oracle nop platform; do [ -d "task/evaluations/$d" ] && { echo "DISALLOWED task/evaluations/$d"; fail=1; }; done
[ -d task/evaluations/difficulty ] && [ "$(ls task/evaluations/difficulty | wc -l)" -eq 4 ] && echo "ok   4 difficulty runs" || { echo "difficulty/ does not hold exactly 4 runs"; fail=1; }
[ -d task/evaluations/solvability/r1 ] && echo "ok   solvability/r1" || echo "note no solvability/r1 (only valid in the 0/4 case)"
loose=$(find task/evaluations -maxdepth 1 -type f | wc -l); [ "$loose" -eq 0 ] || { echo "LOOSE files under evaluations/"; fail=1; }
head -1 task/review.csv 2>/dev/null | grep -qx 'review_check,status,review_notes,change_made,what_to_record' && echo "ok   review.csv header" || { echo "review.csv header wrong"; fail=1; }
[ $fail -eq 0 ] || { echo "preflight failed"; exit 1; }

rm -f "$OUT"
zip -qr "$OUT" task -x 'task/**/__pycache__/*'
echo "== wrote $OUT"; unzip -l "$OUT" | tail -1
