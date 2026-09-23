# g308 — your steps (Windows cmd, in the Turing1 folder)

> **Status:** round 1 oracle 1.0, GLM 8/8 (too easy). Round 2 pushed: run Steps A, C, D again with the `-r2` job names.

Same pattern as the cord task. Task folder is `task-g308`. Job names carry `g308`.

## Step A — pull and refresh

```bat
git pull
git rm -r --cached -q . && git reset --hard -q
```

## Step B — baseline battery on the untouched mined package (recommended, ~12 min)

Commit `e479df2` holds the mined package.

```bat
git worktree add ..\g308-baseline e479df2
harbor run -p ..\g308-baseline\task-g308 -a terminus-2 -m openai/glm-5.2 -k 4 -n 4 --env-file glm.env -o jobs --job-name glm-g308-baseline -y
for /d %d in (jobs\glm-g308-baseline\*) do @type "%d\verifier\reward.txt"
```

Send me the four rewards. (Expected 4/4.)

## Step C — oracle on the hardened task

```bat
harbor run -p task-g308 -a oracle -k 1 -n 1 --env-file glm.env -o jobs --job-name oracle-g308-r2 -y
for /d %d in (jobs\oracle-g308-r2\*) do @type "%d\verifier\reward.txt"
```

Must print `1.0`. If not, stop and send me `jobs\oracle-g308-r2\<trial>\verifier\test-stdout.txt`.

## Step D — eight GLM runs

```bat
docker ps --format "{{.Names}}"
harbor run -p task-g308 -a terminus-2 -m openai/glm-5.2 -k 8 -n 4 --env-file glm.env -o jobs --job-name glm-g308-r2 -y
for /d %d in (jobs\glm-g308-r2\*) do @type "%d\verifier\reward.txt"
```

Send me the eight rewards and a zip of the whole `jobs\glm-g308-r2` folder. I classify
every failure, pick the first four by start time if 3–5 of 8 passed, and build the
evidence, README figures and review.csv. If 7–8 pass I push round 2 (job names `-r2`);
if 0–1 pass I check for unfairness first.

## Step E — Delivery Gate, twice

I send you the zip. Upload it as a new task, run the Gate, send me the report card and
the `qc_report.html`; I add the report, rebuild, you upload the new version, run the Gate
again and Submit.
