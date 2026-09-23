# Task

The June commission run is with me for sign-off and I do not trust the partner reports. Finance has consolidated the four partner reports into one line list; I have also saved the customer master, the June NetSuite revenue extract, the VP exceptions register and the commission recognition policy the run has to follow. Work through every line and tell me which ones are wrong: a rate that is not what the policy pays, commission claimed on revenue the ledger does not carry for June, and any deal that has been claimed more than once. Give me the findings sheet, a memo that explains each finding and also calls out the lines that look wrong but are actually compliant and why, and the headline counts. File layout is in `input/submission_format.md`.

---
Save your deliverables into your current working directory using exactly these filenames:
    - `commission_findings.csv` — One row per flagged commission line
    - `commission_memo.md` — Markdown reconciliation memo
    - `results.json` — a JSON object with the keys `total_lines`, `rate_mismatch_count`, `unmatched_to_ledger_count`, `duplicate_line_count`, `compliant_lines`
- The exact headers, key sets, allowed values and worked examples are specified in `input/submission_format.md` — follow it precisely.
- Writing those files is the required deliverable and must be your final action; confirm each one exists before you answer.

---

## Working environment

- Your current working directory is `/app`, and it is writable.
- The read-only attachments referred to as `input/` are at `/app/input`.
- Write every deliverable into `/app`, at the exact filenames listed above.
