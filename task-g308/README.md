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
GLM-5.2 baseline battery: [N]/4, rewards [r1, r2, r3, r4] (harbor job glm-g308-baseline).

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

Result: 32 lines, 6 `RATE_MISMATCH`, 5 `UNMATCHED_TO_LEDGER`, 6 `DUPLICATE_LINE`,
15 compliant.

**Grading rebuilt.** The findings sheet is keyed by `line_id` and graded with one
`table_equals` check: every flagged line's cells plus a `row_set` lock, so listing a
compliant line, missing a flagged one or duplicating an id all fail. The memo is graded on
values only: it must mention every flagged deal id, DEAL-07 and `EXC-VP-02`, in any
wording and any case. `results.json` is a closed five-key object. Scoring is the core-gated
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
Ten shortcuts (trusting the partner type, flagging DEAL-07, applying a pending or
out-of-window override, case-sensitive joins on either file, gross instead of net revenue,
a reversal read as a failure, wrong precedence, flagging house lines for missing ledger
postings) were replayed against the verifier and each scores 0.0.

## Scoring shape

All checks are core, so a run scores exactly 1.0 or 0.0; the difficulty signal is the pass
count.

**Final battery:** [to be filled from harbor job glm-g308-r1].

## QC flags left as-is

- R3 stability evidence: Turing runs stability; no `stability/` folder is shipped.
