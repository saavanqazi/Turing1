#!/usr/bin/env bash
# collect_runs.sh — copy four GLM trial folders into task/evaluations/difficulty/r1..r4,
# put the first passing one into solvability/r1, and annotate result.json.
#
# Usage:  tools/collect_runs.sh /tmp/harbor-jobs/<glm-job-dir>
# Run from the repo root after the four-run battery is finished.
set -euo pipefail

JOB_DIR="${1:?usage: tools/collect_runs.sh /tmp/harbor-jobs/<job>}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVAL="$REPO/task/evaluations"

rm -rf "$EVAL"
mkdir -p "$EVAL/difficulty" "$EVAL/solvability"

i=0
solv=""
for trial in "$JOB_DIR"/*/; do
  [ -f "$trial/result.json" ] && [ -d "$trial/verifier" ] || continue   # skip job-level files
  i=$((i+1))
  dst="$EVAL/difficulty/r$i"
  mkdir -p "$dst/agent" "$dst/verifier"
  cp "$trial/agent/trajectory.json" "$dst/agent/" 2>/dev/null || echo "WARN: r$i has no agent/trajectory.json"
  cp "$trial/result.json" "$dst/"
  [ -f "$trial/config.json" ] && cp "$trial/config.json" "$dst/"
  for f in reward.json reward.txt verifier_summary.json ctrf.json score.json test-stdout.txt; do
    [ -f "$trial/verifier/$f" ] && cp "$trial/verifier/$f" "$dst/verifier/"
  done
  r=$(cat "$trial/verifier/reward.txt")
  echo "r$i <- $(basename "$trial")  reward=$r"
  if [ -z "$solv" ] && [ "$r" = "1.0" ]; then solv="$dst"; fi
done

[ "$i" -eq 4 ] || echo "WARN: expected 4 trials, found $i — ship exactly four"

if [ -n "$solv" ]; then
  cp -r "$solv" "$EVAL/solvability/r1"
  echo "solvability/r1 <- $(basename "$solv")"
else
  rmdir "$EVAL/solvability"
  echo "NOTE: no run scored 1.0 — no solvability/ folder (0/4 case, Turing re-runs)"
fi

python3 "$REPO/tools/annotate_rollout.py" "$EVAL"/difficulty/r* ${solv:+"$EVAL/solvability/r1"}

# never ship job-level artifacts
find "$EVAL" -maxdepth 1 -type f -delete
echo; echo "tree:"; find "$EVAL" -type f | sort
