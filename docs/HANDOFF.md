# Your steps, in order (Windows cmd)

> **Status:** Steps 1–5 and 7 are done (baseline 4/4, round 1 4/4, round 2 3/4; oracle 1.0;
> evidence under task/evaluations; task/review.csv written). Remaining: Step 6 (final oracle,
> optional record run), Step 8 (Delivery Gate twice), Step 9.

Everything that needs Docker, harbor, the GLM key or the QC website is yours.
Paste the printed output of each step back into the session; I read it and do
the next edits. All commands run in cmd inside the `Turing1` folder.

Harbor pattern used throughout (your own, from earlier tasks):

```
harbor run -p <task-folder> -a <agent> [-m openai/glm-5.2] -k <total runs> -n <at once> --env-file glm.env -o jobs --job-name <name> -y
```

## Step 1 — Set up (once)

```bat
cd %USERPROFILE%
git clone https://github.com/saavanqazi/Turing1
cd Turing1
git checkout claude/benchmark-task-hardening-rv3am4
git log --oneline -3
docker ps --format "{{.Names}}"
harbor --version
notepad glm.env
```

In Notepad paste exactly these three lines with your real key, save, close:

```
OPENAI_API_KEY=<your key>
OPENAI_BASE_URL=http://34.41.10.8:4000/v1
JUDGE_MODEL=openai/glm-5.2
```

`JUDGE_MODEL` must be exactly `openai/glm-5.2` (no trailing letter). `glm.env`
and `jobs\` are in `.gitignore`, so git will never push your key or the run
folders.

## Step 2 — Baseline measurement (optional, recommended)

Gives the README its "before" figure. Commit `b41f537` is the untouched mined
package.

```bat
git worktree add ..\b7a4-baseline b41f537
harbor run -p ..\b7a4-baseline\task -a oracle -k 1 -n 1 --env-file glm.env -o jobs --job-name oracle-b7a4-baseline -y
for /d %d in (jobs\oracle-b7a4-baseline\*) do @type "%d\verifier\reward.txt"
```

Expect `1.0`. Then the four GLM runs on the baseline:

```bat
harbor run -p ..\b7a4-baseline\task -a terminus-2 -m openai/glm-5.2 -k 4 -n 2 --env-file glm.env -o jobs --job-name glm-b7a4-baseline -y
for /d %d in (jobs\glm-b7a4-baseline\*) do @type "%d\verifier\reward.txt"
```

**Send me:** the four numbers. Expected 4/4. Skip this step if time is short.

## Step 3 — Round oracle (round 1 done: 1.0. Now run for round 2 with `oracle-b7a4-r2`)

```bat
harbor run -p task -a oracle -k 1 -n 1 --env-file glm.env -o jobs --job-name oracle-b7a4-r2 -y
for /d %d in (jobs\oracle-b7a4-r2\*) do @type "%d\verifier\reward.txt"
```

Must print `1.0`. If not, **stop** and send me the file
`jobs\oracle-b7a4-r2\<trial>\verifier\test-stdout.txt`.

## Step 4 — Round GLM battery (round 1 done: 4/4. Now run round 2 with `glm-b7a4-r2`)

```bat
docker ps --format "{{.Names}}"
harbor run -p task -a terminus-2 -m openai/glm-5.2 -k 1 -n 1 --env-file glm.env -o jobs --job-name glm-b7a4-smoke -y
for /d %d in (jobs\glm-b7a4-smoke\*) do @type "%d\verifier\reward.txt"
```

If the smoke run finishes without a crash (a reward of 0.0 or 1.0 is both
fine here), run the real battery:

```bat
harbor run -p task -a terminus-2 -m openai/glm-5.2 -k 4 -n 2 --env-file glm.env -o jobs --job-name glm-b7a4-r2 -y
for /d %d in (jobs\glm-b7a4-r2\*) do @type "%d\verifier\reward.txt"
```

Use `-n 3` if `docker ps` showed nothing else running; `-n 1` if the machine
is slow.

**Send me:**

1. the four rewards,
2. for every run below 1.0: `verifier\verifier_summary.json`,
   `verifier\score.json`, and `exception.txt` if it exists,
3. `dir jobs\glm-b7a4-r2\<trial>\agent` for any trial that has no
   `trajectory.json`.

I classify each failure. Then:

- 1, 2 or 3 of 4 pass → Step 5.
- 4 of 4 → I push the next round; you repeat Steps 3 and 4 with the next job
  names (`oracle-b7a4-r3`, `glm-b7a4-r3`).
- 0 of 4 → I check the failures for unfairness before we decide.

## Step 5 — Collect the evidence (DONE by Claude from the uploaded run zips)

`tools\collect_runs.sh` is a bash script. Open **Git Bash** in the `Turing1`
folder (right-click → "Git Bash Here") and run:

```bash
git pull
tools/collect_runs.sh jobs/glm-b7a4-r2
git add task/evaluations
git commit -m "Add GLM-5.2 difficulty and solvability evidence"
git push
```

**Send me:** the tree the script prints. I fill the bracketed figures in
`task/README.md` and `docs/review_rows_draft.md` and push.

## Step 6 — Final oracle (cmd) — REQUIRED: the grader loaders changed back to verifier.json

```bat
git pull
harbor run -p task -a oracle -k 1 -n 1 --env-file glm.env -o jobs --job-name oracle-b7a4-final -y
for /d %d in (jobs\oracle-b7a4-final\*) do @type "%d\verifier\reward.txt"
```

Must print `1.0`.

## Step 7 — review.csv (DONE: generated from the review record at task/review.csv; the form is optional)

1. Copy the `task` folder to Google Drive (the folder, not a zip).
2. Open the review form, sign in with your Turing Google account, paste the
   Drive folder link.
3. Fill the fourteen rows from `docs/review_rows_draft.md` (I will have
   replaced the brackets). Layer 2 Stability and Cross-trial Calibration: the
   one line "Turing runs this".
4. Download `review.csv`, put it at `task\review.csv`, then in cmd:

```bat
git add task\review.csv
git commit -m "Add review.csv"
git push
```

## Step 8 — Delivery Gate, twice

In Git Bash:

```bash
tools/make_zip.sh
```

It preflights the bundle and writes `bus-mg-bus-b7-a4-same-day-power-cord-sourcing.zip`
in the `Turing1` folder.

1. Upload that zip to https://qc-api-713053229214.us-central1.run.app/ and run
   the Delivery Gate. Do the manual checklist in the right pane while it runs.
2. Expected finding: R3 stability → mark reviewed with "Turing runs stability".
   Anything else → send me the report; I fix, you re-zip and re-run.
3. Download `qc_report.html` into `task\`, then commit and push it.
4. Run `tools/make_zip.sh` again → upload as a **new version of the same
   task** → run the Gate again → Submit that version.

## Step 9 — Watch the pipeline

Queued → Running → Accepted. On "Rejected · N findings", send me the
findings; we loop from Step 3 with a new version.
