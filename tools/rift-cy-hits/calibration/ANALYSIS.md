# Rift CY calculator — calibration pass 1 (6 reports, Fungal L12)

## Model (mirrors wall-break sim structure)
- Attacker CY strength = N × u × M + GiantSlayer
  - M = 1 + equipCY% + flameThrower% + warwagon5% + **0.60 fixed** (the "+60%" shown
    at the Courtyard step in every report — empirically constant)
  - GiantSlayer = 9% × defender total CY strength (per tooltip), cap 3× attacker
    strength (uncapped in all 6 reports — values ~25M regardless of army size)
- Defender CY strength = 280M  (derived: GS 25.2M ÷ 9%; = 1M units @ +400% → base ~56/unit)
- Winner's losses = N × (weaker/stronger)^1.5 ; loser loses 100% (classic GGE curve)

## Fit (pass 1)
- Single effective unit attack u = **2410** → rms error **16.7%** on losses
  (r2 +1%, r5 +7%, r6 −9%, r4 +18%, r3 −31%)
- r1 (Gzer, 100% wipe despite killing all 1M) is consistent ONLY with a ranged
  attack malus (×0.4) — i.e. fungal L12 nerfs ranged like necromancer does.
  Full-melee his hit models as a win; ranged-malused it models as the defeat it was.
- Residual spread is almost certainly REAL UNIT DIFFERENCES (players sent
  different L10 rift units; one fitted u can't capture that). v2: resolve unit
  stacks to real attack stats from troops-tools.json and refit a single global
  scale (like wall-break's ALPHA).

## What the remaining ~40 reports should ideally add
1. **Partial clears** — all 6 killed the full 1M, so the KILL curve (hits-to-clear
   for weaker hits) only has a lower bound. Reports where the CY was NOT fully
   cleared pin it directly. Even 3-4 of these are gold.
2. **Unit-stack screenshots** (or tell us which units the (10)-badge stacks are).
3. Points scored per hit if visible.
4. Any different boss level — even one L11/L13 report validates level scaling.

## Pass 2 (batch 2: +3 Fungal L11, +1 Ashen — 10 reports total)
- **Dormant spores/eggs have ZERO defensive strength** but inflate the CY kill count.
  Proven three ways: GS = 9% × (real units only) at L11 (18.05/18.08/18.14M ≈ 9% × 201.7M)
  and L12 (25.2M ≈ 9% × 280M); real-spore base def ≈ 56 at BOTH levels.
- **Refit u = 2440, rms 13.7%** across 8 victories spanning L11+L12 — same constants
  predict both levels (L11 Shawno1 +0%, L12 Rage −1%, L11 Gzer −3%, L12 Lydia +5%).
  Outlier: Stu −32% (likely stronger units; unit-type resolution will fix).
- **Boss attacker-debuffs from game data** (rift-bosses.json, no GeneralsCamp needed):
  Fungal = NONE (all levels). Necromancer: L11 −60% RANGED, L12/13 −60% MELEE (flips!).
  Ashen = none, but CY is 70% ranged defenders, tiny CY (30–40k) @ +1800–2200%.
- **Ashen single report**: dragon real CY units base def ≈ 298 (5× spores), but CY mostly
  weak eggs → losses tiny (312 of 67,689).
- Gzer's L12 full wipe remains the one anomaly (model says narrow win, 72% losses;
  reality 100% loss in the "Close defeat" steep zone near strength parity).
- **Calculator design implication**: CY size must be an input (report shows it) because
  dormant stacking varies it; strength side uses REAL units only = base CY from game data.
