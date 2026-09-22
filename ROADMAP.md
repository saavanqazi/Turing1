# Roadmap — `bus-mg-bus-b7-a4-same-day-power-cord-sourcing`

> **Status 2026-09-22:** Phases 1–6 done. Round 1 GLM 4/4, round 2 GLM 3/4 (rewards 0.0, 1.0, 1.0, 1.0), oracle 1.0; evidence in `task/evaluations/`. Remaining: review.csv via the form, Delivery Gate loop (`docs/HANDOFF.md` Steps 6–9).

Phase-wise plan to take the mined package from the uploaded zip to a submittable
delivery bundle that clears both gates (Oracle = 1.0, GLM-5.2 = 1–3 of 4 passing)
and carries `README.md`, `review.csv` and `qc_report.html`.

Source: `bcd4736b-bus-mg-bus-b7-a4-same-day-power-cord-sourcing-20260922T150313Z-1-001.zip`

---

## 0. What the package is (baseline read, 2026-09-22)

**The ask.** A buyer in Phenix City, AL (14:40 Friday, Central) needs a 10-ft
figure-8 (IEC C7, non-polarized) AC cord today from Kestrel. Eleven same-day
offers (pickup/delivery) across five stores must each be ruled eligible or not
under terms S1–S7, with the first refusing clause as `reason_code` and the landed
cost (shelf price + fulfilling store's tax, rounded, + USD 9.99 delivery fee) for
eligible ones. Deliverables: `offer_evaluation.csv` and `results.json`
(`eligible_offer_count`, `chosen_offer_id`, `chosen_total_usd`).

**Inputs** (`environment/input/`): `cord_catalogue.csv` (8 SKUs),
`power_supply_spec.md`, `same_day_offers.csv` (11 offers), `store_directory.csv`
(5 stores, two in `America/New_York`), `same_day_terms.md` (S1–S7),
`standard_delivery.md` (distractor), `submission_format.md`.

**Gold** (`solution/files/`): 4 eligible (OF-02 19.61, OF-04 24.08, OF-08 24.13,
OF-09 34.12); chosen OF-02 at 19.61. Independently recomputed by hand — correct.

**Verifiers** (`tests/verifier.json`, 6 checks, all `metadata.tag = core`):
`evaluation_exists`, `evaluation_header` (tolerant regex), `evaluation_table_trap_of01`
(OF-01 row), `evaluation_table` (10 rows + 11-id row_set + closed columns),
`results_figures` (closed 3-key object, ±0.01 on the total), `results_exists`.
Scoring is core-gated (`tests/score.py`): any core failure → reward 0.0. So every
run reads exactly 1.0 or 0.0. There are no secondary verifiers to delete.

**Prior evidence shipped:** `evaluations/oracle/` (reward 1.0) and
`evaluations/nop/` (reward 0.0). Both must go — the gate only accepts
`solvability/`, `difficulty/`, `stability/` under `evaluations/`.

**Verified in this session:** the vendored engine replays gold at reward 1.0
(`HARBOR_TASK_WORKSPACE=<gold files> python3 tests/score.py` → 1.0, 6/6).

**Baseline defects / gaps versus the delivery spec**

| # | Finding | Fix phase |
|---|---|---|
| B1 | `tests/verifier.json` must become `tests/manifest.json`; `score.py` and `test_outputs.py` load the spec by that name (lines 38 / 41) | 6 |
| B2 | `evaluations/oracle/` and `evaluations/nop/` are disallowed folders; no `difficulty/`, no `solvability/` | 6 |
| B3 | No `README.md`, `review.csv`, `qc_report.html` | 7–8 |
| B4 | Task is trivially scriptable: 8 independent rules, one trap (state line), `STOCK_RESERVE` and every tie-break never fire. Expect 4/4 | 4–5 |
| B5 | `consistency/` is mining-pipeline metadata (requirements.json, mutations.json) that goes stale the moment the gold changes; not in the spec layout | 6 |
| B6 | `solution/solve.sh` installs static files; the gold, the verifier expected values and `golden_trajectory.json` (which embeds the CSV in a heredoc) are three hand-kept copies of one answer | 4 |

Core pieces (task.toml, instruction.md, tests/, environment/, solution/) are all
present — nothing to report back as missing.

**Where each phase can run.** This remote session has Python and the verifier
engine but no Docker daemon, no `harbor`, and no GLM key. Phases 1, 4, 5(a–c),
6, 7 are doable here and committed to `claude/benchmark-task-hardening-rv3am4`.
Phases 2, 3, 5(d–e), 8, 9 need the workstation with Docker + harbor +
`~/.config/harbor/env` and the QC platform login.

---

## Phase 0 — Setup (workstation, ~30 min)

1. `source ~/.config/harbor/env` (every session). Confirm `OPENAI_API_KEY`,
   `OPENAI_BASE_URL`, `JUDGE_MODEL=openai/glm-5.2` are set.
2. `docker ps --format '{{.Names}}'` — budget check.
3. Clone the branch, unzip the package into `task/` at repo root (keep the
   original zip untouched outside the repo).
4. Write `glm-harbor-config.json` with `tasks[0].path = task` and a `job_name`.
5. Commit the untouched mined baseline as the first commit so every later diff
   is auditable ("what changed from the mined baseline" is a README requirement).

Exit: harbor, Docker and the key all respond; baseline committed.

---

## Phase 1 — Picky-reviewer read (this session, ~1 h)

Read `instruction.md` cold, list every guess, compare to gold. Findings so far:

- **Guess list (all resolved by the inputs, none ambiguous):** whose clock for
  the cutoff (S1 says store's); whether the fee is taxed (S6 says no); rounding
  order (tax rounded to cent, then fee); whether 10 ft is exact (S4: 10–15
  inclusive); precedence when two clauses fail (S5 lists it). No open ambiguity.
- **Leakage:** none in the prompt. Verifier names (`..._trap_of01`) never enter
  the image (Dockerfile copies `input/` only).
- **References exist:** every file named in the prompt ships in `input/`.
- **Forward map** (instruction → verifiers): sheet exists + header → 2 checks;
  every row's decision/reason/cost → 2 checks; count/chosen/total → 1 check +
  exists. Complete.
- **Backward map** (verifiers → instruction): nothing grades an unasked thing.
  `evaluation_table_trap_of01` and `evaluation_table` both serve the "every row"
  ask but grade disjoint rows, so no double payment. Keep both names (Phase 6
  stability of check names) — or fold OF-01 into `evaluation_table`; either is
  defensible, folding is cleaner. Decide in Phase 5 when rows are regenerated.
- **Regex:** only the header check uses regex, and it is already case- and
  quote-tolerant. Landed cost cells compare numerically (±0.001). Fine.
- **Secondary verifiers:** none (`metadata.tag` is `core` everywhere).

Deliverable: findings folded into the `review.csv` rows for Layer 1 (Phase 7).

---

## Phase 2 — Baseline Oracle (workstation, ~15 min)

```bash
harbor run -p task -a oracle \
  --ve OPENAI_API_KEY="$OPENAI_API_KEY" --ve OPENAI_BASE_URL="$OPENAI_BASE_URL" \
  -o /tmp/harbor-jobs --job-name oracle-b7a4-baseline -n 1 -y
cat /tmp/harbor-jobs/oracle-b7a4-baseline/*/verifier/reward.txt   # expect 1.0
```

Exit: 1.0 on the untouched baseline (the shipped oracle evidence says it was
1.0 on 2026-09-20; re-prove it on our infra). Keep the trial dir for reference
only — oracle evidence never ships.

---

## Phase 3 — Baseline GLM-5.2 battery (workstation, ~1–2 h wall clock)

```bash
harbor run -c glm-harbor-config.json -n 1 -y                # smoke test
harbor run -c glm-harbor-config.json -n <3-minus-running> -k 4 -y
cat /tmp/harbor-jobs/<job>/*/verifier/reward.txt
```

For each run: read `verifier/verifier_summary.json` items in full, check for
`exception.txt` / missing `agent/trajectory.json`, and classify a fail as
MODEL / ambiguity / verifier bug / infra.

Expected: 4/4. That is the signal to harden, not a defect. Record the four
rewards; they go in README and the Layer 2 Difficulty row as the "before".

---

## Phase 4 — Hardening design (this session, ~2 h)

Principle: coupled reasoning, not more independent rules. Every change below
makes one figure depend on the interaction of two sources or two steps, has an
explicit clause so a careful analyst lands on one answer, and moves at least
one graded cell. Ordered by leverage; implement H1, H2, H4, H6 first, measure,
then add H3 / H5 only if still 4/4.

| ID | Lever | Change | Why it couples | Ambiguity guard |
|---|---|---|---|---|
| H1 | input data + terms | Replace the `on_hand` snapshot with `stock_ledger.csv`: per store×SKU opening count at 09:00 plus timestamped intraday movements (sales, a customer hold, a transfer out) stamped in **store-local** time. Effective stock = opening + every movement at or before the order instant on that store's clock. New reason `NO_STOCK` (effective < 1, either method), slotted after `FIT_LENGTH` and before `STOCK_RESERVE` in S5 and in `submission_format.md`. A pickup and a delivery offer for the same store/SKU share one stock figure. | Stock now depends on the timezone reasoning (a 15:05 movement at an Eastern store has already happened, a 15:05 one at a Central store has not) and on dedupe across offers. `STOCK_RESERVE` finally fires. | S2 gains one sentence defining "effective stock" and the clock used for movements. |
| H2 | terms | Destination-based tax: collection taxed at the fulfilling store's rate; delivery taxed at the delivery address's rate, looked up in a new `tax_jurisdictions.csv` (city/state → combined rate; includes Phenix City 9.75, Columbus 8.00, Auburn, Opelika). | Method → jurisdiction → rate; a delivery from an Alabama store still uses the buyer's rate, not the store's. Moves OF-09-class costs. | S6 names the file and the rule in one sentence. |
| H4 | input data | After H1/H2 land, set catalogue prices so two eligible offers land on the **same cent**, one pickup and one delivery (or two pickups at different distances), so the S6 tie-break chain (ready earliest → nearer → lower id) decides `chosen_offer_id`. | The choice depends on reading the tie-break, computing pickup-ready (order + 2 h store-local) vs delivery (by 20:00), then distance. | Tie-break already fully specified in S6; only the data changes. Verify with the gold generator that exactly one offer wins. |
| H6 | input data | Grow to ~16 offers and ~11 SKUs with precedence/boundary edge rows: 8-ft 20 AWG (→ `FIT_GAUGE`, not `FIT_LENGTH`), 6-ft 20 AWG (gauge rule only over 6 ft → `FIT_LENGTH`), 15-ft 20 AWG (`FIT_GAUGE`), 20-ft 18 AWG (`FIT_LENGTH`), a delivery offer that fails radius **and** reserve (→ `STOCK_RESERVE` by precedence), a suspended Eastern store (→ `SAME_DAY_SUSPENDED` over `CUTOFF_PASSED`, already present as OF-05). | Naive per-rule scripts that check clauses in file order, or that apply the gauge rule unconditionally, misclassify these rows. | All rows resolve under the existing S4/S5 text. |
| H3 | input data + terms | `store_price_overrides.csv` (store_id, sku, shelf_price_usd, valid_through as store-local time). Override applies only while valid at the order instant on the store's clock, else catalogue price. Put one override at a Central store with `valid_through 14:30` (expired) and one with `16:00` (live). | Price depends on time-zone reasoning and a fallback; one expired override changes the chosen offer. | S6 gets one sentence: "shelf price is the live override where one exists for that store and SKU, otherwise the catalogue price". |
| H5 | terms + spec | Move the gauge threshold (18 AWG over 6 ft) and the length floor ("no shorter than the supplied cord") into `power_supply_spec.md`; S4 says "meets the data sheet's conductor and length requirements" and keeps only the 15-ft ceiling. | The fit rule can no longer be read from one file. | Numbers stay explicit, just in the data sheet; no new interpretation. |

Instruction rewrite (keep 90–150 words, human voice, no recipe, no paths):
mention the new files naturally ("the stock ledger the stores share", "the tax
table", "the shelf-price specials"), keep the time and place, keep the three
asks. Do **not** state counts, thresholds or method. The harness-appended
`Working environment` block stays as is.

Build a single generator, `solution/compute_gold.py`, that reads
`environment/input/` and emits: `solution/files/offer_evaluation.csv`,
`solution/files/results.json`, the `rows`/`row_set`/`keys` blocks for the
verifier spec, and `solution/golden_trajectory.json` (heredoc regenerated).
This kills defect B6: one command regenerates all three copies after every
data tweak. `solve.sh` stays as the installer of `solution/files/`.

Exit: design table above filled with concrete rows/prices in a scratch sheet;
expected new gold produced by the generator and sanity-checked by hand.

---

## Phase 5 — Implement + measure loop (this session for a–c, workstation for d–e)

Repeat until the battery lands at 1/4, 2/4 or 3/4.

a. Apply the round's H-changes to `environment/input/*`, `same_day_terms.md`,
   `submission_format.md` (add `NO_STOCK` to the allowed values), `instruction.md`.
b. `python3 solution/compute_gold.py` → gold files + spec blocks + trajectory.
   Paste the spec blocks into `tests/verifier.json` (expected rows, row_set,
   results keys). Check every reason code in the gold appears in the format doc.
c. Local replay: `HARBOR_TASK_WORKSPACE=solution/files python3 tests/score.py`
   → 1.0, and `python3 -m pytest tests/test_outputs.py` on a copy of the gold
   workspace → all lanes green (the negative lanes prove the numbers are
   load-bearing). Commit the round.
d. Workstation: Phase 2 oracle command again (new job name). Must be 1.0.
e. Workstation: Phase 3 battery again (`-k 4`). Read all four
   `verifier_summary.json`; classify every failure. Only MODEL failures count.
   Bimodal or ambiguity failures → fix the prompt/terms, not the data, and re-run.

Guardrails: never harden via hidden info, ambiguity, or narrowed tolerances;
never edit the gold by hand (always the generator); re-run the oracle after
every change, no exceptions. Verifier-only changes can be re-graded against
existing trajectories; instruction or input changes invalidate the four runs.

Exit: oracle 1.0 twice in a row on the final package; four GLM rewards
recorded with 1–3 exactly 1.0; per-run failure classification written down.

---

## Phase 6 — Packaging (this session, ~1 h)

1. **Manifest rename (B1).** `git mv tests/verifier.json tests/manifest.json`;
   change the two loaders in `tests/score.py:38` and `tests/test_outputs.py:41`
   to `manifest.json`; fix the docstring mention. Re-run local replay, then the
   workstation oracle once more (the rule: oracle after the rename).
2. **evaluations/ (B2).** Delete `oracle/` and `nop/`. Create:
   - `evaluations/difficulty/r1..r4/` — copy each GLM trial folder whole
     (`agent/trajectory.json`, `result.json`, `verifier/reward.json`,
     `verifier/verifier_summary.json`, trial `config.json`). Never the job-level
     `config.json`, `lock.json`, `job.log`, or job-root `result.json`.
   - `evaluations/solvability/r1/` — a copy of one difficulty run that scored
     1.0. Never an oracle run. If 0/4, leave it out and say so in README (Turing
     re-runs on another frontier model).
   - No `stability/`, no `platform/`, nothing loose directly under `evaluations/`.
3. **result.json annotation.** Small script `tools/annotate_rollout.py` that
   adds to each shipped rollout's `result.json`: `"model": "GLM-5.2"`,
   boolean `overall_pass` (reward == 1.0), `final_answer` (the run's
   `results.json` content), `reward`, and judge provenance
   (`{"judge": "deterministic file_check", "judge_model": null}`). Annotate,
   never alter harbor's own fields.
4. **consistency/ (B5).** Keep it in the repo for provenance; exclude it from
   the shipped zip (not in the spec layout, and stale after hardening).
5. **Hygiene.** `solution/files/` holds only the two deliverables; no `.oracle_logs`,
   no `__pycache__`, no `.DS_Store`; `task.toml` unchanged (name, timeouts,
   `network_mode` stay as mined).
6. Zip check: `zip -r task.zip task/` from the parent — the archive's root is
   the task folder, nothing else.

Exit: tree matches the spec layout exactly; oracle re-run after the rename = 1.0.

---

## Phase 7 — README.md and review.csv (this session drafts, you sign off)

**README.md** (short, cumulative): mined baseline → hardened final; the
before/after batteries with all four rewards each; why it is hard now (H1/H2/H4
coupling, edge rows); why rewards are binary (core-gated scoring, so "steady
0.2–0.35" cannot occur); any QC flag left unfixed (expect R3 stability →
"Turing runs stability"); note that `consistency/` was dropped from the bundle.

**review.csv** — write it through the review form (Drive link to the extracted
folder), not by hand. Twelve rows you own; drafts of the substance:

| review_check | status | what the row will say |
|---|---|---|
| Layer 1 · Package consistency | FIXED_AND_VERIFIED | verifier.json → manifest.json + loaders; evaluations restructured; gold/spec/trajectory regenerated from one generator |
| Layer 1 · Clarity and scope | FIXED_AND_VERIFIED or PASS | guess list resolved; instruction rewritten for new files without recipe |
| Layer 1 · Realism and leakage | PASS | no totals/method in prompt; tests never enter image |
| Layer 2 Difficulty | FIXED_AND_VERIFIED | baseline 4/4 (rewards) → final N/4 (rewards), cause H1/H2/H4/H6, paths `evaluations/difficulty/rX/verifier/reward.json` |
| Layer 2 Solvability | PASS | `evaluations/solvability/r1` reward 1.0, GLM-5.2, not oracle |
| Layer 2 Stability | (blank or "Turing runs this") | — |
| Layer 3 Oracle Mode | PASS / FIXED_AND_VERIFIED | oracle 1.0 on baseline, after each round, after the rename; job names listed |
| Layer 4 · Environment and files | PASS | Dockerfile copies input only; deps pinned; inputs read-only |
| Layer 4 · Connectors, MCPs, and CLIs | N/A | non-connector, `mcp_servers = []`, no `_app/` mirror |
| Layer 4 · Deliverables and artifact quality | PASS | two files, format doc matches verifiers, NO_STOCK added to allowed values |
| Layer 5 · Verifier coverage and fairness | PASS / FIXED | forward+backward map closed; only tolerant header regex; ±0.01 on total |
| Layer 5 · LLM judge consistency | N/A | no judged rubric in the manifest (say so) |
| Layer 5 · Reward hacking and exploitability | PASS | closed key set, row_set lock, negative lanes in test_outputs.py |
| Cross-trial · Calibration | (blank or one line) | — |

Only PASS / FIXED_AND_VERIFIED / N/A. `change_made` filled on every FIXED row.
`what_to_record` names the oracle job and battery that re-proved it.

---

## Phase 8 — Delivery Gate loop (workstation, ~30–45 min incl. two gate runs)

1. Zip the task folder alone; upload to the QC platform; run the Delivery Gate.
2. Read the report card. Expected: R3 (stability) → mark reviewed, note
   "Turing runs stability". Anything else → fix in the bundle, update the
   `review.csv` row, and start Phase 8 again.
3. Download `qc_report.html`, drop it at the task root next to `review.csv`.
4. Re-zip, upload as a **new version of the same task**, run the Gate again.
5. Confirm Submit is enabled (not a harbor-bundle upload; Gate PASS; score at or
   above the floor; review.csv present and resolved; not already submitted at
   this score). Submit that version.

Exit: state shows "Queued in pipeline".

---

## Phase 9 — After submission

- Watch the state: Queued → Running → Accepted / Rejected · N findings /
  Pipeline error (re-run, not a rejection).
- On rejection: read findings, fix in the bundle, regenerate gold via the
  generator, oracle 1.0, battery if the prompt or inputs changed, refresh
  `qc_report.html`, update the affected `review.csv` rows to
  FIXED_AND_VERIFIED, upload as a new version, Gate, Submit.

---

## Hand-back traps checklist (tick before zipping)

- [ ] Oracle exactly 1.0 on the final package, repeated, after the manifest rename
- [ ] Four GLM rewards listed individually; 1–3 of them exactly 1.0
- [ ] No `evaluations/oracle/`, no `nop/`, no `platform/`, nothing loose under `evaluations/`
- [ ] `solvability/r1` is a model run, never the oracle
- [ ] Every rollout `result.json` carries `"model": "GLM-5.2"`, `overall_pass`, `final_answer`, `reward`, judge provenance
- [ ] `tests/manifest.json` exists and the loaders read it; no `tests/verifier.json` left behind
- [ ] `submission_format.md` allowed values include every reason code the gold uses
- [ ] `golden_trajectory.json` heredoc matches `solution/files/` byte for byte
- [ ] `review.csv` header exactly `review_check,status,review_notes,change_made,what_to_record`, twelve owned rows, no FAIL/TODO
- [ ] `qc_report.html` inside the zip at the task root
- [ ] Zip contains the task folder only

## Effort estimate

| Phase | Where | Time |
|---|---|---|
| 0 Setup | workstation | 0.5 h |
| 1 Read | here | 1 h (done in outline) |
| 2 Baseline oracle | workstation | 0.25 h |
| 3 Baseline battery | workstation | 1–2 h wall |
| 4 Hardening design + generator | here | 2–3 h |
| 5 Implement/measure, 2–3 rounds | here + workstation | 4–8 h wall |
| 6 Packaging | here | 1 h |
| 7 README + review.csv | here + form | 1 h |
| 8 Gate loop | workstation | 0.75 h |
