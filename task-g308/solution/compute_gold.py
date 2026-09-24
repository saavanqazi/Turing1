#!/usr/bin/env python3
"""compute_gold.py — derive the gold deliverables for the commission reconciliation task.

Single source of truth. Reads environment/input/, applies commission_policy.md R1–R6 and
writes solution/files/{commission_findings.csv,commission_memo.md,results.json},
solution/golden_trajectory.json and tests/verifier.json + tests/manifest.json (identical).
Prints the derivation per line so the answer can be checked by hand.
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
INPUT = TASK / "environment" / "input"
FILES = TASK / "solution" / "files"
TESTS = TASK / "tests"

RUN_DATE = date(2026, 6, 30)
NEW_CUTOFF = date(2025, 7, 1)          # first invoice on/after this -> new (R1)
JUNE = (date(2026, 6, 1), date(2026, 6, 30))
STANDARD = {"new": Decimal("8"), "renewal": Decimal("4"), "house": Decimal("0")}
TOLERANCE = Decimal("0.01")            # 1% (R2)
PRECEDENCE = ["DUPLICATE_LINE", "UNMATCHED_TO_LEDGER", "RATE_MISMATCH"]  # R5


def rows(name):
    with (INPUT / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def money(text: str) -> Decimal:
    """'$50,000.00' / '-$48,000.00' / '($48,000.00)' -> Decimal (R6): the sign is read as the
    system printed it, a leading minus or accounting parentheses."""
    stripped = text.strip()
    neg = stripped.startswith("-") or (stripped.startswith("(") and stripped.endswith(")"))
    digits = stripped.replace("$", "").replace(",", "").replace("-", "").strip("() ")
    value = Decimal(digits)
    return -value if neg else value


def main() -> int:
    master = {r["customer_id"].strip().upper(): r for r in rows("customer_master.csv")}
    # line_id is the consolidated list's key: a row the export repeats is one line
    lines, seen_lines, repeated_lines = [], set(), []
    for ln in rows("commission_lines.csv"):
        if ln["line_id"].strip().upper() in seen_lines:
            repeated_lines.append(ln["line_id"])
            continue
        seen_lines.add(ln["line_id"].strip().upper())
        lines.append(ln)
    ledger = rows("netsuite_revenue_june.csv")
    exceptions = rows("commission_exceptions.csv")

    # R1: end-user type from the master
    def end_user_type(cust_id: str) -> str:
        m = master[cust_id.strip().upper()]
        if m["account_class"].strip().lower() == "house":
            return "house"
        return "new" if date.fromisoformat(m["first_invoice_date"]) >= NEW_CUTOFF else "renewal"

    # R4: applicable overrides
    approved: dict[str, tuple[str, Decimal]] = {}
    for e in exceptions:
        if e["status"].strip().lower() != "active":
            continue
        if not (date.fromisoformat(e["effective_from"]) <= RUN_DATE <= date.fromisoformat(e["effective_to"])):
            continue
        approved[e["deal_id"].strip().upper()] = (e["exception_code"], Decimal(e["approved_rate_pct"]))

    # R2: net June revenue per deal (case-insensitive); posting_id identifies a posting, so a
    # repeated export row counts once. R1: the ledger's customer for the deal governs.
    net: dict[str, Decimal] = {}
    ledger_customer: dict[str, str] = {}
    june_postings: dict[str, list[dict]] = {}
    seen_postings: set[str] = set()
    repeated_ids: dict[str, list[str]] = {}
    evidence_values: list[str] = []
    for p in ledger:
        if p["posting_id"].strip().upper() in seen_postings:
            repeated_ids.setdefault(p["deal_ref"].strip().upper(), []).append(p["posting_id"])
            continue
        seen_postings.add(p["posting_id"].strip().upper())
        d = date.fromisoformat(p["posting_date"])
        if JUNE[0] <= d <= JUNE[1]:
            key = p["deal_ref"].strip().upper()
            net[key] = net.get(key, Decimal(0)) + money(p["amount_usd"])
            june_postings.setdefault(key, []).append(p)

    # R1: the ledger's customer for a deal, disregarding a posting and the reversal that cancels
    # it (a later posting of the opposite amount). Whatever remains names the customer.
    for key, ps in june_postings.items():
        cancelled: set[str] = set()
        for i, later in enumerate(ps):
            amt = money(later["amount_usd"])
            if amt >= 0:
                continue
            for earlier in ps[:i]:
                if earlier["posting_id"] not in cancelled and money(earlier["amount_usd"]) == -amt:
                    cancelled.update({earlier["posting_id"], later["posting_id"]})
                    break
        live = [p for p in ps if p["posting_id"] not in cancelled] or ps
        ledger_customer[key] = live[0]["customer_id"].strip().upper()

    # R3: registered co-sells
    cosell: dict[str, list[dict]] = {}
    for r in rows("co_sell_register.csv"):
        cosell.setdefault(r["deal_id"].strip().upper(), []).append(r)

    # R3: deal occurrence counts (case-insensitive)
    occurrences: dict[str, int] = {}
    for ln in lines:
        occurrences[ln["deal_id"].strip().upper()] = occurrences.get(ln["deal_id"].strip().upper(), 0) + 1

    def registered_cosell(deal: str) -> dict[str, Decimal] | None:
        """partner -> share if the co-sell exception applies to this deal, else None."""
        regs = cosell.get(deal)
        if not regs or any(r["status"].strip().lower() != "active" for r in regs):
            return None
        named = {r["partner"].strip().upper(): Decimal(r["share_pct"]) for r in regs}
        sources = [ln["source_report"].strip().upper() for ln in lines if ln["deal_id"].strip().upper() == deal]
        if sorted(sources) != sorted(named) or sum(named.values()) != 100:
            return None
        return named

    findings, explained = [], []
    counts = {c: 0 for c in PRECEDENCE}
    for ln in lines:
        deal = ln["deal_id"].strip().upper()
        cust = ledger_customer.get(deal, ln["customer_id"].strip().upper())
        etype = end_user_type(cust)
        split = registered_cosell(deal)
        exc = approved.get(deal)
        pays = exc[1] if exc else STANDARD[etype]
        reported = Decimal(ln["reported_rate_pct"])
        revenue = Decimal(ln["revenue_usd"])
        commissionable = pays > 0
        june_net = net.get(deal, Decimal(0))
        target = june_net * split[ln["source_report"].strip().upper()] / 100 if split else june_net
        matched = abs(target - revenue) <= revenue * TOLERANCE

        fails = set()
        if occurrences[deal] > 1 and not split:
            fails.add("DUPLICATE_LINE")
        if commissionable and not matched:
            fails.add("UNMATCHED_TO_LEDGER")
        if reported != pays:
            fails.add("RATE_MISMATCH")
        code = next((c for c in PRECEDENCE if c in fails), None)

        note = (f"{ln['line_id']} {ln['source_report']:8s} {ln['deal_id']:8s} cust={cust}{'*' if cust != ln['customer_id'].strip().upper() else ''} type={etype:7s} "
                f"(partner said {ln['partner_customer_type']}) pays={pays}% reported={reported}% {'split=' + str(split[ln['source_report'].strip().upper()]) + '%' if split else ''} "
                f"exc={exc[0] if exc else '-'} juneNet={june_net} rev={revenue} matched={matched} "
                f"occ={occurrences[deal]} fails={sorted(fails, key=PRECEDENCE.index) or '-'} -> {code or 'compliant'}")
        print(note)
        if code:
            counts[code] += 1
            findings.append({"line_id": ln["line_id"], "deal_id": ln["deal_id"],
                             "source_report": ln["source_report"], "finding_code": code,
                             "_etype": etype, "_pays": pays, "_reported": reported, "_exc": exc,
                             "_net": june_net, "_rev": revenue, "_partner_type": ln["partner_customer_type"],
                             "_cust": cust, "_line_cust": ln["customer_id"].strip().upper(),
                             "_reversed": any(money(p["amount_usd"]) < 0 for p in june_postings.get(deal, []))})
        else:
            # lines that look wrong but are compliant: every contract item 3 category that applies
            deal_rows = [p for p in ledger if p["deal_ref"].strip().upper() == deal]
            outside = [p for p in deal_rows if not (JUNE[0] <= date.fromisoformat(p["posting_date"]) <= JUNE[1])]
            reversal_ids = [p["posting_id"] for p in deal_rows
                            if money(p["amount_usd"]) < 0 or "re-post" in p["memo"].lower()]
            reasons = []
            if repeated_ids.get(deal):                                                    # (a)
                reasons.append(f"the extract repeats posting {', '.join(repeated_ids[deal])}; it is one posting under R6, "
                               f"so net June revenue is {june_net:,.2f}, which matches")
                evidence_values += repeated_ids[deal]
            if reversal_ids:                                                              # (b)
                reasons.append(f"the ledger carries a reversal ({', '.join(reversal_ids)}) but the net June revenue is "
                               f"{june_net:,.2f}, which matches")
                evidence_values += reversal_ids
            if outside:                                                                   # (c)
                reasons.append("posting " + ", ".join(f"{p['posting_id']} ({p['posting_date']})" for p in outside)
                               + " falls outside June and is left out of the June net under R2")
                evidence_values += [p["posting_id"] for p in outside]
            if commissionable and june_net != revenue and not split:                     # (d)
                reasons.append(f"the net June postings total {june_net:,.2f} against revenue {revenue:,.2f}, inside the 1% tolerance")
                evidence_values.append(ln["deal_id"].strip().upper())
            if cust != ln["customer_id"].strip().upper():                                         # (e)
                reasons.append(f"the partner attributes the deal to {ln['customer_id']} but NetSuite bills it to {cust}; "
                               f"the {etype} rate follows the ledger's customer and the reported {reported}% is right")
                evidence_values.append(ln["deal_id"].strip().upper())
            if split:                                                                     # (f)
                reasons.append(f"{ln['deal_id']} is claimed by {' and '.join(sorted(ln2['source_report'] for ln2 in lines if ln2['deal_id'].strip().upper() == deal))}, "
                               f"but the co-sell register carries an active {'/'.join(str(v) for v in split.values())} split naming exactly "
                               f"those partners, so the lines are not duplicates and this one matches its share of the {june_net:,.2f} net")
                evidence_values.append(ln["deal_id"].strip().upper())
            if etype != ln["partner_customer_type"].strip().lower():                      # (g)
                reasons.append(f"the partner tagged it {ln['partner_customer_type']} but the master makes it {etype}; "
                               f"the reported {reported}% is the {etype} rate, so the tag is wrong and the rate is right")
                evidence_values.append(ln["deal_id"].strip().upper())
            if not commissionable and june_net == 0:                                      # (h)
                reasons.append(f"a {etype} line at 0% is not commissionable, so the absence of a June posting is not a finding")
                evidence_values.append(ln["deal_id"].strip().upper())
            if exc and reported != STANDARD[etype]:                                       # item 2
                reasons.append(f"reported {reported}% against a standard {STANDARD[etype]}% for a {etype} line, "
                               f"but override {exc[0]} (active, in force on the run date) approves {exc[1]}%")
            elif not reasons and any(e["deal_id"].strip().upper() == deal for e in exceptions):
                e = next(e for e in exceptions if e["deal_id"].strip().upper() == deal)
                reasons.append(f"register row {e['exception_code']} names this deal but is {e['status']}"
                               f"{'' if e['status'] != 'active' else ' outside its window'}, so it grants nothing and "
                               f"the standard {STANDARD[etype]}% applies, which is what was reported")
            for why in reasons:
                explained.append((ln, why))


    total = len(lines)
    compliant = total - sum(counts.values())
    results = {"total_lines": total, "rate_mismatch_count": counts["RATE_MISMATCH"],
               "unmatched_to_ledger_count": counts["UNMATCHED_TO_LEDGER"],
               "duplicate_line_count": counts["DUPLICATE_LINE"], "compliant_lines": compliant}
    print(f"\n{results}")

    # ---- deliverables ------------------------------------------------------------------
    FILES.mkdir(parents=True, exist_ok=True)
    header = ["line_id", "deal_id", "source_report", "finding_code"]
    csv_text = ",".join(header) + "\n" + "".join(",".join(f[h] for h in header) + "\n" for f in findings)
    (FILES / "commission_findings.csv").write_text(csv_text, encoding="utf-8")
    json_text = json.dumps(results, indent=2) + "\n"
    (FILES / "results.json").write_text(json_text, encoding="utf-8")

    memo = [f"# June 2026 commission reconciliation — {total} consolidated lines", "",
            f"{total} lines from four partner reports checked against COMM-POL-6 on the run date 30 June 2026. "
            f"{compliant} lines are compliant; {total - compliant} carry a finding "
            f"({counts['DUPLICATE_LINE']} duplicate, {counts['UNMATCHED_TO_LEDGER']} unmatched to the ledger, "
            f"{counts['RATE_MISMATCH']} rate mismatches). One finding per line under R5 precedence.", "",
            "## Findings", "", "| Line | Deal | Source | Finding | Why |", "|---|---|---|---|---|"]
    for f in findings:
        if f["finding_code"] == "DUPLICATE_LINE":
            why = f"{f['deal_id']} is claimed on more than one line (R3)"
        elif f["finding_code"] == "UNMATCHED_TO_LEDGER":
            why = (f"commissionable at {f['_pays']}% but net June ledger revenue is {f['_net']:,.2f} against "
                   f"{f['_rev']:,.2f} (R2)")
        else:
            src = f"override {f['_exc'][0]} approves {f['_exc'][1]}%" if f["_exc"] else \
                  (f"NetSuite bills the deal to {f['_cust']}, a {f['_etype']} customer per the master (partner said {f['_partner_type']}), standard {f['_pays']}%"
                   + (" - the posting to the partner's customer was reversed as a wrong entity and re-posted" if f["_reversed"] else "")
                   if f["_cust"] != f["_line_cust"] else
                   f"master makes it {f['_etype']} (partner said {f['_partner_type']}), standard {f['_pays']}%")
            why = f"reported {f['_reported']}%; {src} (R1/R4)"
        memo.append(f"| {f['line_id']} | {f['deal_id']} | {f['source_report']} | {f['finding_code']} | {why} |")
    memo += ["", "## Lines that look wrong but are compliant", ""]
    for lid in repeated_lines:
        memo.append(f"- **{lid}** appears twice in `commission_lines.csv` as an identical row; `line_id` is the list's key, so it is one line, counted once and not a duplicate claim.")
    for ln, why in explained:
        memo.append(f"- **{ln['line_id']} {ln['deal_id']} ({ln['source_report']})** — {why}.")
    memo_text = "\n".join(memo) + "\n"
    (FILES / "commission_memo.md").write_text(memo_text, encoding="utf-8")

    # ---- golden trajectory ------------------------------------------------------------
    reads = ["commission_policy.md", "commission_lines.csv", "customer_master.csv",
             "netsuite_revenue_june.csv", "commission_exceptions.csv", "co_sell_register.csv",
             "submission_format.md"]
    steps = [{"name": "bash", "server": "local", "arguments": {"command": f"cat input/{f}"}} for f in reads]
    steps.append({"name": "bash", "server": "local", "arguments": {
        "command": "cat > commission_findings.csv << 'FINDINGSEOF'\n" + csv_text + "FINDINGSEOF"}})
    steps.append({"name": "bash", "server": "local", "arguments": {
        "command": "cat > commission_memo.md << 'MEMOEOF'\n" + memo_text + "MEMOEOF"}})
    steps.append({"name": "bash", "server": "local", "arguments": {
        "command": "cat > results.json << 'RESULTSEOF'\n" + json_text + "RESULTSEOF"}})
    steps.append({"name": "bash", "server": "local", "arguments": {
        "command": "ls -la commission_findings.csv commission_memo.md results.json"}})
    (TASK / "solution" / "golden_trajectory.json").write_text(json.dumps(steps, indent=2) + "\n", encoding="utf-8")

    # ---- verifier spec ----------------------------------------------------------------
    def exists(name, path, why):
        return {"name": name, "metadata": {"how_justification": f"Checks {path} is present as a file in the workspace.",
                                            "why_justification": why, "tag": "core"},
                "source": {"type": "file", "file": {"type": "filesystem", "command": "check_path_exists",
                                                     "arguments": {"path": path}}},
                "assertion": {"type": "deterministic", "expected": True,
                              "deterministic": {"path": "$.is_file", "comparison": "equals"}}}

    flagged_ids = [f["line_id"] for f in findings]
    # graded memo content: one plain substring check per fact the format names (no regex on
    # prose): every flagged deal (contract item 1), the protected deal and its code (item 2),
    # the posting ids / deal ids of the compliant-but-looks-wrong lines (item 3).
    protected_exc = sorted({(ln["deal_id"].strip().upper(), approved[ln["deal_id"].strip().upper()][0])
                            for ln, _ in explained if ln["deal_id"].strip().upper() in approved})
    flagged_deals = sorted({f["deal_id"].strip().upper() for f in findings})
    ev = sorted(set(evidence_values))
    memo_values = flagged_deals + [d for d, _ in protected_exc] + [c for _, c in protected_exc] + ev

    def memo_contains(name, value, why):
        return {"name": name,
                "metadata": {"how_justification": f"Reads commission_memo.md with md.extract_text and checks the text contains {value!r} (plain substring; wording, order and layout are not graded).",
                             "why_justification": why, "tag": "core"},
                "source": {"type": "file", "file": {"type": "md", "command": "extract_text", "arguments": {"path": "commission_memo.md"}}},
                "assertion": {"type": "deterministic", "expected": value,
                              "deterministic": {"path": "$.text", "comparison": "contains"}}}

    def slug(v): return v.lower().replace('-', '_')
    memo_checks = [memo_contains(f"memo_names_{slug(d)}", d,
                   f"Contract item 1: the memo names every flagged line by its deal_id; {d} is flagged.") for d in flagged_deals]
    for d, c in protected_exc:
        memo_checks.append(memo_contains(f"memo_names_protected_{slug(d)}", d, f"Contract item 2: the line reported off the standard mapping yet compliant is {d}."))
        memo_checks.append(memo_contains(f"memo_quotes_{slug(c)}", c, f"Contract item 2: the exception code that protects that line is {c}."))
    for v in ev:
        kind = "posting id of a repeated, reversed, re-posted or out-of-June ledger row" if v.startswith("P-") else "deal id of a compliant line whose tolerance, customer, co-sell split, partner tag or missing posting looks wrong"
        memo_checks.append(memo_contains(f"memo_evidence_{slug(v)}", v, f"Contract item 3: {kind} behind a compliant line that looks wrong ({v})."))

    spec = {"task_id": "gen-g308-commission-report-reconciliation-audit", "verifiers": [
        exists("findings_exists", "commission_findings.csv", "The findings sheet is delivered."),
        {"name": "findings_header",
         "metadata": {"how_justification": "Opens commission_findings.csv with csv.extract_text and applies a case- and quote-tolerant regex to the first line.",
                      "why_justification": "The contract pins the header verbatim. Entailed by: \"Header, exactly: `line_id,deal_id,source_report,finding_code`\"", "tag": "core"},
         "source": {"type": "file", "file": {"type": "csv", "command": "extract_text", "arguments": {"path": "commission_findings.csv"}}},
         "assertion": {"type": "deterministic",
                       "expected": "(?i)\\A\\x22?line_id\\x22?[ \\t]*,[ \\t]*\\x22?deal_id\\x22?[ \\t]*,[ \\t]*\\x22?source_report\\x22?[ \\t]*,[ \\t]*\\x22?finding_code\\x22?[ \\t]*\\r?\\n",
                       "deterministic": {"path": "$.text", "comparison": "regex_match"}}},
        {"name": "findings_table",
         "metadata": {"how_justification": f"Parses commission_findings.csv with csv.read_rows and applies table_equals: every graded cell of the {len(flagged_ids)} flagged lines plus the population as a row_set lock (a compliant line listed, a flagged line missing, or a duplicated id fails), columns closed to the stated header, id-typed cells normalised on both sides.",
                      "why_justification": "Every flagged line's deal, source and single precedence-assigned finding are graded, so a trusted partner type, a case-sensitive or gross ledger join, an out-of-window or pending override applied, or a duplicate missed shows on the lines it moves. Entailed by: \"One row per flagged line, keyed by `line_id` ... `finding_code` is the single finding the policy's precedence rule assigns to the line\"", "tag": "core"},
         "source": {"type": "file", "file": {"type": "csv", "command": "read_rows", "arguments": {"path": "commission_findings.csv"}}},
         "assertion": {"type": "deterministic",
                       "expected": {"id_column": "line_id",
                                    "rows": {f["line_id"]: {"deal_id": f["deal_id"], "source_report": f["source_report"], "finding_code": f["finding_code"]} for f in findings},
                                    "row_set": flagged_ids,
                                    "columns": header,
                                    "cell_types": {"deal_id": "text", "source_report": "text", "finding_code": "id"}},
                       "deterministic": {"path": "$", "comparison": "table_equals"}}},
        exists("memo_exists", "commission_memo.md", "The memo is delivered."),
        *memo_checks,
        exists("results_exists", "results.json", "Derived figures delivered."),
        {"name": "results_figures",
         "metadata": {"how_justification": "Reads results.json with json.read_file and applies object_equals over the 5 graded keys with the key set closed; a failure names the exact key.",
                      "why_justification": "Each count moves under the master-derived type, the net June ledger join, the override window and status tests, the case-insensitive duplicate test and the R5 precedence; the contract closes the key set.", "tag": "core"},
         "source": {"type": "file", "file": {"type": "json", "command": "read_file", "arguments": {"path": "results.json"}}},
         "assertion": {"type": "deterministic",
                       "expected": {"keys": {k: {"value": v, "tolerance": None} for k, v in results.items()}, "closed": True},
                       "deterministic": {"path": "$", "comparison": "object_equals"}}},
    ]}
    text = json.dumps(spec, indent=2) + "\n"
    (TESTS / "verifier.json").write_text(text, encoding="utf-8")
    (TESTS / "manifest.json").write_text(text, encoding="utf-8")
    print(f"\nmemo must contain ({len(memo_values)} values): {memo_values}")
    print(f"wrote {FILES}, golden_trajectory.json, verifier.json + manifest.json (identical)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
