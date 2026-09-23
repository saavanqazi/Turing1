# Submission format

Deliver exactly these files, in your working directory:

- `commission_findings.csv` — one row per line that carries a finding.
- `commission_memo.md` — the reconciliation memo.
- `results.json` — a JSON object; see below.

## `commission_findings.csv`

Header, exactly: `line_id,deal_id,source_report,finding_code`
One row per flagged line, keyed by `line_id` (the consolidated list's key) as
`commission_lines.csv` writes it, in any order; compliant lines are not listed. `deal_id` and `source_report` are copied from the
line. `finding_code` is the single finding the policy's precedence rule assigns to the
line and takes exactly one of: `DUPLICATE_LINE`, `UNMATCHED_TO_LEDGER`, `RATE_MISMATCH`.

Example (placeholder values):

```
line_id,deal_id,source_report,finding_code
L-00,DEAL-00,PartnerX,RATE_MISMATCH
```

## `commission_memo.md`

Markdown, wording free. It must:

1. name every flagged line by its `deal_id`, with the rule behind the finding;
2. name the line that is reported off the standard mapping yet is compliant, quoting the
   exception code that makes it so;
3. name every commissionable line that is compliant although its June ledger evidence
   looks wrong: a repeated export row, a reversal (with or without a re-posting), or a net
   that differs from the line's `revenue_usd` yet stays within the tolerance. For the first
   two kinds quote the `posting_id` of every posting involved (the repeated row, the
   reversal, the re-posting); for the third name the line's `deal_id`.

Other lines may be discussed too. Nothing else about the memo's form is graded.

## `results.json`

A JSON object with exactly these keys and nothing else:

- `total_lines` — number of lines (`line_id`s) in the consolidated list
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
