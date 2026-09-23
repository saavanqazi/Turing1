# Commission recognition policy (COMM-POL-6)

Binding for the June 2026 commission run, whose run date is 30 June 2026, once the partner
reports are consolidated into one line list (`commission_lines.csv`). Where a partner report
and this policy disagree, this policy wins. Where a partner report and the customer master
or the NetSuite ledger disagree on a fact, the master and the ledger win.

## R1 — End-user type and standard rate

The customer of a line is the customer NetSuite records against the deal's June postings
(`customer_id` in `netsuite_revenue_june.csv`); the partner's `customer_id` is used only
where the ledger carries no June posting for the deal. The end-user type of a line is then
determined from `customer_master.csv` for that customer, not from the type the partner
wrote on its report:

- `house` if the customer's `account_class` is `house`;
- otherwise `new` if the customer's `first_invoice_date` is on or after 1 July 2025 (within
  the twelve months ending on the run date);
- otherwise `renewal`.

| end-user type | standard rate |
|---|---|
| new | 8% |
| renewal | 4% |
| house | 0% |

A line whose `reported_rate_pct` does not equal the rate the policy pays for that line (the
standard rate for its end-user type, or an approved rate under R4) is a `RATE_MISMATCH`.

## R2 — Ledger match

A line is **commissionable** when the rate the policy pays for it is above 0%. Every
commissionable line must be matched to June revenue in `netsuite_revenue_june.csv` before it
is paid. A line is matched when the ledger's **net June revenue** for its deal, the sum of
`amount_usd` over every posting for that deal whose `posting_date` falls in June 2026
(reversals are negative postings and count), is within 1% of the line's `revenue_usd`.
Postings dated outside June 2026 do not count. A commissionable line that is not matched is
`UNMATCHED_TO_LEDGER`. A line that is not commissionable needs no ledger match.

## R3 — Duplicate lines and registered co-sells

A deal may be claimed once in the consolidated list. A deal that appears on more than one
line, whether in different partner reports or twice in the same report, is a
`DUPLICATE_LINE` on every one of those lines, with one exception: a registered co-sell.
`co_sell_register.csv` lists deals sold jointly. The exception applies only when every
register row for the deal has `status = active`, the partners named in the register are
exactly the `source_report` values of the deal's lines (one line per named partner), and the
shares sum to 100. For such a deal the lines are not duplicates, and under R2 each line is
matched against its share of the deal's net June revenue (`share_pct` of the net) instead
of the full net. A register entry that fails any of these tests changes nothing.

## R4 — VP-approved rate overrides

`commission_exceptions.csv` lists rate overrides. An override applies to a deal only when
its `status` is `active` and the run date falls within `effective_from` to `effective_to`
inclusive. A register row that fails either test grants nothing, whatever it says. When an
override applies, the rate the policy pays for that deal is the `approved_rate_pct`
instead of the standard rate, and the line is commissionable if that rate is above 0%.
A line reported at an applicable approved rate is compliant even though it disagrees with
the standard mapping; flagging it is the commonest false positive in this audit.

## R5 — One finding per line

A line may fail more than one rule. Report the first that applies, in this order:
`DUPLICATE_LINE`, `UNMATCHED_TO_LEDGER`, `RATE_MISMATCH`. A line that fails none is
compliant.

## R6 — Identifiers and amounts as exported

Identifiers and coded values (deal, customer and posting identifiers, account classes,
statuses) are matched without regard to case. Rates and amounts are numbers however a
report prints them: `6`, `6.0` and `$6.00` denote the same value, and ledger amounts carry
the accounting system's currency symbol, thousands separators and a leading minus for
reversals. `posting_id` identifies a ledger posting.

## Finding codes

`RATE_MISMATCH`, `UNMATCHED_TO_LEDGER`, `DUPLICATE_LINE`.
