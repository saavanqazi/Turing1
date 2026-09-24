#!/usr/bin/env python3
"""g308_extend_inputs.py — grow the g308 inputs to a realistic run size (round 8).

Keeps the 35 hand-built lines and their ledger stories untouched and appends ~100 filler
deals across the same four partner reports, with a handful of planted shapes that the
policy already rules on (R1 reversed pair, R6 keys and case, R4 windows, R3 registers).
Deterministic (seeded); run once from the repo root, then solution/compute_gold.py.
"""
import csv, random
from datetime import date, timedelta
from pathlib import Path

INP = Path(__file__).resolve().parents[1] / "task-g308" / "environment" / "input"
rng = random.Random(308)

def read(name):
    with open(INP / name, newline="", encoding="utf-8") as fh:
        r = csv.reader(fh); return next(r), list(r)

def write(name, header, rows):
    with open(INP / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(header); w.writerows(rows)

cust_h, custs = read("customer_master.csv")
line_h, lines = read("commission_lines.csv")
led_h, ledger = read("netsuite_revenue_june.csv")
exc_h, excs = read("commission_exceptions.csv")
cos_h, cosell = read("co_sell_register.csv")
assert len(custs) == 18 and len(lines) == 36 and ledger[-1][0] == "P-1033"

# ---- customers CUST-19..CUST-58
A = ["Alder", "Birch", "Cobalt", "Dunmore", "Ember", "Fallow", "Granite", "Harlow", "Isley", "Juniper",
     "Kelso", "Larkin", "Marrow", "Nettle", "Oakridge", "Pellman", "Quill", "Rowan", "Sorrel", "Thorne",
     "Umber", "Vesper", "Wrenfield", "Yarrow", "Zeller", "Ashby", "Bramble", "Calder", "Dorset", "Elmsley",
     "Finch", "Garland", "Hollis", "Ivory", "Jarrow", "Kestrel", "Linden", "Moss", "Norwell", "Osprey"]
B = ["Logistics", "Analytics", "Foods", "Dental", "Robotics", "Marine", "Clinics", "Energy", "Media", "Civil",
     "Optics", "Schools", "Farms", "Textiles", "Labs", "Freight", "Holdings", "Systems", "Brewing", "Health"]
new_custs = []
for i in range(19, 59):
    cid = f"CUST-{i:02d}"
    name = f"{A[i-19]} {rng.choice(B)}"
    cls = "standard"
    # first invoice: spread 2019..2026, a few right at the R1 boundary
    days = rng.randint(0, 7 * 365)
    first = date(2019, 6, 1) + timedelta(days=days)
    if i == 23: first = date(2025, 6, 30)      # renewal by one day
    if i == 31: first = date(2025, 7, 1)       # new by the boundary
    if i in (27, 44): cls = "house"
    if i == 44: cls = "House"
    new_custs.append([cid, name, cls, first.isoformat()])
custs += new_custs
cls_of = {c[0].upper(): c[2].strip().lower() for c in custs}
first_of = {c[0].upper(): date.fromisoformat(c[3]) for c in custs}
def etype(cid):
    cid = cid.upper()
    if cls_of[cid] == "house": return "house"
    return "new" if first_of[cid] >= date(2025, 7, 1) else "renewal"
STD = {"new": 8, "renewal": 4, "house": 0}

# ---- filler deals DEAL-32..DEAL-131
partners = ["PartnerA", "PartnerB", "PartnerC", "PartnerD"]
new_lines, new_ledger, new_excs, new_cos = [], [], [], []
lid = 36; pid = 1034
def fmt_amt(v, neg=False):
    s = f"${v:,.2f}"
    return f"({s})" if neg else s
def rate_str(partner, r):
    return f"{r}.0" if partner == "PartnerD" else str(r)
june_days = [date(2026, 6, d) for d in range(1, 31)]
plans = {}
for n in range(32, 132):
    deal = f"DEAL-{n:03d}"
    partner = rng.choice(partners)
    cid = rng.choice([c[0] for c in new_custs])
    et = etype(cid)
    rev = rng.choice(range(5000, 120001, 500))
    plans[deal] = dict(partner=partner, cid=cid, et=et, rev=rev, rate=STD[et], tag=et, ledger="june", note="June invoice")
P = plans
# planted shapes (each ruled on by the policy)
P["DEAL-040"].update(rate=6)                                   # plain RATE_MISMATCH
P["DEAL-047"].update(rate=8, et_force="renewal")               # partner tags renewal customer as new at 8%
P["DEAL-055"].update(ledger="july")                            # UNMATCHED: posted July
P["DEAL-063"].update(ledger="none")                            # UNMATCHED: nothing posted
P["DEAL-071"].update(ledger="within")                          # within tolerance (0.6% short)
P["DEAL-078"].update(ledger="outside")                         # 3% short -> UNMATCHED
P["DEAL-084"].update(ledger="split")                           # two postings sum to revenue
P["DEAL-090"].update(ledger="repeat")                          # identical posting row repeated (R6 key)
P["DEAL-096"].update(ledger="wrong_entity")                    # reversed + re-posted to a customer of another type (R1)
P["DEAL-102"].update(ledger="lowercase")                      # deal_ref/customer in lower case (R6)
P["DEAL-108"].update(rate=5, exc=("EXC-VP-08", "active", "2026-01-01", "2026-06-29"))   # override expired day before run
P["DEAL-114"].update(rate=6, exc=("EXC-VP-09", "active", "2026-03-01", "2026-12-31"))   # valid override -> compliant
P["DEAL-119"].update(rate=4, house=True)                      # house customer claimed at 4% -> RATE_MISMATCH
P["DEAL-125"].update(rate=0, house=True)                      # house at 0% -> compliant, no ledger needed
P["DEAL-128"].update(dup="plain")                             # claimed twice, no register
P["DEAL-131"].update(cosell="valid")                          # registered 50/50, both partners on lines
P["DEAL-121"].update(cosell="wrong_partner")                  # register names a partner not on the lines
P["DEAL-105"].update(repeat_line=True)                        # identical line row re-sent later (R6 key)
P["DEAL-036"].update(ledger="july_credit")                    # June invoice fully credited in July (June net still matches)
P["DEAL-073"].update(ledger="july_credit")
P["DEAL-051"].update(ledger="double_reversed")                # posted twice in error, second posting reversed
P["DEAL-066"].update(ledger="cust_diff")                      # ledger bills a different customer of the same type

house_ids = [c[0] for c in new_custs if c[2].strip().lower() == "house"]
for deal, p in P.items():
    if p.get("house"):
        p["cid"] = house_ids[0] if deal == "DEAL-119" else house_ids[1]; p["et"] = "house"; p["tag"] = "house"
    if p.get("et_force"):
        # pick a customer of that type
        p["cid"] = rng.choice([c[0] for c in new_custs if etype(c[0]) == p["et_force"]]); p["et"] = p["et_force"]; p["tag"] = "new"
    if "rate" not in p or p.get("rate") is None: p["rate"] = STD[p["et"]]
    if p.get("rate") == STD[p["et"]] and not p.get("house") and not p.get("exc") and not p.get("et_force") and deal not in ("DEAL-040",):
        p["rate"] = STD[p["et"]]
    partner, cid, rev = p["partner"], p["cid"], p["rev"]
    row = [f"L-{lid:03d}", partner, deal, cid, p["tag"], rate_str(partner, p["rate"]), str(rev)]
    new_lines.append(row); p["line"] = row; lid += 1
    if p.get("dup") == "plain":
        other = rng.choice([x for x in partners if x != partner])
        new_lines.append([f"L-{lid:03d}", other, deal, cid, p["tag"], rate_str(other, p["rate"]), str(rev)]); lid += 1
    if p.get("cosell") == "valid":
        other = rng.choice([x for x in partners if x != partner])
        half = rev // 2
        row[6] = str(half)
        new_lines.append([f"L-{lid:03d}", other, deal, cid, p["tag"], rate_str(other, p["rate"]), str(rev - half)]); lid += 1
        new_cos += [[deal, partner, "50", "active"], [deal, other, "50", "active"]]
    if p.get("cosell") == "wrong_partner":
        other = rng.choice([x for x in partners if x != partner])
        third = rng.choice([x for x in partners if x not in (partner, other)])
        half = rev // 2
        row[6] = str(half)
        new_lines.append([f"L-{lid:03d}", other, deal, cid, p["tag"], rate_str(other, p["rate"]), str(rev - half)]); lid += 1
        new_cos += [[deal, partner, "60", "active"], [deal, third, "40", "active"]]
    if p.get("exc"):
        code, status, f, t = p["exc"]; new_excs.append([code, deal, str(p["rate"]), status, f, t])
    # ledger
    d = rng.choice(june_days)
    kind = p["ledger"]
    if p.get("house") and kind == "june": kind = "june"
    if kind == "june":
        new_ledger.append([f"P-{pid}", d.isoformat(), deal, cid, fmt_amt(rev), "June invoice"]); pid += 1
    elif kind == "july":
        new_ledger.append([f"P-{pid}", date(2026, 7, rng.randint(1, 6)).isoformat(), deal, cid, fmt_amt(rev), "July invoice"]); pid += 1
    elif kind == "none":
        pass
    elif kind == "within":
        new_ledger.append([f"P-{pid}", d.isoformat(), deal, cid, fmt_amt(rev * 0.994), "June invoice - net of early-settlement discount"]); pid += 1
    elif kind == "outside":
        new_ledger.append([f"P-{pid}", d.isoformat(), deal, cid, fmt_amt(rev * 0.97), "June invoice - partial"]); pid += 1
    elif kind == "split":
        a = (rev * 6) // 10
        new_ledger.append([f"P-{pid}", d.isoformat(), deal, cid, fmt_amt(a), "June invoice part 1"]); pid += 1
        new_ledger.append([f"P-{pid}", (d + timedelta(days=3)).isoformat() if d.day <= 27 else d.isoformat(), deal, cid, fmt_amt(rev - a), "June invoice part 2"]); pid += 1
    elif kind == "repeat":
        r = [f"P-{pid}", d.isoformat(), deal, cid, fmt_amt(rev), "June invoice"]; pid += 1
        new_ledger.append(r); p["repeat_row"] = list(r)
    elif kind == "wrong_entity":
        # posted to a customer of the other type, reversed, re-posted to the line's customer
        wrong = rng.choice([c[0] for c in new_custs if etype(c[0]) not in (p["et"], "house")])
        p["wrong_cid"] = wrong
        new_ledger.append([f"P-{pid}", d.isoformat(), deal, wrong, fmt_amt(rev), "June invoice"]); a = pid; pid += 1
        new_ledger.append([f"P-{pid}", d.isoformat(), deal, wrong, fmt_amt(rev, neg=True), f"reversal of P-{a} - wrong entity"]); pid += 1
        d2 = d + timedelta(days=1) if d.day <= 29 else d
        new_ledger.append([f"P-{pid}", d2.isoformat(), deal, cid, fmt_amt(rev), "June invoice re-posted to the correct entity"]); pid += 1
        # the line reports the WRONG customer's rate: the partner keyed the invoice's first entity
        row[3] = wrong; row[4] = etype(wrong); row[5] = rate_str(partner, STD[etype(wrong)])
    elif kind == "july_credit":
        new_ledger.append([f"P-{pid}", d.isoformat(), deal, cid, fmt_amt(rev), "June invoice"]); a = pid; pid += 1
        new_ledger.append([f"P-{pid}", date(2026, 7, rng.randint(2, 9)).isoformat(), deal, cid, fmt_amt(rev, neg=True), f"credit note against P-{a} - issued July"]); pid += 1
    elif kind == "double_reversed":
        new_ledger.append([f"P-{pid}", d.isoformat(), deal, cid, fmt_amt(rev), "June invoice"]); pid += 1
        new_ledger.append([f"P-{pid}", d.isoformat(), deal, cid, fmt_amt(rev), "June invoice"]); a = pid; pid += 1
        d2 = d + timedelta(days=2) if d.day <= 28 else d
        new_ledger.append([f"P-{pid}", d2.isoformat(), deal, cid, fmt_amt(rev, neg=True), f"reversal of P-{a} - posted twice in error"]); pid += 1
    elif kind == "cust_diff":
        other = rng.choice([c[0] for c in new_custs if etype(c[0]) == p["et"] and c[0] != cid])
        name = next(c[1] for c in new_custs if c[0] == other)
        new_ledger.append([f"P-{pid}", d.isoformat(), deal, other, fmt_amt(rev), f"June invoice - billed to {name}"]); pid += 1
    elif kind == "lowercase":
        new_ledger.append([f"P-{pid}", d.isoformat(), deal.lower(), cid.lower(), fmt_amt(rev), "June invoice"]); pid += 1

# repeated line row re-sent near the end of the list; repeated posting row far from its twin
rep = list(P["DEAL-105"]["line"])
new_lines.insert(len(new_lines) - 6, rep)
new_ledger.sort(key=lambda r: (r[1], r[0]))
rr = P["DEAL-090"]["repeat_row"]
idx = next(i for i, r in enumerate(new_ledger) if r[0] == rr[0])
new_ledger.insert(min(idx + 37, len(new_ledger)), rr)

write("customer_master.csv", cust_h, custs)
write("commission_lines.csv", line_h, lines + new_lines)
write("netsuite_revenue_june.csv", led_h, ledger + new_ledger)
write("commission_exceptions.csv", exc_h, excs + new_excs)
write("co_sell_register.csv", cos_h, cosell + new_cos)
print(f"lines {len(lines)+len(new_lines)} rows, ledger {len(ledger)+len(new_ledger)} rows, customers {len(custs)}, exceptions {len(excs)+len(new_excs)}, co-sell rows {len(cosell)+len(new_cos)}")
print("wrong entity:", P["DEAL-096"]["wrong_cid"], "->", P["DEAL-096"]["cid"], "line reports", P["DEAL-096"]["line"])
