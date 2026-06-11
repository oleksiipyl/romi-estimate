"""
LA Glass Market Benchmarks — compiled 2026-06-11
Sources: Angi, Modernize, CostToRenovate, DesignTransitionStudio, Homewyse,
         InsightGlass, ProGlassGV, AmericanGlassExperts, HCP historical job data
Research by: VICTOR — Senior Glazing Consultant (35 yrs LA market)
"""

MARKET_BENCHMARKS = {
    "single_pane": {
        "label": "Single Pane Glass Replacement",
        "market_avg_sqft": 82,      # $/sqft — LA residential market average
        "market_low_sqft": 55,      # budget/contractor pricing
        "market_high_sqft": 130,    # premium tempered, difficult access
        "our_avg_sqft": 125,        # Fast Glass HCP avg (78 jobs)
        "our_avg_job": 811,         # Fast Glass avg job value
        "our_min_job": 199,
        "our_max_job": 7600,
        "job_count": 78,
        "vs_market": "+52%",        # our pricing vs market avg
        "sources": ["Modernize 2026", "CountBricks LA", "Angi LA", "HCP historical"],
        "note": (
            "Standard residential single pane. LA market $383-$800/opening. "
            "Our avg $124.8/sqft — significantly above market avg, suggesting "
            "premium positioning or larger/commercial panes in mix. "
            "Competitive floor: ~$55/sqft; premium ceiling: ~$130/sqft."
        ),
    },

    "double_pane_igu": {
        "label": "Double Pane IGU Replacement",
        "market_avg_sqft": 105,     # $/sqft — LA installed
        "market_low_sqft": 70,      # standard double-hung, vinyl frame
        "market_high_sqft": 160,    # Low-E, argon, difficult access, premium brand
        "our_avg_sqft": 116,        # Fast Glass HCP avg (223 jobs)
        "our_avg_job": 1203,
        "our_min_job": 232,
        "our_max_job": 4987,
        "job_count": 223,
        "vs_market": "+11%",        # healthy premium over market
        "sources": [
            "DesignTransitionStudio IGU guide 2026",
            "Modernize LA 2026 ($450-$525/window standard)",
            "ProjectCostAtlas LA ($576-$1,792/window)",
            "HCP historical",
        ],
        "note": (
            "LA market: $210-$640/unit installed (basic to Low-E argon). "
            "Modernize reports $450-$525/window for standard vinyl replacement. "
            "Our $116/sqft is a solid 11% above market avg — well-positioned. "
            "Largest category by volume (223 jobs) — strong data confidence."
        ),
    },

    "shower_door": {
        "label": "Frameless Shower Door / Enclosure",
        "market_avg_sqft": 130,     # $/sqft — frameless installed, LA
        "market_low_sqft": 80,      # semi-frameless, 3/8\" glass, standard hardware
        "market_high_sqft": 220,    # custom panel system, 1/2\" glass, premium hardware
        "market_avg_job": 2430,     # LA mid-range project (CostToRenovate)
        "market_low_job": 945,      # budget (semi-frameless)
        "market_high_job": 5400,    # premium custom
        "our_avg_sqft": 161,        # Fast Glass HCP avg (6 jobs)
        "our_avg_job": 990,
        "our_min_job": 450,
        "our_max_job": 1895,
        "job_count": 6,             # low sample — use with caution
        "vs_market": "+24%",        # per sqft; but avg job is BELOW market
        "sources": [
            "CostToRenovate LA frameless 2026 ($945-$5,400)",
            "AmericanGlassExperts LA 2026",
            "AffordableFrameless LA",
            "HCP historical (n=6, low confidence)",
        ],
        "note": (
            "LA market: $1,215-$4,725 typical range (CostToRenovate, +35% vs national). "
            "Frameless hinged: $900-$2,500. Custom panel system: $2,000-$6,000. "
            "Our avg job ($990) is BELOW market avg ($2,430) — likely doing smaller "
            "repairs/single panels vs full enclosures. Only 6 HCP jobs — low confidence. "
            "Opportunity: upsell full enclosure packages."
        ),
    },

    "mirror": {
        "label": "Custom Mirror (Cut, Polish & Install)",
        "market_avg_sqft": 65,      # $/sqft — LA custom cut + polished edge + install
        "market_low_sqft": 35,      # simple vanity mirror, standard size
        "market_high_sqft": 130,    # full-wall custom, beveled, backlit
        "our_avg_sqft": 125,        # Fast Glass HCP avg (9 jobs)
        "our_avg_job": 722,
        "our_min_job": 390,
        "our_max_job": 1100,
        "job_count": 9,             # low sample
        "vs_market": "+92%",        # our sqft pricing nearly 2x market
        "sources": [
            "Homewyse 2026 ($13.86-$19.93/sqft national — basic install)",
            "Angi 2026 ($525-$2,000 wall mirror install)",
            "Homeyou LA custom mirrors",
            "HCP historical (n=9, low confidence)",
        ],
        "note": (
            "Homewyse national avg $14-$20/sqft for basic mirror install. "
            "LA premium + custom cutting + polished edges: $35-$130/sqft. "
            "Our $125/sqft strongly suggests specialty work (custom cut, "
            "thick glass, complex shapes). If doing standard vanity mirrors, "
            "we are significantly above market — verify job types. "
            "Low job count (9) — limited data reliability."
        ),
    },

    "commercial_storefront": {
        "label": "Commercial Storefront Glass Replacement",
        "market_avg_sqft": 80,      # $/sqft — LA commercial, installed
        "market_low_sqft": 50,      # simple panel, standard aluminum frame
        "market_high_sqft": 150,    # tempered, specialty tint, complex framing
        "market_avg_job": 5000,     # typical LA storefront project
        "market_low_job": 2400,
        "market_high_job": 15000,
        "our_avg_sqft": 93,         # Fast Glass HCP avg (3 jobs)
        "our_avg_job": 1713,
        "our_min_job": 1100,
        "our_max_job": 2520,
        "job_count": 3,             # very low sample — use with extreme caution
        "vs_market": "+16%",        # per sqft reasonable premium
        "sources": [
            "DesignTransitionStudio storefront guide ($18-$90/sqft)",
            "InsightGlass ($50-$150/sqft Bay Area)",
            "ProGlassGV CA calculator ($3,000-$15,000+)",
            "CommercialGlassWorks ($500-$5,000)",
            "HCP historical (n=3, very low confidence)",
        ],
        "note": (
            "LA commercial market: $2,400-$12,000/project, $18-$90/sqft (national), "
            "$50-$150/sqft (CA/Bay Area premium). Our avg job ($1,713) is well BELOW "
            "market avg ($5,000+) — likely doing small panel replacements, not full "
            "storefront systems. Only 3 HCP jobs — extremely low confidence. "
            "Big opportunity: full storefront system bids ($5K-$15K range)."
        ),
    },

    "laminated": {
        "label": "Laminated Safety Glass Replacement",
        "market_avg_sqft": 110,     # $/sqft — LA installed (material + labor)
        "market_low_sqft": 70,      # thin laminate (6.38mm), basic install
        "market_high_sqft": 180,    # thick laminate, security grade, framing work
        "our_avg_sqft": 140,        # Fast Glass HCP avg (8 jobs)
        "our_avg_job": 1617,
        "our_min_job": 722,
        "our_max_job": 3000,
        "job_count": 8,             # low sample
        "vs_market": "+27%",
        "sources": [
            "Landmark Construction LA ($9-$15/sqft material only)",
            "DesignTransitionStudio safety glass guide 2026",
            "LatestCost safety glass 2026",
            "HCP historical (n=8, low confidence)",
        ],
        "note": (
            "Laminated glass material (LA): $9-$15/sqft (Landmark LA). "
            "Installed total: ~$70-$180/sqft depending on thickness and framing. "
            "Our $139.5/sqft is 27% above market avg — consistent with "
            "premium/security-grade work. Typical applications: skylights, "
            "floor glass, hurricane-rated, security glazing."
        ),
    },
}


# ── Quick reference: confidence levels ──────────────────────────────────────
CONFIDENCE = {
    "single_pane":           "HIGH   (78 jobs)",
    "double_pane_igu":       "HIGH   (223 jobs)",
    "shower_door":           "LOW    (6 jobs — treat as directional only)",
    "mirror":                "LOW    (9 jobs — treat as directional only)",
    "commercial_storefront": "VERY LOW (3 jobs — placeholder only)",
    "laminated":             "LOW    (8 jobs — treat as directional only)",
}


# ── Competitive snapshot ─────────────────────────────────────────────────────
# Category            | Market avg | Our avg | Delta   | Assessment
# single_pane         |  $82/sqft  | $125/sqft| +52%   | Premium or complex jobs
# double_pane_igu     | $105/sqft  | $116/sqft| +11%   | ✅ Solid market position
# shower_door         | $130/sqft  | $161/sqft| +24%   | ⚠️ Avg job below market
# mirror              |  $65/sqft  | $125/sqft| +92%   | Likely specialty/custom
# commercial_storefront| $80/sqft  |  $93/sqft| +16%   | ⚠️ Jobs too small vs market
# laminated           | $110/sqft  | $140/sqft| +27%   | Premium positioning ✅
