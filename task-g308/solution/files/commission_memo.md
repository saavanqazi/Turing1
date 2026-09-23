# June 2026 commission reconciliation — 35 consolidated lines

35 lines from four partner reports checked against COMM-POL-6 on the run date 30 June 2026. 14 lines are compliant; 21 carry a finding (6 duplicate, 6 unmatched to the ledger, 9 rate mismatches). One finding per line under R5 precedence.

## Findings

| Line | Deal | Source | Finding | Why |
|---|---|---|---|---|
| L-02 | DEAL-02 | PartnerA | RATE_MISMATCH | reported 4%; NetSuite bills the deal to CUST-17, a new customer per the master (partner said renewal), standard 8% (R1/R4) |
| L-03 | DEAL-03 | PartnerB | RATE_MISMATCH | reported 6%; master makes it new (partner said new), standard 8% (R1/R4) |
| L-04 | DEAL-04 | PartnerB | RATE_MISMATCH | reported 8%; master makes it renewal (partner said new), standard 4% (R1/R4) |
| L-06 | DEAL-06 | PartnerA | DUPLICATE_LINE | DEAL-06 is claimed on more than one line (R3) |
| L-07 | DEAL-06 | PartnerC | DUPLICATE_LINE | DEAL-06 is claimed on more than one line (R3) |
| L-09 | DEAL-08 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 4% but net June ledger revenue is 0.00 against 22,000.00 (R2) |
| L-10 | DEAL-09 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 8% but net June ledger revenue is 0.00 against 48,000.00 (R2) |
| L-13 | DEAL-12 | PartnerC | UNMATCHED_TO_LEDGER | commissionable at 8% but net June ledger revenue is 29,800.00 against 31,000.00 (R2) |
| L-14 | DEAL-13 | PartnerD | RATE_MISMATCH | reported 4.0%; override EXC-VP-07 approves 6% (R1/R4) |
| L-15 | DEAL-14 | PartnerA | DUPLICATE_LINE | DEAL-14 is claimed on more than one line (R3) |
| L-16 | deal-14 | PartnerD | DUPLICATE_LINE | deal-14 is claimed on more than one line (R3) |
| L-17 | DEAL-15 | PartnerB | RATE_MISMATCH | reported 5%; master makes it renewal (partner said renewal), standard 4% (R1/R4) |
| L-18 | DEAL-16 | PartnerC | RATE_MISMATCH | reported 4%; master makes it new (partner said renewal), standard 8% (R1/R4) |
| L-19 | DEAL-17 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 2% but net June ledger revenue is 0.00 against 9,000.00 (R2) |
| L-23 | DEAL-21 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 4% but net June ledger revenue is 0.00 against 19,500.00 (R2) |
| L-24 | DEAL-22 | PartnerA | UNMATCHED_TO_LEDGER | commissionable at 8% but net June ledger revenue is 104,000.00 against 52,000.00 (R2) |
| L-25 | DEAL-23 | PartnerB | RATE_MISMATCH | reported 4%; master makes it house (partner said house), standard 0% (R1/R4) |
| L-27 | DEAL-25 | PartnerD | DUPLICATE_LINE | DEAL-25 is claimed on more than one line (R3) |
| L-28 | DEAL-25 | PartnerD | DUPLICATE_LINE | DEAL-25 is claimed on more than one line (R3) |
| L-30 | DEAL-27 | PartnerB | RATE_MISMATCH | reported 4%; NetSuite bills the deal to CUST-18, a new customer per the master (partner said renewal), standard 8% - the posting to the partner's customer was reversed as a wrong entity and re-posted (R1/R4) |
| L-31 | DEAL-28 | PartnerC | RATE_MISMATCH | reported 6%; override EXC-VP-06 approves 5% (R1/R4) |

## Lines that look wrong but are compliant

- **L-21** appears twice in `commission_lines.csv` as an identical row; `line_id` is the list's key, so it is one line, counted once and not a duplicate claim.
- **L-05 DEAL-05 (PartnerC)** — a house line at 0% is not commissionable, so the absence of a June ledger posting is not a finding.
- **L-08 DEAL-07 (PartnerB)** — reported 6% against a standard 4% for a renewal line, but override EXC-VP-02 (active, in force on the run date) approves 6.0%.
- **L-11 DEAL-10 (PartnerA)** — the ledger's net June postings for DEAL-10 total 27,400.00 against revenue 27,500.00, inside the 1% match tolerance.
- **L-12 DEAL-11 (PartnerB)** — a house line at 0% is not commissionable, so the absence of a June ledger posting is not a finding.
- **L-22 DEAL-20 (PartnerC)** — the extract repeats posting P-1019 for DEAL-20; it is one posting, so net June revenue is 47,000.00, which matches.
- **L-26 DEAL-24 (PartnerC)** — the partner attributes the deal to CUST-12 but NetSuite bills it to CUST-14; both are new customers so the reported 8% stands.
- **L-29 DEAL-26 (PartnerA)** — the ledger carries a reversal for DEAL-26 (P-1031) but the net June revenue is still 41,000.00, which matches.
- **L-33 DEAL-30 (PartnerA)** — DEAL-30 is claimed by PartnerA and PartnerB, but the co-sell register carries an active 60/40 split naming exactly those partners, so the two lines are not duplicates and each matches its share of the 12,500.00 net.
- **L-34 DEAL-30 (PartnerB)** — DEAL-30 is claimed by PartnerA and PartnerB, but the co-sell register carries an active 60/40 split naming exactly those partners, so the two lines are not duplicates and each matches its share of the 12,500.00 net.
- **L-35 DEAL-31 (PartnerC)** — the ledger's net June postings for DEAL-31 total 19,800.00 against revenue 20,000.00, inside the 1% match tolerance.
