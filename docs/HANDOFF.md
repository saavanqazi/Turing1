# Your steps, in order

Everything in the repo is ready for round 1. You run the parts that need Docker,
harbor, the GLM key and the QC website. After each step, paste the output back
into the session; I do the reading and the next edits.

Run all commands from the repo root on your workstation.

## Step 1 — Set up (once, ~20 min)

```bash
git clone https://github.com/saavanqazi/Turing1 && cd Turing1
git checkout claude/benchmark-task-hardening-rv3am4
source ~/.config/harbor/env          # every session, before anything else
echo "$OPENAI_BASE_URL $JUDGE_MODEL"  # must print the proxy URL and openai/glm-5.2
docker ps --format '{{.Names}}'      # budget check
```

Create `glm-harbor-config.json` from your usual template and set:

- `tasks[0].path` = `task`
- `job_name` = `glm-b7a4-r1`

## Step 2 — Baseline measurement (optional but recommended, ~1.5 h wall)

The README needs a "before" figure. The untouched mined package is at commit
`b41f537`. Check it out into a scratch folder and run oracle + battery there:

```bash
git worktree add ../b7a4-baseline b41f537
harbor run -p ../b7a4-baseline/task -a oracle \
  --ve OPENAI_API_KEY="$OPENAI_API_KEY" --ve OPENAI_BASE_URL="$OPENAI_BASE_URL" \
  -o /tmp/harbor-jobs --job-name oracle-b7a4-baseline -n 1 -y
cat /tmp/harbor-jobs/oracle-b7a4-baseline/*/verifier/reward.txt        # expect 1.0
```

Point a copy of the config at `../b7a4-baseline/task` with `job_name`
`glm-b7a4-baseline`, then:

```bash
harbor run -c glm-harbor-config-baseline.json -n 1 -y
harbor run -c glm-harbor-config-baseline.json -n 3 -k 4 -y
cat /tmp/harbor-jobs/glm-b7a4-baseline/*/verifier/reward.txt
```

**Send me:** the four rewards. (Expected 4/4.) You can skip this step if time
is short; the README then says "baseline not measured, task was trivially
scriptable".

## Step 3 — Round 1 oracle (~10 min)

```bash
harbor run -p task -a oracle \
  --ve OPENAI_API_KEY="$OPENAI_API_KEY" --ve OPENAI_BASE_URL="$OPENAI_BASE_URL" \
  -o /tmp/harbor-jobs --job-name oracle-b7a4-r1 -n 1 -y
cat /tmp/harbor-jobs/oracle-b7a4-r1/*/verifier/reward.txt
```

Must print `1.0`. If not, **stop** and send me
`/tmp/harbor-jobs/oracle-b7a4-r1/*/verifier/test-stdout.txt`.

## Step 4 — Round 1 GLM battery (~1–2 h wall)

```bash
docker ps --format '{{.Names}}'
harbor run -c glm-harbor-config.json -n 1 -y            # smoke test
harbor run -c glm-harbor-config.json -n 3 -k 4 -y       # the battery (4 total)
cat /tmp/harbor-jobs/glm-b7a4-r1/*/verifier/reward.txt
```

**Send me:**

1. the four rewards,
2. for every run that is not 1.0: `verifier/verifier_summary.json`,
   `verifier/score.json`, the agent's `offer_evaluation.csv` and `results.json`
   if they are in the trial folder, and `exception.txt` if it exists,
3. `ls` of any trial with no `agent/trajectory.json`.

I classify each failure (MODEL / ambiguity / verifier / infra) and decide:

- 1, 2 or 3 of 4 pass → go to Step 5.
- 4 of 4 → I push round 2 (price overrides + moving the fit thresholds into the
  data sheet); you repeat Steps 3 and 4 with job names `oracle-b7a4-r2`,
  `glm-b7a4-r2`.
- 0 of 4 → I check for unfairness first; if the failures are genuine MODEL
  failures we ship as 0/4 and say so.

## Step 5 — Collect the evidence (~10 min)

```bash
git pull
tools/collect_runs.sh /tmp/harbor-jobs/glm-b7a4-r1      # or -r2 …
git add task/evaluations && git commit -m "Add GLM-5.2 difficulty and solvability evidence" && git push
```

**Send me:** the script's printed tree. I fill the bracketed figures in
`task/README.md` and `docs/review_rows_draft.md`, run the final oracle-after-
rename check on my side with the engine, and push.

## Step 6 — Final oracle after packaging (~10 min)

```bash
git pull
harbor run -p task -a oracle \
  --ve OPENAI_API_KEY="$OPENAI_API_KEY" --ve OPENAI_BASE_URL="$OPENAI_BASE_URL" \
  -o /tmp/harbor-jobs --job-name oracle-b7a4-final -n 1 -y
cat /tmp/harbor-jobs/oracle-b7a4-final/*/verifier/reward.txt          # 1.0
```

## Step 7 — review.csv through the form (~30 min, must be you)

1. Copy the `task/` folder to Google Drive (the folder, not a zip).
2. Open the review form, sign in with your Turing Google account, paste the
   Drive folder link.
3. Fill the fourteen rows from `docs/review_rows_draft.md` (brackets already
   replaced by me). Layer 2 Stability and Cross-trial Calibration: one line
   "Turing runs this".
4. Download `review.csv` and place it at `task/review.csv`. Commit and push.

## Step 8 — Delivery Gate, twice (~45 min)

```bash
tools/make_zip.sh            # preflight + zip of task/ alone
```

1. Upload the zip to https://qc-api-713053229214.us-central1.run.app/ and run
   the Delivery Gate. Do the manual checklist in the right pane while it runs.
2. Expected finding: R3 stability → mark reviewed, note "Turing runs stability".
   Any other finding → send me the report; I fix, you re-zip and re-run.
3. Download `qc_report.html` → `task/qc_report.html`. Commit and push.
4. `tools/make_zip.sh` again → upload as a **new version of the same task** →
   run the Gate again → Submit that version.

## Step 9 — Watch the pipeline

Queued → Running → Accepted. On "Rejected · N findings", send me the findings;
the fix loop is Steps 3–8 again with a new version.
