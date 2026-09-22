# Kestrel — same-day fulfilment terms, and what an offer costs

These terms govern every same-day offer the chain shows. The buyer's order is placed at
14:40 on a Friday in Phenix City, Alabama.

## S1 — the same-day cutoff

Same-day collection and same-day delivery both require the order to be placed
before 15:00 in the fulfilling store's own local time, which is the timezone the store directory gives that store and not the buyer's. A store's own local time is what its `timezone` column says, whatever time it
is where the buyer is standing. Collection is ready two hours after the order; delivery
arrives by 20:00. An order placed on or after the cutoff cannot be fulfilled same-day by
either method, and the offer is refused `CUTOFF_PASSED`.

## S2 — delivery

A same-day delivery additionally requires the delivery address to be within
10 road miles of the fulfilling store, measured by the `distance_mi` column
(`OUT_OF_RADIUS` where it is not), and requires the store to hold at least
2 units of the cord, because one unit is held back as floor stock
(`STOCK_RESERVE` where it does not). Collection carries neither requirement. The
delivery fee is USD 9.99; collection is free.

## S3 — suspended stores

A store whose `same_day_suspended` flag is set cannot fulfil same-day by either method
while the flag stands, and the offer is refused `SAME_DAY_SUSPENDED`.

## S4 — what fits this brick

A cord fits only if all of these hold. Its `connector` must be `C7`, because a `C5`
cloverleaf end will not enter a two-pin inlet (`FIT_CONNECTOR`). It must be
non-polarized, because a keyed C7 will not seat in a non-polarized inlet
(`FIT_POLARIZED`). At any length over 6 ft it must be
18 AWG or heavier, which means a `conductor_awg` of 18 or lower
(`FIT_GAUGE`). Its `length_ft` must be between 10 and 15 feet
inclusive: the buyer asked for ten feet and will take any run that reaches the wall
without coiling, but nothing shorter than the cord it replaces (`FIT_LENGTH`). Every
cord in the listings is rated at or above the brick's 2.5 A and 125 V, so the rating
refuses nothing here.

## S5 — reason precedence

An offer may fail more than one clause. Report the FIRST that applies, in this order:
`FIT_CONNECTOR`, `FIT_POLARIZED`, `FIT_GAUGE`, `FIT_LENGTH`, `STOCK_RESERVE`,
`SAME_DAY_SUSPENDED`, `CUTOFF_PASSED`, `OUT_OF_RADIUS`. An offer that fails none of them is
eligible and its reason is `NONE`.

## S6 — landed cost and the choice

An eligible offer's landed cost is the cord's shelf price plus sales tax at the
FULFILLING store's `sales_tax_pct` — not at the buyer's own rate — rounded to the cent,
plus the delivery fee where the offer is a delivery. The fee is not taxed. Take the
eligible offer with the lowest landed cost. Where two offers land at the same cost, take
the one ready earliest; where they are also ready at the same time, take the nearer store;
where they are also equally near, take the lower `offer_id`.

## S7 — what is out of scope

Only the same-day offers listed count. Standard and two-day shipping, back-order,
ship-to-store and transfers between stores do not put the cord in the buyer's hand today
and are never eligible here, whatever they cost.
