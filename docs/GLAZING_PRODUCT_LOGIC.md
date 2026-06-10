# GLAZING EXPERT — Product Configuration Logic
# Professional glazing knowledge base for ROMI Estimate calculator
# Based on field experience + Alex's business requirements

---

## ⛔ GLOBAL RULES (Never Break These)

```
1. Solarban/Low-E → ONLY in Double Pane IGU (never Single Pane)
   EXCEPTION: Laminated glass can have Low-E interlayer film
   
2. Double Pane IGU → ALWAYS has spacer (color is configurable)

3. If IGU glass type = Tempered → BOTH panes must be tempered

4. Commercial → almost always Tempered (code requirement)
   Exception: interior partitions can be annealed

5. Table Top / Mirror → MUST be tempered + polished edge

6. Auto Glass → WE DO NOT OFFER. Never show.

7. Solarban 70 default combo: Glass #1 = Clear, Glass #2 = Solarban 70
   Low-E default combo: Glass #1 = Clear, Glass #2 = Low-E Advantage
   (Don't make user pick both panes separately for these standard combos)
```

---

## PRODUCT 1: Residential — Single Pane Glass Replacement

**Most common job. Simple window or door glass.**

### Fields:
```
Frame Type (radio):
  ● Wood frame     → glazing compound (putty) method
  ○ Aluminum frame → rubber gasket/vinyl bead method  [auto-shows Gasket Size]
  ○ Vinyl frame    → vinyl bead snap-in
  ○ Steel frame    → glazing compound (heavier)

  AUTO-TRIGGER: If Aluminum/Vinyl selected → show "Glazing Method" as info text
               If Wood selected → show "Glazing Compound included"

Glass Color/Tint (radio):
  ● Clear (standard)
  ○ Bronze tint     +$3/sqft
  ○ Grey tint       +$3/sqft
  ○ Blue tint       +$4/sqft

Glass Thickness (radio):
  ○ 3/32" (very old homes, rare)
  ● 1/8"  (standard residential)
  ○ 3/16" +$2/sqft
  ○ 1/4"  +$4/sqft (heavy/large)

Heat Treatment (radio):
  ● Annealed (standard)
  ○ Tempered  +$15/sqft  [required by code: doors, sidelights, bathrooms, near floor]
  
Special Type (checkbox, optional):
  □ Obscure/Frosted  +$5/sqft  (privacy, bathrooms)
  □ Laminated        +$12/sqft (safety, sound reduction)
```

### ❌ IMPOSSIBLE Combinations:
- Single Pane + Low-E = NO
- Single Pane + Solarban = NO
- Single Pane + Argon = NO (that's IGU)
- Single Pane + Spacer = NO

---

## PRODUCT 2: Residential — Double Pane IGU Replacement

**Most profitable job. Biggest variety of options.**

### Fields:
```
IGU Package (radio) — SIMPLIFIES glass selection:
  ● Clear/Clear (standard, annealed)
  ○ Clear/Low-E Advantage        +$8/sqft  [Glass#1=Clear, Glass#2=Low-E]
  ○ Clear/Solarban 70            +$12/sqft [Glass#1=Clear, Glass#2=Solarban70]
  ○ Tinted/Clear (Bronze or Grey)+$5/sqft
  ○ Custom (pick panes separately) → shows Glass #1 and Glass #2 selectors

Heat Treatment (radio):
  ● Annealed (standard residential)
  ○ Tempered (both panes)   +$18/sqft  [safety locations]
  ○ Heat Strengthened        +$10/sqft

Spacer Color (radio):
  ● Silver (standard)
  ○ Bronze   +$2/sqft
  ○ Black    +$2/sqft  [premium look, Andersen/Pella style]
  ○ Warm Edge (TGI/Swiggle) +$3/sqft  [better thermal]

Spacer Width / Unit Thickness (radio):
  ○ 5/8" unit  (1/8 + 3/8 air + 1/8)  — standard
  ● 3/4" unit  (1/8 + 1/2 air + 1/8)  — most common
  ○ 1" unit    (1/4 + 1/2 air + 1/4)  — heavy/large +$5/sqft
  ○ 1-1/8" unit (commercial grade)     +$8/sqft

Gas Fill (radio):
  ● Air (standard)
  ○ Argon  +$3/sqft  [better insulation, standard upgrade]
  ○ Krypton +$8/sqft [premium, very narrow units]

Grids (radio):
  ● No Grids
  ○ SDL — Simulated Divided Lights (surface applied)  +$45/unit
  ○ GBG — Grilles Between Glass                       +$65/unit
  ○ True Divided Lights (separate panes, rare)        +$150+/unit
```

### ❌ IMPOSSIBLE:
- Solarban 70 on BOTH panes = rare/unnecessary, don't offer
- Low-E on both panes = uncommon, don't offer
- Krypton + 1" unit = rare combo, skip
- Tempered + Krypton = exists but premium only

---

## PRODUCT 3: Foggy IGU Replacement (Failed Seal)

**Seal failed, glass is cloudy/foggy. Replace IGU only, no frame work.**

### Fields:
```
Note shown: "Replacing sealed unit only. Frame stays."

IGU Package (same as Double Pane above)
Spacer Color (same)
Gas Fill (same)

Frame Material (radio) — affects labor:
  ● Vinyl/Aluminum (snap-in, easier)
  ○ Wood (glazed in, harder)   +$25/unit labor

Number of Panes (if multiple foggy):
  Qty: [1] [2] [3] [4] [5+]
  (each unit priced separately)
```

---

## PRODUCT 4: Tempered Glass — Custom Cut

**Cut-to-size tempered glass. Table tops, shower panels, custom shapes.**

### Fields:
```
Application (radio) — affects edge work requirement:
  ● Table Top       → Polished edge required (auto-check)
  ○ Shelf           → Polished edge recommended
  ○ Window/Door     → Seamed edge OK
  ○ Shower Panel    → Polished edge required (auto-check)
  ○ Railing/Balcony → Polished edge required (auto-check)
  ○ Custom/Other

Thickness (radio):
  ○ 1/4"  (6mm) — standard tables, shelves
  ● 3/8"  (10mm) — most common tempered
  ○ 1/2"  (12mm) — heavy duty, large panels  +$8/sqft
  ○ 3/4"  (19mm) — structural               +$20/sqft

Glass Color (radio):
  ● Clear
  ○ Low Iron (Starphire/Optiwhite) +$10/sqft [ultra-clear, no green tint]
  ○ Bronze tint  +$5/sqft
  ○ Grey tint    +$5/sqft

Edge Finish (radio):
  ○ Seamed only (remove sharp edge, no polish) — cheapest
  ● Flat Polish  +$8/linear ft — standard finish
  ○ Pencil Polish +$10/linear ft — rounded edge
  ○ Beveled 1"   +$15/linear ft — decorative

Holes/Cutouts (checkbox):
  □ Drilled holes: [qty input] × $25 each
  □ Notch/Corner cut: [qty] × $35 each
  □ Radius corners: [qty] × $20 each

Delivery/Service (radio):
  ○ Pickup at shop (no install)
  ● Delivery only            +$75
  ○ Delivery + Install       +standard labor
```

### ❌ IMPOSSIBLE:
- Tempered glass CANNOT be cut after tempering (must order exact size)
- Cannot add holes after tempering
- Low-E coating not available on standard tempered (exists on special order, skip for now)

---

## PRODUCT 5: Laminated Safety Glass

**Two panes bonded with PVB interlayer. Safety, sound, UV.**

### Fields:
```
Construction (radio):
  ● 1/4" Laminated (1/8 + PVB + 1/8) — standard
  ○ 3/8" Laminated (3/16 + PVB + 3/16) +$8/sqft
  ○ 1/2" Laminated (1/4 + PVB + 1/4)   +$15/sqft

Interlayer (radio):
  ● Standard PVB (clear)
  ○ Acoustic PVB    +$10/sqft [sound reduction]
  ○ Low-E interlayer +$12/sqft [energy + safety — THIS is where Low-E works in laminated!]
  ○ Tinted PVB (Bronze/Grey) +$8/sqft

Heat Treatment (radio):
  ● Annealed
  ○ Heat Strengthened +$10/sqft [both lites]
  ○ Tempered (both)   +$20/sqft [rare, very strong]

Edge (radio):
  ● Seamed
  ○ Polished +$8/lf
```

---

## PRODUCT 6: Obscure / Frosted Glass

**Privacy glass. Bathrooms, sidelights, office doors.**

### Fields:
```
Pattern (radio):
  ● Rain/Glue Chip (most common)
  ○ Satin/Acid Etch (smooth frosted) +$3/sqft
  ○ Reeded (vertical lines)
  ○ Flemish (old-style)
  ○ Custom pattern (special order) — note lead time

Frame Type (same as Single Pane)
Thickness:
  ● 1/8"  ○ 3/16"  ○ 1/4"
Heat Treatment:
  ● Annealed  ○ Tempered +$15/sqft
```

---

## PRODUCT 7: Tinted Glass (Monolithic)

**Solar control single pane. Bronze, Grey, Blue.**

### Fields:
```
Color (radio):
  ● Bronze (most common)
  ○ Grey
  ○ Blue/Azurlite
  ○ Green (rare)

Thickness (radio):
  ○ 1/8"  ● 3/16"  ○ 1/4"  ○ 3/8"

Heat Treatment:
  ● Annealed  ○ Tempered +$15/sqft
```

### Note: Cannot add Low-E to monolithic tinted. For Low-E + Tint → use IGU with tinted outer + Low-E inner.

---

## PRODUCT 8: Commercial Storefront Glass

**Plate glass in aluminum storefront system (Kawneer, YKK, etc.)**

### Fields:
```
System Type (radio):
  ● Single Pane Storefront (common in older buildings)
  ○ IGU Storefront (newer energy code compliant)

  → If Single Pane selected:
    Glass Type:
      ● Clear Tempered 1/4"
      ○ Clear Tempered 3/8"  +$8/sqft
      ○ Tinted Tempered (Bronze/Grey) +$5/sqft
      ○ Laminated (security) +$15/sqft

  → If IGU selected: (same as Double Pane IGU options)
    Default: Clear/Solarban 70, Tempered both panes, 1" unit

Heat Treatment (commercial always tempered unless interior):
  ● Tempered (code required for entry/exit)
  ○ Annealed (interior only, non-safety location)

Setting Block / Gasket:
  ● Included (standard for storefront work)
```

### ❌ IMPOSSIBLE:
- Annealed glass in exterior commercial entry = code violation, don't offer
- Solarban Single Pane storefront = doesn't exist

---

## PRODUCT 9: Office Partition Glass

**Interior glass walls, conference rooms.**

### Fields:
```
Type (radio):
  ● Single Pane (most common interior)
  ○ Double Pane IGU (for sound)  +$20/sqft

Glass (radio):
  ● Clear
  ○ Low Iron (Starphire)  +$10/sqft
  ○ Acid Etch (privacy)   +$8/sqft
  ○ Tinted               +$4/sqft

Heat Treatment (radio):
  ● Tempered (recommended, often required)
  ○ Annealed (not recommended)

Thickness:
  ○ 1/4"  ● 3/8"  ○ 1/2"

Edge:
  ● Seamed  ○ Polished +$8/lf
```

---

## PRODUCT 10: Commercial Door Glass

**Glass panel in metal/wood door frame.**

### Fields:
```
Door Type (radio):
  ● Aluminum storefront door (narrow stile)
  ○ Hollow metal door (welded frame)
  ○ Wood door

Glass Type (radio):
  ● Tempered Clear 1/4"
  ○ Tempered Clear 3/8"  +$6/sqft
  ○ Tempered Wired (fire rated) — note: fire door
  ○ Laminated             +$15/sqft

Wire Glass: (checkbox, fire-rated only)
  □ Fire-rated wired glass (older code, 45-min rated)
  □ FireLite / Pyroguard (newer, clearer)  +$30/sqft
```

---

## PRODUCT 11: Table Top Glass

**Cut-to-size tempered glass for furniture.**

### Fields:
```
Shape (radio):
  ● Rectangle
  ○ Round / Oval
  ○ Custom shape (measure carefully, no refund on custom)

Thickness (radio):
  ○ 1/4" (light tables)
  ● 3/8" (standard)
  ○ 1/2" (heavy duty)

Glass Type (radio):
  ● Clear tempered
  ○ Low Iron / Starphire +$10/sqft [no green edge, premium look]
  ○ Tinted (Bronze/Grey) +$5/sqft

Edge Finish (radio):
  ○ Seamed (sharp removal only)
  ● Flat Polish (standard table edge) +$8/lf
  ○ Pencil Polish (rounded) +$10/lf
  ○ Beveled 1" +$15/lf

Corners (radio):
  ● Square corners
  ○ Clipped corners (small chamfer) +$10/ea
  ○ Radius corners (rounded) +$15/ea

Holes (checkbox):
  □ Center hole (umbrella): 2" hole +$40
  □ Custom holes: [qty] × $25
```

### AUTO-RULE: Table top = always tempered. No option to un-temper.

---

## PRODUCT 12: Custom Mirror

**Cut-to-size mirror installation.**

### Fields:
```
Mirror Type (radio):
  ● Standard Silver Mirror (most common)
  ○ Low Copper / Ecology Mirror +$5/sqft [bathroom, moisture resistant]
  ○ Antique Mirror +$15/sqft [vintage look]
  ○ Back-painted / Lacobel +$12/sqft [color mirror]

Thickness (radio):
  ● 1/8" (standard wall mirror)
  ○ 3/16" +$3/sqft (larger pieces)
  ○ 1/4"  +$6/sqft (frameless, heavy)

Edge Finish (radio):
  ○ Seamed
  ● Flat Polish +$8/lf
  ○ Beveled 1" +$15/lf [classic bathroom mirror look]

Installation (radio):
  ● J-Channel (standard, clips)  — included
  ○ Mastic adhesive only
  ○ French cleat

Holes (checkbox):
  □ Electrical outlet cutout +$45
  □ Custom holes [qty] × $25
```

### ❌ NOTE: Mirrors are NOT tempered (silvering process is incompatible with tempering)
### EXCEPTION: Shower mirrors on walls sometimes get tempered — special order

---

## PRODUCT 13: Shower Door / Enclosure

**Most expensive residential job. Always tempered.**

### Fields:
```
Type (radio):
  ● Frameless (no metal frame, silicone/hardware only) — premium
  ○ Semi-frameless (frame on sides only)
  ○ Framed (full aluminum frame) — budget

Glass Thickness (radio):
  ○ 3/8" (frameless minimum, semi-frameless)
  ● 1/2" (standard frameless) — most sold
  ○ 3/4" (ultra-premium, heavy)  +$25/sqft

Glass Type (radio):
  ● Clear Tempered
  ○ Low Iron / Starphire +$12/sqft [no green tint, premium]
  ○ Acid Etch / Satin +$10/sqft [privacy]
  ○ Rain (textured) +$8/sqft

Coating (checkbox):
  □ ClearShield / EnduroShield (water repellent) +$150/enclosure

Configuration (radio):
  ● Single door (swinging)
  ○ Double door (French style)  +$200
  ○ Sliding door (bypass)
  ○ Fixed panel + door
  ○ Full enclosure (3-4 sides)  → custom quote

Hardware Finish (radio):
  ● Chrome (standard)
  ○ Brushed Nickel  +$50
  ○ Matte Black      +$75
  ○ Oil Rubbed Bronze +$75
  ○ Polished Gold    +$150
```

### AUTO-RULES:
- Shower = always tempered (no option)
- Frameless = minimum 3/8", default 1/2"
- Framed = 1/4" is OK

---

## PRICING IMPACT SUMMARY

| Option | Price Impact |
|--------|-------------|
| Tempered upgrade | +$15-18/sqft |
| Low-E coating (IGU) | +$8/sqft |
| Solarban 70 (IGU) | +$12/sqft |
| Argon fill | +$3/sqft |
| Low Iron / Starphire | +$10/sqft |
| Laminated | +$12-15/sqft |
| Flat Polish edge | +$8/linear ft |
| Beveled edge | +$15/linear ft |
| Bronze/Black spacer | +$2/sqft |
| Grids (SDL) | +$45/unit |
| Grids (GBG) | +$65/unit |
| Holes drilled | +$25/each |
| 2nd floor | +$150 flat |
| 3rd floor+ | +$300 flat |
| Same-day | +30% |
| Emergency | +50% |

---

## MISTAKES TO FIX IN CURRENT CALCULATOR

1. ❌ "Solarban 70 Glass" listed as Residential single product → WRONG
   ✅ It's an IGU OPTION, not a standalone product

2. ❌ "Low-E Insulated Glass" listed separately → partially wrong name
   ✅ Should be "Double Pane IGU — Low-E Package"

3. ❌ Auto Glass listed (products 37-45) → WE DON'T OFFER
   ✅ Remove from database

4. ❌ "Tinted Glass" as separate product → confusing
   ✅ Should be option within Single Pane and IGU

5. ❌ No distinction between annealed and tempered for same glass type
   ✅ Should be a radio button within each product

---

*Written by: Senya (Glazing Expert mode)*
*Based on: Alex's field knowledge + professional glazing standards*
*Date: 2026-06-10*
