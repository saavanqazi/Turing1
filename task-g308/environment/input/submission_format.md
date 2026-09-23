# Submission format

Deliver exactly these files, in your working directory:

- `commission_findings.csv` — one row per line that carries a finding.
- `commission_memo.md` — the reconciliation memo.
- `results.json` — a JSON object; see below.

## `commission_findings.csv`

Header, exactly: `line_id,deal_id,source_report,finding_code`
One row per flagged line, keyed by `line_id` as `commission_lines.csv` writes it, in any
order; compliant lines are not listed. `deal_id` and `source_report` are copied from the
line. `finding_code` is the single finding the policy's precedence rule assigns to the
line and takes exactly one of: `DUPLICATE_LINE`, `UNMATCHED_TO_LEDGER`, `RATE_MISMATCH`.

Example (placeholder values):

```
line_id,deal_id,source_report,finding_code
L-00,DEAL-00,PartnerX,RATE_MISMATCH
```

## `commission_memo.md`

Markdown. It must name every flagged line by its `deal_id` with the rule behind the
finding, and separately name the line that is reported off the standard mapping yet is
compliant, quoting the exception code that makes it so. Other lines that look wrong but
are compliant may be explained too. Wording is free.

## `results.json`

A JSON object with exactly these keys and nothing else:

- `total_lines` — number of lines in the consolidated list
- `rate_mismatch_count` — number of lines whose finding is `RATE_MISMATCH`
- `unmatched_to_ledger_count` — number of lines whose finding is `UNMATCHED_TO_LEDGER`
- `duplicate_line_count` — number of lines whose finding is `DUPLICATE_LINE`
- `compliant_lines` — number of lines with no finding

Shape example (placeholder values):

```json
{
  "total_lines": 0,
  "rate_mismatch_count": 0,
  "unmatched_to_ledger_count": 0,
  "duplicate_line_count": 0,
  "compliant_lines": 0
}
```
