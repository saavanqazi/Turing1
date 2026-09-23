# June 2026 commission reconciliation — 32 consolidated lines

32 lines from four partner reports checked against COMM-POL-6 on the run date 30 June 2026. 15 lines are compliant; 17 carry a finding (6 duplicate, 5 unmatched to the ledger, 6 rate mismatches). One finding per line under R5 precedence.

## Findings

| Line | Deal | Source | Finding | Why |
|---|---|---|---|---|
| L-03 | DEAL-03 | PartnerB | RATE_MISMATCH | reported 6%; master makes it new (partner said new), standard 8% (R1/R4) |
| L-04 | DEAL-04 | PartnerB | RATE_MISMATCH | reported 8%; master makes it renewal (partner said new), standard 4% (R1/R4) |
| L-06 | DEAL-06 | PartnerA | DUPLICATE_LINE | DEAL-06 is claimed on more than one line (R3) |
| L-07 | DEAL-06 | PartnerC | DUPLICATE_LINE | DEAL-06 is claimed on more than one line (R3) |
| L-09 | DEAL-08 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 4% but net June ledger revenue is 0.00 against 22,000.00 (R2) |
| L-10 | DEAL-09 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 8% but net June ledger revenue is 0.00 against 48,000.00 (R2) |
| L-13 | DEAL-12 | PartnerC | UNMATCHED_TO_LEDGER | commissionable at 8% but net June ledger revenue is 29,800.00 against 31,000.00 (R2) |
| L-15 | DEAL-14 | PartnerA | DUPLICATE_LINE | DEAL-14 is claimed on more than one line (R3) |
| L-16 | deal-14 | PartnerD | DUPLICATE_LINE | deal-14 is claimed on more than one line (R3) |
| L-17 | DEAL-15 | PartnerB | RATE_MISMATCH | reported 5%; master makes it renewal (partner said renewal), standard 4% (R1/R4) |
| L-18 | DEAL-16 | PartnerC | RATE_MISMATCH | reported 4%; master makes it new (partner said renewal), standard 8% (R1/R4) |
| L-19 | DEAL-17 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 2% but net June ledger revenue is 0.00 against 9,000.00 (R2) |
| L-23 | DEAL-21 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 4% but net June ledger revenue is 0.00 against 19,500.00 (R2) |
| L-25 | DEAL-23 | PartnerB | RATE_MISMATCH | reported 4%; master makes it house (partner said house), standard 0% (R1/R4) |
| L-27 | DEAL-25 | PartnerD | DUPLICATE_LINE | DEAL-25 is claimed on more than one line (R3) |
| L-28 | DEAL-25 | PartnerD | DUPLICATE_LINE | DEAL-25 is claimed on more than one line (R3) |
| L-31 | DEAL-28 | PartnerC | RATE_MISMATCH | reported 6%; override EXC-VP-06 approves 5% (R1/R4) |

## Lines that look wrong but are compliant

- **L-02 DEAL-02 (PartnerA)** — register row EXC-VP-01 names this deal but is expired, so it grants nothing and the standard 4% applies, which is what was reported.
- **L-05 DEAL-05 (PartnerC)** — a house line at 0% is not commissionable, so the absence of a June ledger posting is not a finding.
- **L-08 DEAL-07 (PartnerB)** — reported 6% against a standard 4% for a renewal line, but override EXC-VP-02 (active, in force on the run date) approves 6%.
- **L-11 DEAL-10 (PartnerA)** — the ledger's net June postings for DEAL-10 total 27,400.00 against revenue 27,500.00, inside the 1% match tolerance.
- **L-12 DEAL-11 (PartnerB)** — a house line at 0% is not commissionable, so the absence of a June ledger posting is not a finding.
- **L-14 DEAL-13 (PartnerD)** — register row EXC-VP-05 names this deal but is pending, so it grants nothing and the standard 4% applies, which is what was reported.
- **L-30 DEAL-27 (PartnerB)** — the ledger carries a reversal for DEAL-27 but the re-posting brings net June revenue back to 28,000.00, which matches.
