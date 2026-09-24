# June 2026 commission reconciliation — 138 consolidated lines

138 lines from four partner reports checked against COMM-POL-6 on the run date 30 June 2026. 105 lines are compliant; 33 carry a finding (10 duplicate, 9 unmatched to the ledger, 14 rate mismatches). One finding per line under R5 precedence.

## Findings

| Line | Deal | Source | Finding | Why |
|---|---|---|---|---|
| L-002 | DEAL-002 | PartnerA | RATE_MISMATCH | reported 4%; NetSuite bills the deal to CUST-17, a new customer per the master (partner said renewal), standard 8% (R1/R4) |
| L-003 | DEAL-003 | PartnerB | RATE_MISMATCH | reported 6%; master makes it new (partner said new), standard 8% (R1/R4) |
| L-004 | DEAL-004 | PartnerB | RATE_MISMATCH | reported 8%; master makes it renewal (partner said new), standard 4% (R1/R4) |
| L-006 | DEAL-006 | PartnerA | DUPLICATE_LINE | DEAL-006 is claimed on more than one line (R3) |
| L-007 | DEAL-006 | PartnerC | DUPLICATE_LINE | DEAL-006 is claimed on more than one line (R3) |
| L-009 | DEAL-008 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 4% but net June ledger revenue is 0.00 against 22,000.00 (R2) |
| L-010 | DEAL-009 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 8% but net June ledger revenue is 0.00 against 48,000.00 (R2) |
| L-013 | DEAL-012 | PartnerC | UNMATCHED_TO_LEDGER | commissionable at 8% but net June ledger revenue is 29,800.00 against 31,000.00 (R2) |
| L-014 | DEAL-013 | PartnerD | RATE_MISMATCH | reported 4.0%; override EXC-VP-07 approves 6% (R1/R4) |
| L-015 | DEAL-014 | PartnerA | DUPLICATE_LINE | DEAL-014 is claimed on more than one line (R3) |
| L-016 | deal-014 | PartnerD | DUPLICATE_LINE | deal-014 is claimed on more than one line (R3) |
| L-017 | DEAL-015 | PartnerB | RATE_MISMATCH | reported 5%; master makes it renewal (partner said renewal), standard 4% (R1/R4) |
| L-018 | DEAL-016 | PartnerC | RATE_MISMATCH | reported 4%; master makes it new (partner said renewal), standard 8% (R1/R4) |
| L-019 | DEAL-017 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 2% but net June ledger revenue is 0.00 against 9,000.00 (R2) |
| L-023 | DEAL-021 | PartnerD | UNMATCHED_TO_LEDGER | commissionable at 4% but net June ledger revenue is 0.00 against 19,500.00 (R2) |
| L-024 | DEAL-022 | PartnerA | UNMATCHED_TO_LEDGER | commissionable at 8% but net June ledger revenue is 104,000.00 against 52,000.00 (R2) |
| L-025 | DEAL-023 | PartnerB | RATE_MISMATCH | reported 4%; master makes it house (partner said house), standard 0% (R1/R4) |
| L-027 | DEAL-025 | PartnerD | DUPLICATE_LINE | DEAL-025 is claimed on more than one line (R3) |
| L-028 | DEAL-025 | PartnerD | DUPLICATE_LINE | DEAL-025 is claimed on more than one line (R3) |
| L-030 | DEAL-027 | PartnerB | RATE_MISMATCH | reported 4%; NetSuite bills the deal to CUST-18, a new customer per the master (partner said renewal), standard 8% - the posting to the partner's customer was reversed as a wrong entity and re-posted (R1/R4) |
| L-031 | DEAL-028 | PartnerC | RATE_MISMATCH | reported 6%; override EXC-VP-06 approves 5% (R1/R4) |
| L-044 | DEAL-040 | PartnerB | RATE_MISMATCH | reported 6%; master makes it renewal (partner said renewal), standard 4% (R1/R4) |
| L-051 | DEAL-047 | PartnerD | RATE_MISMATCH | reported 8.0%; master makes it renewal (partner said new), standard 4% (R1/R4) |
| L-059 | DEAL-055 | PartnerB | UNMATCHED_TO_LEDGER | commissionable at 4% but net June ledger revenue is 0.00 against 19,000.00 (R2) |
| L-067 | DEAL-063 | PartnerC | UNMATCHED_TO_LEDGER | commissionable at 4% but net June ledger revenue is 0.00 against 53,500.00 (R2) |
| L-082 | DEAL-078 | PartnerB | UNMATCHED_TO_LEDGER | commissionable at 4% but net June ledger revenue is 83,905.00 against 86,500.00 (R2) |
| L-100 | DEAL-096 | PartnerD | RATE_MISMATCH | reported 8.0%; NetSuite bills the deal to CUST-25, a renewal customer per the master (partner said new), standard 4% - the posting to the partner's customer was reversed as a wrong entity and re-posted (R1/R4) |
| L-112 | DEAL-108 | PartnerA | RATE_MISMATCH | reported 5%; master makes it renewal (partner said renewal), standard 4% (R1/R4) |
| L-123 | DEAL-119 | PartnerC | RATE_MISMATCH | reported 4%; master makes it house (partner said house), standard 0% (R1/R4) |
| L-125 | DEAL-121 | PartnerB | DUPLICATE_LINE | DEAL-121 is claimed on more than one line (R3) |
| L-126 | DEAL-121 | PartnerA | DUPLICATE_LINE | DEAL-121 is claimed on more than one line (R3) |
| L-133 | DEAL-128 | PartnerD | DUPLICATE_LINE | DEAL-128 is claimed on more than one line (R3) |
| L-134 | DEAL-128 | PartnerA | DUPLICATE_LINE | DEAL-128 is claimed on more than one line (R3) |

## Lines that look wrong but are compliant

- **L-021** appears twice in `commission_lines.csv` as an identical row; `line_id` is the list's key, so it is one line, counted once and not a duplicate claim.
- **L-109** appears twice in `commission_lines.csv` as an identical row; `line_id` is the list's key, so it is one line, counted once and not a duplicate claim.
- **L-005 DEAL-005 (PartnerC)** — a house line at 0% is not commissionable, so the absence of a June posting is not a finding.
- **L-008 DEAL-007 (PartnerB)** — reported 6% against a standard 4% for a renewal line, but override EXC-VP-02 (active, in force on the run date) approves 6.0%.
- **L-011 DEAL-010 (PartnerA)** — the net June postings total 27,400.00 against revenue 27,500.00, inside the 1% tolerance.
- **L-012 DEAL-011 (PartnerB)** — a house line at 0% is not commissionable, so the absence of a June posting is not a finding.
- **L-022 DEAL-020 (PartnerC)** — the extract repeats posting P-1019; it is one posting under R6, so net June revenue is 47,000.00, which matches.
- **L-026 DEAL-024 (PartnerC)** — the partner attributes the deal to CUST-12 but NetSuite bills it to CUST-14; the new rate follows the ledger's customer and the reported 8% is right.
- **L-029 DEAL-026 (PartnerA)** — the ledger carries a reversal (P-1031) but the net June revenue is 41,000.00, which matches.
- **L-029 DEAL-026 (PartnerA)** — posting P-1031 (2026-07-02) falls outside June and is left out of the June net under R2.
- **L-033 DEAL-030 (PartnerA)** — DEAL-030 is claimed by PartnerA and PartnerB, but the co-sell register carries an active 60/40 split naming exactly those partners, so the lines are not duplicates and this one matches its share of the 12,500.00 net.
- **L-034 DEAL-030 (PartnerB)** — DEAL-030 is claimed by PartnerA and PartnerB, but the co-sell register carries an active 60/40 split naming exactly those partners, so the lines are not duplicates and this one matches its share of the 12,500.00 net.
- **L-035 DEAL-031 (PartnerC)** — the net June postings total 19,800.00 against revenue 20,000.00, inside the 1% tolerance.
- **L-040 DEAL-036 (PartnerC)** — the ledger carries a reversal (P-1039) but the net June revenue is 95,000.00, which matches.
- **L-040 DEAL-036 (PartnerC)** — posting P-1039 (2026-07-07) falls outside June and is left out of the June net under R2.
- **L-055 DEAL-051 (PartnerD)** — the ledger carries a reversal (P-1056) but the net June revenue is 8,000.00, which matches.
- **L-070 DEAL-066 (PartnerB)** — the partner attributes the deal to CUST-24 but NetSuite bills it to CUST-31; the new rate follows the ledger's customer and the reported 8% is right.
- **L-075 DEAL-071 (PartnerA)** — the net June postings total 101,885.00 against revenue 102,500.00, inside the 1% tolerance.
- **L-077 DEAL-073 (PartnerC)** — the ledger carries a reversal (P-1078) but the net June revenue is 93,500.00, which matches.
- **L-077 DEAL-073 (PartnerC)** — posting P-1078 (2026-07-02) falls outside June and is left out of the June net under R2.
- **L-094 DEAL-090 (PartnerD)** — the extract repeats posting P-1096; it is one posting under R6, so net June revenue is 79,500.00, which matches.
- **L-118 DEAL-114 (PartnerA)** — reported 6% against a standard 4% for a renewal line, but override EXC-VP-09 (active, in force on the run date) approves 6%.
- **L-137 DEAL-131 (PartnerA)** — DEAL-131 is claimed by PartnerA and PartnerB, but the co-sell register carries an active 50/50 split naming exactly those partners, so the lines are not duplicates and this one matches its share of the 11,500.00 net.
- **L-138 DEAL-131 (PartnerB)** — DEAL-131 is claimed by PartnerA and PartnerB, but the co-sell register carries an active 50/50 split naming exactly those partners, so the lines are not duplicates and this one matches its share of the 11,500.00 net.
