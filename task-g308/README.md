# Change summary — commission report reconciliation audit

## What the task asks

Finance has consolidated four partner commission reports into one line list for the June
2026 run. Each line must be checked against the recognition policy COMM-POL-6, the customer
master, the June NetSuite revenue extract and the VP exceptions register, and the wrong
ones reported: a rate the policy does not pay, commission claimed on revenue the ledger
does not carry for June, and deals claimed more than once. Deliverables: a findings sheet
keyed by line, a memo, and the headline counts.

## From the mined baseline to this version

**Baseline (as mined).** 8 lines, one exceptions row, a `netsuite_matched` yes/no flag on
each line, the partner's own `customer_type` taken as fact. One trap (the DEAL-07 VP
override). Every rule was a one-column lookup. Findings were graded by per-row regexes with
no population lock (flagging every line except DEAL-07 passed the sheet checks), the memo
by wording regexes (`standard…rate`, `override…approv`, `ledger…match`), and the package
shipped no `golden_trajectory.json`, no format document and no `manifest.json`.
GLM-5.2 baseline battery: 0/4 (harbor job glm-g308-baseline), but not from difficulty. All four
runs failed only `result_compliant_lines`: the mined expected value 5 contradicts the mined
sheet, which flags 4 of 8 lines, so GLM's answer of 4 was arguably right. The mined memo
also failed a wording regex in one run. The mined package was unfair rather than hard.

**Hardened (current).** The rules are unchanged in kind and stay explicit in
`commission_policy.md`; what changed is that each of them now has to be *computed from a
second source* rather than read off the line, and the data has the shapes real exports have.

1. **End-user type is derived, not trusted (R1).** `customer_master.csv` gives
   `account_class` and `first_invoice_date`; a customer is `new` only if first invoiced on
   or after 1 July 2025. Partners mis-tag two lines (L-04 claims `new` for a customer first
   invoiced 2025-06-30; L-18 claims `renewal` for one first invoiced 2025-12-01). Trusting
   the partner's tag passes both and misses two `RATE_MISMATCH`.
2. **Ledger match is a join, not a flag (R2).** `netsuite_revenue_june.csv` is a real
   extract: amounts printed as `$50,000.00`, reversals as `-$48,000.00`, one deal
   reference in lower case, a July posting and a May posting for June lines, a deal paid in
   two postings, a reversal with a re-posting. Matched means *net June postings within 1%*.
   Any June posting → matched misses L-10 (reversed to zero); gross instead of net misses
   L-10 too; treating a reversal as a failure flags L-30 wrongly; a case-sensitive join
   flags L-21 wrongly; the 3.9%-off L-13 is unmatched while the 0.4%-off L-11 is fine.
3. **Overrides have status and a window (R4).** Six register rows: one expired by status,
   one `active` but out of window (L-17 is a mismatch after all), one `pending` (L-14 stays
   compliant at the standard rate), one for a house account that makes it commissionable
   and therefore ledger-bound (L-19 is unmatched), one where the reported rate disagrees
   with the approved rate (L-31). The classic DEAL-07 false positive is kept.
4. **Duplicates across and within reports, case-insensitive (R3, R6).** DEAL-06 in two
   reports, DEAL-25 twice in one report, DEAL-14 once as `deal-14`.
5. **One finding per line under precedence (R5).** L-13 fails both R2 and R1 and is
   reported as `UNMATCHED_TO_LEDGER`; L-15/L-16 fail R3 and R1 and are `DUPLICATE_LINE`.
   The counts in `results.json` follow the same rule, so a two-codes-per-line answer
   breaks both the sheet and the counts.
6. **House lines at 0% are not commissionable**, so their missing ledger postings are not
   findings (L-05, L-12), while a house line reported at 4% is a rate mismatch (L-25).

Round 1 result: 32 lines, 6 `RATE_MISMATCH`, 5 `UNMATCHED_TO_LEDGER`, 6 `DUPLICATE_LINE`,
15 compliant. GLM-5.2 passed 8/8 locally (harbor job the round-1 GLM job): every explicit rule,
however derived, was coded correctly.

**Round 2 (current).** The gold answer is unchanged; the data stops matching the assumptions
a rule-to-code script makes, and R6 says in one sentence how such values compare. Each is
silent: no error, a different answer.

7. **A repeated posting row.** The NetSuite extract lists P-1019 twice, identically.
   `posting_id` identifies a posting; a script that sums rows doubles DEAL-20's June revenue
   and turns compliant L-22 into `UNMATCHED_TO_LEDGER`.
8. **A July reversal of a June invoice.** P-1031 (2026-07-02) reverses DEAL-26's June
   posting. Only June postings count, so L-29 stays matched; a script that nets reversals
   regardless of date flags it.
9. **Numbers written differently.** PartnerD writes rates as `4.0`, `8.0`, `2.0`; the
   register approves `6.0` for DEAL-07. A string comparison against `4`, `8`, `6` flags
   every PartnerD line and the protected DEAL-07.
10. **Case in coded values.** `deal-28` in the register, `cust-09` on a line, `House` in the
    master. Exact-string joins drop the DEAL-28 override (harmless there), fail the L-24
    master lookup and make CUST-11 a renewal, which flags L-12 at 0%.

Round 2 result: unchanged gold. GLM-5.2 passed 7/8 locally (harbor job the round-2 GLM job): the
policy's R6 tells a careful reader how values compare, and GLM codes what the policy says.

**Round 3 (current).** Two inferences that are explicit as principles but not as steps:

11. **The ledger's customer governs.** The policy already said the master and the ledger win
    over a partner report on a fact; R1 now says the customer of a line is the one NetSuite
    bills. Two deals are billed to a different customer than the partner wrote: DEAL-02 to
    the new customer CUST-17 (L-02 reports the renewal rate and is a `RATE_MISMATCH`) and
    DEAL-24 to CUST-14 (same type, compliant). Reading the partner's customer misses L-02.
12. **Registered co-sells are not duplicates.** `co_sell_register.csv` lists joint deals.
    DEAL-30 is claimed by PartnerA (7,500) and PartnerB (5,000) under an active 60/40 split
    that names exactly those partners: not duplicates, and each line matches its share of
    the 12,500 net. DEAL-06's split is `proposed` and DEAL-25's names PartnerB where both
    lines are PartnerD, so both stay `DUPLICATE_LINE`. Ignoring the register flags L-33/L-34;
    honouring a failing entry clears real duplicates; matching a split line against the full
    net flags it unmatched.

Round 3 result: 34 lines, 7 / 5 / 6 / 16. GLM-5.2 passed 8/8 locally (harbor job
the round-3 GLM job). Across every battery on both tasks, no failure has ever come from a rule the
policy states; failures come from anomalies nothing points at. Round 2's R6 had listed its
own traps as a checklist, and the runs ticked them off.

**Round 4 (current).** The policy now states principles only (R6 is two sentences; R2 no
longer enumerates reversals or out-of-month postings), and the data carries anomalies whose
handling follows from the ordinary meaning of a key or a rule:

13. **Two kinds of repeated posting.** P-1019 appears twice with the same `posting_id`
    (an export repeat: one posting, DEAL-20 matches). DEAL-22 has two postings with
    different ids for the same amount on the same day (a genuine double booking: net is
    twice the line, L-24 is `UNMATCHED_TO_LEDGER`). Summing every row breaks L-22;
    deduplicating on content breaks L-24; only deduplicating on the key gets both.
14. **Two register rows for one deal.** DEAL-13 has an active override (EXC-VP-07, listed
    first) and a pending one (EXC-VP-05). R4 applies to the row that is active and in
    window; taking the first row, or a last-row-wins dictionary, misses that L-14 reports
    4% against an approved 6%.
15. **The tolerance boundary.** L-35 reports 20,000 against 19,800 in the ledger, exactly
    1%. R2 says at most 1%, so it matches; a strict comparison flags it.

Result: 35 lines, 8 `RATE_MISMATCH`, 6 `UNMATCHED_TO_LEDGER`, 6 `DUPLICATE_LINE`,
15 compliant.

**Grading rebuilt.** The findings sheet is keyed by `line_id` and graded with one
`table_equals` check: every flagged line's cells plus a `row_set` lock, so listing a
compliant line, missing a flagged one or duplicating an id all fail. The memo is graded by five
plain substring checks, no regex on prose: it must name DEAL-07 and quote `EXC-VP-02`, and
it must name each of the three finding codes it explains. Wording, order and layout are free. `results.json` is a closed five-key object. Scoring is the core-gated
`tests/score.py` with the positive/incomplete/corrupted/extra-key lanes in
`tests/test_outputs.py`. `input/submission_format.md` carries the contract.

**Also added.** `solution/compute_gold.py` derives the three gold files, the golden
trajectory and both verifier files from the inputs in one run; `solution/solve.sh` emits
the ATIF oracle trajectory; `tests/manifest.json` mirrors `tests/verifier.json`; the base
image is pinned to its digest.

## Why it is hard

No column answers a rule on its own. The rate test needs the master and the register with
its status and window; the ledger test needs a case-insensitive join, currency parsing, a
June date filter and a net sum with a tolerance; the duplicate test needs a case-insensitive
count across the whole list; and every line then takes exactly one code by precedence.
Twenty-five shortcuts (summing a repeated export row, deduplicating postings on content, taking the first or last register row, a strict tolerance, trusting the partner type or the partner's customer, ignoring or over-honouring the co-sell register, matching a split line against the full net, flagging DEAL-07, applying a pending or
out-of-window override, case-sensitive joins on either file, gross instead of net revenue,
a reversal read as a failure, wrong precedence, flagging house lines for missing ledger
postings, double-counting a repeated posting row, netting a July reversal into June, comparing
rates as strings, case-sensitive matching of a register deal, a line's customer or an account
class) were replayed against the verifier and each scores 0.0.

## Scoring shape

All checks are core, so a run scores exactly 1.0 or 0.0; the difficulty signal is the pass
count.

**Round-4 battery (round-4 GLM job, terminus-2, GLM-5.2, 8 runs at -k 8): 3 of 8 passed;
rewards in start order 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0.** Selection is mechanical:
the earliest passing run is held out as the solvability evidence, and the next four runs by
start time are the difficulty rollouts, which score 2 of 4:

| rollout | harbor trial | reward | outcome |
|---|---|---|---|
| difficulty/r1 | task-g308__5rgWFcx | 0.0 | MODEL: summed every ledger row, doubled DEAL-20's revenue and flagged compliant L-22 `UNMATCHED_TO_LEDGER` (count 7, compliant 14); every other cell correct |
| difficulty/r2 | task-g308__R9iyPo4 | 1.0 | keyed the ledger on `posting_id`, counted P-1019 once, kept both DEAL-22 postings |
| difficulty/r3 | task-g308__bMp9PbM | 1.0 | as above |
| difficulty/r4 | task-g308__kxNUbJJ | 0.0 | MODEL: same as r1 |

`evaluations/solvability/r1` is the held-out run task-g308__AxAgMA6 (GLM-5.2, reward 1.0, not
an oracle and not one of the four difficulty rollouts). The three unshipped runs (eLmrW6p,
mCYs8hN, YaVSACn, all 0.0) fail for the identical reason. All eight handled the derived
customer type, the ledger-governed customer, the override statuses and windows including the
second DEAL-13 row, the co-sell register, the genuine DEAL-22 double booking and the 1%
boundary. The one discriminating behaviour is whether the run treats the ledger's key as a
key before summing. Zero exceptions.

Oracle on this package: 1.0 after every round, re-run after the round-5 grader and policy changes.

**Round-5 battery:** [to be filled from the round-5 GLM job].

**Evidence format note.** This harbor build writes `verifier/reward.txt` and
`verifier/score.json`; the bundle's `verifier/reward.json` and `verifier/verifier_summary.json`
were derived from those two files by `tools/annotate_rollout.py` (a format conversion, no new
facts), which also added `model`, `overall_pass`, `final_answer`, `reward` and `judge` to each
`result.json`.

**Platform battery on round 4 (first QC run): oracle 1.0, GLM-5.2 2 of 4.** The platform's
two failures read the 1% tolerance against the ledger figure instead of the line's revenue
(L-35) and, in one run, summed the repeated P-1019 row (L-22). Its Harbor Check raised six
findings, addressed in round 5:

- **Ambiguous rule (confirmed).** R2 now says "at most 1% of the line's `revenue_usd`", and
  R6 states the ledger's key: rows sharing a `posting_id` are one posting, postings with
  different ids are different postings. The repeated P-1019 row also says in its memo column
  that it is repeated by export page overlap. The gold is unchanged.
- **Memo grading (confirmed, four findings with one root cause).** The memo contract in
  `submission_format.md` is now three enumerated items, and the grader holds one plain
  substring check per fact those items name: every flagged `deal_id` (17), the protected
  deal and its exception code (2), and the posting or deal ids behind the compliant lines
  whose ledger evidence looks wrong (6: P-1019, P-1026, P-1027, P-1031, DEAL-10, DEAL-31).
  No finding-code tokens are required in prose, no regex is used, and the reviewer's
  five-token stub scores 0.0 while a plain-language memo carrying the facts scores 1.0.
  Item 3 is new reasoning work: the model must recognise which compliant lines look wrong.
- **Golden access (disputed).** The finding says the agent can read `tests/verifier.json`.
  The Dockerfile copies `input/` only, and harbor uploads `tests/` for the verifier phase
  after the agent has finished; the accepted b39 bundle ships its expected rows inline the
  same way. Marked as a false positive with that note.

**PreQC round 1 fixes.** The first Gate run flagged the memo's lookahead regex as
reward-hackable (replaced by substring checks, widened to one per fact in round 5), the solvability run being a
byte copy of a difficulty run (now an independent held-out run), and job names of the form
job-name suffixes in the review being misread as rollout scores (reworded).

## QC flags left as-is

- R3 stability evidence: Turing runs stability; no `stability/` folder is shipped.
