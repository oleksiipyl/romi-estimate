"""
ROMI Estimate — Product Definitions
Based on Victor's supplier research and glazing expertise.
Structure: 4 categories → 12 scenarios → fast selection
"""

PRODUCTS = {

    # ─────────────────────────────────────────────────────
    # 🏠 RESIDENTIAL
    # ─────────────────────────────────────────────────────

    "residential_single": {
        "id": "residential_single",
        "category": "residential",
        "category_label": "🏠 Residential",
        "label": "Single Pane Replacement",
        "description": "One piece of glass, no spacer",
        "supplier": "Western States Glass",
        "price_per_sqft_min": 18,
        "price_per_sqft_max": 45,
        "min_charge": 150,
        "fields": [
            {
                "id": "frame_type",
                "label": "Frame Type",
                "type": "radio",
                "default": "wood",
                "options": [
                    {"value": "wood",     "label": "Wood",     "labor_add": 15},
                    {"value": "aluminum", "label": "Aluminum", "labor_add": 0},
                    {"value": "steel",    "label": "Steel",    "labor_add": 35},
                    {"value": "vinyl",    "label": "Vinyl",    "labor_add": 0},
                ]
            },
            {
                "id": "glass_type",
                "label": "Glass Type",
                "type": "radio",
                "default": "clear",
                "options": [
                    {"value": "clear",       "label": "Clear",           "price_add_sqft": 0},
                    {"value": "bronze",      "label": "Bronze Tint",     "price_add_sqft": 3},
                    {"value": "gray",        "label": "Gray Tint",       "price_add_sqft": 3},
                    {"value": "dark_gray",   "label": "Dark Gray",       "price_add_sqft": 4},
                    {"value": "rain",        "label": "Rain (Privacy)",  "price_add_sqft": 5},
                    {"value": "acid_etch",   "label": "Acid Etch (Satin)","price_add_sqft": 8},
                    {"value": "reeded",      "label": "Reeded",          "price_add_sqft": 5},
                ]
            },
            {
                "id": "thickness",
                "label": "Thickness",
                "type": "radio",
                "default": "1/8",
                "options": [
                    {"value": "3/32", "label": "3/32\"", "price_add_sqft": -2},
                    {"value": "1/8",  "label": "1/8\"",  "price_add_sqft": 0},
                    {"value": "3/16", "label": "3/16\"", "price_add_sqft": 2},
                    {"value": "1/4",  "label": "1/4\"",  "price_add_sqft": 4},
                    {"value": "3/8",  "label": "3/8\"",  "price_add_sqft": 8},
                    {"value": "1/2",  "label": "1/2\"",  "price_add_sqft": 14},
                ]
            },
            {
                "id": "heat_treatment",
                "label": "Heat Treatment",
                "type": "radio",
                "default": "annealed",
                "note": "Required by code: doors, sidelights, bathrooms, near floor",
                "options": [
                    {"value": "annealed", "label": "Annealed", "price_add_sqft": 0},
                    {"value": "tempered", "label": "Tempered", "price_add_sqft": 15},
                ]
            },
        ]
    },

    "residential_igu": {
        "id": "residential_igu",
        "category": "residential",
        "category_label": "🏠 Residential",
        "label": "Double Pane IGU",
        "description": "Two panes + spacer, full unit replacement",
        "supplier": "Western States Glass",
        "price_per_sqft_min": 28,
        "price_per_sqft_max": 75,
        "min_charge": 200,
        "fields": [
            {
                "id": "igu_package",
                "label": "Glass Package",
                "type": "radio",
                "default": "clear_clear",
                "options": [
                    {"value": "clear_clear",    "label": "Clear / Clear (standard)",        "price_add_sqft": 0},
                    {"value": "clear_lowe",     "label": "Clear / Low-E Advantage",         "price_add_sqft": 8},
                    {"value": "clear_solarban", "label": "Clear / Solarban 70",             "price_add_sqft": 12},
                    {"value": "tinted_clear",   "label": "Tinted Outer / Clear",            "price_add_sqft": 5},
                ]
            },
            {
                "id": "tint_color",
                "label": "Tint Color",
                "type": "radio",
                "default": "bronze",
                "show_if": {"field": "igu_package", "value": "tinted_clear"},
                "options": [
                    {"value": "bronze", "label": "Bronze", "price_add_sqft": 0},
                    {"value": "gray",   "label": "Gray",   "price_add_sqft": 0},
                ]
            },
            {
                "id": "heat_treatment",
                "label": "Heat Treatment",
                "type": "radio",
                "default": "annealed",
                "options": [
                    {"value": "annealed", "label": "Annealed (standard)", "price_add_sqft": 0},
                    {"value": "tempered", "label": "Tempered both panes", "price_add_sqft": 18},
                ]
            },
            {
                "id": "spacer",
                "label": "Spacer Color",
                "type": "radio",
                "default": "silver",
                "options": [
                    {"value": "silver",     "label": "Silver (standard)", "price_add_sqft": 0},
                    {"value": "bronze",     "label": "Bronze",            "price_add_sqft": 2},
                    {"value": "black",      "label": "Black",             "price_add_sqft": 2},
                    {"value": "warm_edge",  "label": "Warm Edge (TGI)",   "price_add_sqft": 3},
                ]
            },
            {
                "id": "gas_fill",
                "label": "Gas Fill",
                "type": "radio",
                "default": "air",
                "options": [
                    {"value": "air",    "label": "Air (standard)", "price_add_sqft": 0},
                    {"value": "argon",  "label": "Argon",          "price_add_sqft": 3},
                ]
            },
            {
                "id": "grids",
                "label": "Grids",
                "type": "radio",
                "default": "none",
                "options": [
                    {"value": "none",  "label": "No Grids",                          "price_add_unit": 0},
                    {"value": "flat",  "label": "Flat Grids (inside unit)",           "price_add_unit": 45},
                    {"value": "sdl",   "label": "SDL — Simulated Divided Lights",    "price_add_unit": 55},
                    {"value": "gbg",   "label": "GBG — Grilles Between Glass",       "price_add_unit": 65},
                ]
            },
        ]
    },

    "residential_foggy": {
        "id": "residential_foggy",
        "category": "residential",
        "category_label": "🏠 Residential",
        "label": "Foggy IGU (seal failed)",
        "description": "Cloudy glass, frame stays — unit only",
        "supplier": "Western States Glass",
        "price_per_sqft_min": 28,
        "price_per_sqft_max": 65,
        "min_charge": 180,
        "note": "Replacing sealed unit only. Frame stays.",
        "fields": [
            {
                "id": "igu_package",
                "label": "Replace With",
                "type": "radio",
                "default": "clear_clear",
                "options": [
                    {"value": "clear_clear",    "label": "Clear / Clear (match original)", "price_add_sqft": 0},
                    {"value": "clear_lowe",     "label": "Clear / Low-E (upgrade)",        "price_add_sqft": 8},
                    {"value": "clear_solarban", "label": "Clear / Solarban 70 (upgrade)",  "price_add_sqft": 12},
                ]
            },
            {
                "id": "frame_material",
                "label": "Frame Material",
                "type": "radio",
                "default": "vinyl",
                "options": [
                    {"value": "vinyl",    "label": "Vinyl / Aluminum (snap-in)", "labor_add": 0},
                    {"value": "wood",     "label": "Wood (glazed in)",           "labor_add": 25},
                ]
            },
        ]
    },

    # ─────────────────────────────────────────────────────
    # 🏢 COMMERCIAL
    # ─────────────────────────────────────────────────────

    "commercial_storefront": {
        "id": "commercial_storefront",
        "category": "commercial",
        "category_label": "🏢 Commercial",
        "label": "Storefront Glass",
        "description": "Aluminum storefront system glass",
        "supplier": "Western States Glass",
        "price_per_sqft_min": 50,
        "price_per_sqft_max": 120,
        "min_charge": 400,
        "fields": [
            {
                "id": "system_type",
                "label": "System Type",
                "type": "radio",
                "default": "single_tempered",
                "options": [
                    {"value": "single_tempered", "label": "Single Pane Tempered",     "price_add_sqft": 0},
                    {"value": "igu_storefront",  "label": "IGU (energy efficient)",    "price_add_sqft": 20},
                ]
            },
            {
                "id": "glass_type",
                "label": "Glass Type",
                "type": "radio",
                "default": "clear_tempered",
                "options": [
                    {"value": "clear_tempered",  "label": "Clear Tempered",          "price_add_sqft": 0},
                    {"value": "bronze_tempered", "label": "Bronze Tint Tempered",    "price_add_sqft": 5},
                    {"value": "gray_tempered",   "label": "Gray Tint Tempered",      "price_add_sqft": 5},
                    {"value": "reflective_gray", "label": "Solar Cool Gray Reflective","price_add_sqft": 12},
                    {"value": "reflective_bronze","label": "Solar Cool Bronze Reflective","price_add_sqft": 12},
                ]
            },
            {
                "id": "thickness",
                "label": "Thickness",
                "type": "radio",
                "default": "1/4",
                "options": [
                    {"value": "1/4", "label": "1/4\" (standard)", "price_add_sqft": 0},
                    {"value": "3/8", "label": "3/8\"",             "price_add_sqft": 8},
                    {"value": "1/2", "label": "1/2\"",             "price_add_sqft": 18},
                ]
            },
        ]
    },

    "commercial_partition": {
        "id": "commercial_partition",
        "category": "commercial",
        "category_label": "🏢 Commercial",
        "label": "Office Partition Glass",
        "description": "Interior glass walls, conference rooms",
        "supplier": "Western States Glass",
        "price_per_sqft_min": 45,
        "price_per_sqft_max": 95,
        "min_charge": 350,
        "fields": [
            {
                "id": "glass_type",
                "label": "Glass Type",
                "type": "radio",
                "default": "clear_tempered",
                "options": [
                    {"value": "clear_tempered",  "label": "Clear Tempered",           "price_add_sqft": 0},
                    {"value": "acid_etch",        "label": "Acid Etch (Privacy)",      "price_add_sqft": 8},
                    {"value": "low_iron",         "label": "Low Iron / Starphire",     "price_add_sqft": 10},
                    {"value": "tinted",           "label": "Tinted",                   "price_add_sqft": 4},
                ]
            },
            {
                "id": "thickness",
                "label": "Thickness",
                "type": "radio",
                "default": "3/8",
                "options": [
                    {"value": "1/4", "label": "1/4\"",             "price_add_sqft": -4},
                    {"value": "3/8", "label": "3/8\" (standard)",  "price_add_sqft": 0},
                    {"value": "1/2", "label": "1/2\"",             "price_add_sqft": 8},
                ]
            },
        ]
    },

    "commercial_door": {
        "id": "commercial_door",
        "category": "commercial",
        "category_label": "🏢 Commercial",
        "label": "Commercial Door Glass",
        "description": "Glass panel in commercial door",
        "supplier": "Western States Glass",
        "price_per_sqft_min": 60,
        "price_per_sqft_max": 130,
        "min_charge": 300,
        "fields": [
            {
                "id": "door_type",
                "label": "Door Type",
                "type": "radio",
                "default": "aluminum",
                "options": [
                    {"value": "aluminum",     "label": "Aluminum storefront door",  "labor_add": 0},
                    {"value": "hollow_metal", "label": "Hollow metal door",         "labor_add": 30},
                    {"value": "wood",         "label": "Wood door",                 "labor_add": 20},
                ]
            },
            {
                "id": "glass_type",
                "label": "Glass Type",
                "type": "radio",
                "default": "clear_tempered",
                "options": [
                    {"value": "clear_tempered",  "label": "Clear Tempered 1/4\"",  "price_add_sqft": 0},
                    {"value": "clear_3_8",       "label": "Clear Tempered 3/8\"",  "price_add_sqft": 8},
                    {"value": "wired",           "label": "Wired Glass (fire rated)","price_add_sqft": 15},
                    {"value": "firelite",        "label": "FireLite (clear fire)",  "price_add_sqft": 30},
                ]
            },
        ]
    },

    # ─────────────────────────────────────────────────────
    # 🚿 SHOWER & BATH
    # ─────────────────────────────────────────────────────

    "shower_door": {
        "id": "shower_door",
        "category": "shower",
        "category_label": "🚿 Shower & Bath",
        "label": "Shower Door",
        "description": "Frameless or semi-frameless shower door",
        "supplier": "Western States Glass + Liberty",
        "price_per_sqft_min": 85,
        "price_per_sqft_max": 180,
        "min_charge": 600,
        "fields": [
            {
                "id": "door_style",
                "label": "Style",
                "type": "radio",
                "default": "frameless_swing",
                "options": [
                    {"value": "frameless_swing",  "label": "Frameless — Swing Door",    "price_add_unit": 0},
                    {"value": "frameless_sliding","label": "Frameless — Sliding Bypass","price_add_unit": 150},
                    {"value": "semi_frameless",   "label": "Semi-Frameless",            "price_add_unit": -100},
                    {"value": "framed",           "label": "Framed (aluminum)",         "price_add_unit": -200},
                ]
            },
            {
                "id": "glass_type",
                "label": "Glass",
                "type": "radio",
                "default": "clear",
                "options": [
                    {"value": "clear",       "label": "Clear Tempered",              "price_add_sqft": 0},
                    {"value": "low_iron",    "label": "Low Iron (ultra clear)",      "price_add_sqft": 12},
                    {"value": "rain",        "label": "Rain Pattern (privacy)",      "price_add_sqft": 8},
                    {"value": "acid_etch",   "label": "Acid Etch (satin/frosted)",   "price_add_sqft": 10},
                    {"value": "spraylite",   "label": "SprayLite Pattern",           "price_add_sqft": 8},
                ]
            },
            {
                "id": "thickness",
                "label": "Glass Thickness",
                "type": "radio",
                "default": "1/2",
                "options": [
                    {"value": "3/8", "label": "3/8\" (semi-frameless)",  "price_add_sqft": -8},
                    {"value": "1/2", "label": "1/2\" (frameless standard)","price_add_sqft": 0},
                ]
            },
            {
                "id": "hardware_finish",
                "label": "Hardware Finish",
                "type": "radio",
                "default": "chrome",
                "options": [
                    {"value": "chrome",          "label": "Chrome",          "price_add_unit": 0},
                    {"value": "brushed_nickel",  "label": "Brushed Nickel",  "price_add_unit": 50},
                    {"value": "matte_black",     "label": "Matte Black",     "price_add_unit": 75},
                    {"value": "orb",             "label": "Oil Rubbed Bronze","price_add_unit": 75},
                    {"value": "gold",            "label": "Polished Gold",   "price_add_unit": 150},
                ]
            },
            {
                "id": "coating",
                "label": "Glass Coating",
                "type": "checkbox",
                "options": [
                    {"value": "clearshield", "label": "ClearShield water repellent", "price_add_unit": 150},
                ]
            },
        ]
    },

    "shower_mirror": {
        "id": "shower_mirror",
        "category": "shower",
        "category_label": "🚿 Shower & Bath",
        "label": "Bathroom Mirror",
        "description": "Custom cut mirror installation",
        "supplier": "Western States Glass",
        "price_per_sqft_min": 35,
        "price_per_sqft_max": 75,
        "min_charge": 200,
        "fields": [
            {
                "id": "mirror_type",
                "label": "Mirror Type",
                "type": "radio",
                "default": "standard",
                "options": [
                    {"value": "standard",     "label": "Standard Silver",             "price_add_sqft": 0},
                    {"value": "low_copper",   "label": "Low Copper (moisture resist)","price_add_sqft": 5},
                    {"value": "antique",      "label": "Antique Mirror",              "price_add_sqft": 15},
                ]
            },
            {
                "id": "thickness",
                "label": "Thickness",
                "type": "radio",
                "default": "1/8",
                "options": [
                    {"value": "1/8",  "label": "1/8\" (standard wall mirror)",  "price_add_sqft": 0},
                    {"value": "3/16", "label": "3/16\"",                         "price_add_sqft": 3},
                    {"value": "1/4",  "label": "1/4\" (large/frameless)",        "price_add_sqft": 6},
                ]
            },
            {
                "id": "edge",
                "label": "Edge Finish",
                "type": "radio",
                "default": "polished",
                "options": [
                    {"value": "seamed",   "label": "Seamed (clean edge)",    "price_add_lf": 0},
                    {"value": "polished", "label": "Flat Polished",           "price_add_lf": 8},
                    {"value": "beveled",  "label": "Beveled 1\" (decorative)","price_add_lf": 15},
                ]
            },
        ]
    },

    # ─────────────────────────────────────────────────────
    # ✨ SPECIALTY
    # ─────────────────────────────────────────────────────

    "specialty_tabletop": {
        "id": "specialty_tabletop",
        "category": "specialty",
        "category_label": "✨ Specialty",
        "label": "Table Top Glass",
        "description": "Tempered glass for tables and furniture",
        "supplier": "Western States Glass",
        "price_per_sqft_min": 45,
        "price_per_sqft_max": 90,
        "min_charge": 180,
        "note": "Always tempered for safety",
        "fields": [
            {
                "id": "glass_type",
                "label": "Glass Type",
                "type": "radio",
                "default": "clear",
                "options": [
                    {"value": "clear",     "label": "Clear Tempered",           "price_add_sqft": 0},
                    {"value": "low_iron",  "label": "Low Iron / Starphire",     "price_add_sqft": 10},
                    {"value": "bronze",    "label": "Bronze Tint Tempered",     "price_add_sqft": 5},
                    {"value": "gray",      "label": "Gray Tint Tempered",       "price_add_sqft": 5},
                ]
            },
            {
                "id": "thickness",
                "label": "Thickness",
                "type": "radio",
                "default": "3/8",
                "options": [
                    {"value": "1/4", "label": "1/4\" (light tables)",    "price_add_sqft": -6},
                    {"value": "3/8", "label": "3/8\" (standard)",        "price_add_sqft": 0},
                    {"value": "1/2", "label": "1/2\" (heavy duty)",      "price_add_sqft": 8},
                ]
            },
            {
                "id": "edge",
                "label": "Edge Finish",
                "type": "radio",
                "default": "polished",
                "options": [
                    {"value": "polished", "label": "Flat Polished (standard)", "price_add_lf": 8},
                    {"value": "pencil",   "label": "Pencil Polish (rounded)",  "price_add_lf": 10},
                    {"value": "beveled",  "label": "Beveled 1\"",              "price_add_lf": 15},
                ]
            },
            {
                "id": "corners",
                "label": "Corners",
                "type": "radio",
                "default": "square",
                "options": [
                    {"value": "square",  "label": "Square",               "price_add_unit": 0},
                    {"value": "clipped", "label": "Clipped (+$10/corner)","price_add_unit": 40},
                    {"value": "radius",  "label": "Radius (+$15/corner)", "price_add_unit": 60},
                ]
            },
        ]
    },

    "specialty_custom": {
        "id": "specialty_custom",
        "category": "specialty",
        "category_label": "✨ Specialty",
        "label": "Custom Tempered Glass",
        "description": "Railings, balconies, custom shapes",
        "supplier": "Western States Glass",
        "price_per_sqft_min": 55,
        "price_per_sqft_max": 110,
        "min_charge": 250,
        "fields": [
            {
                "id": "application",
                "label": "Application",
                "type": "radio",
                "default": "railing",
                "options": [
                    {"value": "railing",    "label": "Railing / Balcony",     "labor_add": 0},
                    {"value": "canopy",     "label": "Glass Canopy",          "labor_add": 100},
                    {"value": "floor",      "label": "Glass Floor Panel",     "labor_add": 150},
                    {"value": "window",     "label": "Custom Window / Door",  "labor_add": 0},
                    {"value": "other",      "label": "Other",                 "labor_add": 0},
                ]
            },
            {
                "id": "glass_type",
                "label": "Glass",
                "type": "radio",
                "default": "clear",
                "options": [
                    {"value": "clear",    "label": "Clear Tempered",     "price_add_sqft": 0},
                    {"value": "low_iron", "label": "Low Iron / Starphire","price_add_sqft": 10},
                    {"value": "tinted",   "label": "Tinted",             "price_add_sqft": 5},
                    {"value": "acid_etch","label": "Acid Etch",          "price_add_sqft": 8},
                ]
            },
            {
                "id": "thickness",
                "label": "Thickness",
                "type": "radio",
                "default": "3/8",
                "options": [
                    {"value": "1/4", "label": "1/4\"",            "price_add_sqft": -4},
                    {"value": "3/8", "label": "3/8\" (standard)", "price_add_sqft": 0},
                    {"value": "1/2", "label": "1/2\"",            "price_add_sqft": 8},
                    {"value": "3/4", "label": "3/4\" (structural)","price_add_sqft": 20},
                ]
            },
        ]
    },

    "specialty_laminated": {
        "id": "specialty_laminated",
        "category": "specialty",
        "category_label": "✨ Specialty",
        "label": "Laminated Safety Glass",
        "description": "Safety + sound reduction, PVB interlayer",
        "supplier": "Western States Glass",
        "price_per_sqft_min": 40,
        "price_per_sqft_max": 85,
        "min_charge": 250,
        "fields": [
            {
                "id": "construction",
                "label": "Construction",
                "type": "radio",
                "default": "1/4_lam",
                "options": [
                    {"value": "1/4_lam", "label": "1/4\" Laminated (1/8+PVB+1/8)",   "price_add_sqft": 0},
                    {"value": "3/8_lam", "label": "3/8\" Laminated (3/16+PVB+3/16)", "price_add_sqft": 8},
                    {"value": "1/2_lam", "label": "1/2\" Laminated (1/4+PVB+1/4)",   "price_add_sqft": 15},
                ]
            },
            {
                "id": "interlayer",
                "label": "Interlayer",
                "type": "radio",
                "default": "standard",
                "options": [
                    {"value": "standard",  "label": "Standard PVB (clear)",     "price_add_sqft": 0},
                    {"value": "acoustic",  "label": "Acoustic PVB (sound)",     "price_add_sqft": 10},
                    {"value": "lowe_film", "label": "Low-E Interlayer (energy)","price_add_sqft": 12},
                    {"value": "tinted",    "label": "Tinted PVB (Bronze/Gray)", "price_add_sqft": 8},
                ]
            },
        ]
    },
}


def get_product(product_id: str) -> dict:
    return PRODUCTS.get(product_id)


def get_products_by_category() -> dict:
    """Returns products grouped by category"""
    result = {}
    for pid, product in PRODUCTS.items():
        cat = product["category"]
        if cat not in result:
            result[cat] = []
        result[cat].append({
            "id": pid,
            "label": product["label"],
            "description": product["description"],
            "price_per_sqft_min": product["price_per_sqft_min"],
            "price_per_sqft_max": product["price_per_sqft_max"],
        })
    return result


CATEGORY_META = {
    "residential": {"label": "🏠 Residential", "order": 1},
    "commercial":  {"label": "🏢 Commercial",   "order": 2},
    "shower":      {"label": "🚿 Shower & Bath", "order": 3},
    "specialty":   {"label": "✨ Specialty",     "order": 4},
}

# Hardware products — real prices from Alex 2026-06-11
HARDWARE_PRODUCTS = [
    {"id": "hw_operator",   "label": "Window Operator / Crank",   "description": "Casement/awning crank replacement",  "service_id": 60, "price_min": 350, "price_max": 450},
    {"id": "hw_balance",    "label": "Window Balance (spiral)",    "description": "Spiral balance replacement",          "service_id": 61, "price_min": 350, "price_max": 450},
    {"id": "hw_column_bal", "label": "Window Balance (column)",    "description": "Column balancer vinyl windows",        "service_id": 71, "price_min": 350, "price_max": 450},
    {"id": "hw_roller",     "label": "Window Rollers (bottom)",    "description": "Bottom rollers sliding windows",       "service_id": 70, "price_min": 350, "price_max": 450},
    {"id": "hw_track",      "label": "Sliding Door Track",         "description": "Rollers + track repair/replace",       "service_id": 67, "price_min": 650, "price_max": 850},
    {"id": "hw_lock",       "label": "Window Lock / Latch",        "description": "Sash lock, cam lock, keyed lock",      "service_id": 66, "price_min": 70,  "price_max": 150},
    {"id": "hw_hardware",   "label": "Window Hardware Repair",     "description": "Handles, hinges, general hardware",    "service_id": 62, "price_min": 70,  "price_max": 150},
    {"id": "hw_casement",   "label": "Casement Adjustment",        "description": "Sagging/misaligned sash fix",          "service_id": 69, "price_min": 150, "price_max": 250},
    {"id": "hw_screen_new", "label": "Screen Replacement",         "description": "New fiberglass/aluminum mesh screen",  "service_id": 63, "price_min": 45,  "price_max": 85},
    {"id": "hw_screen_fix", "label": "Screen Re-screen",           "description": "Re-screen existing frame",             "service_id": 64, "price_min": 25,  "price_max": 55},
    {"id": "hw_reglaze",    "label": "Window Reglazing",           "description": "Re-putty glass in wood frame",         "service_id": 65, "price_min": 45,  "price_max": 85},
    {"id": "hw_weather",    "label": "Weatherstripping",           "description": "Seal gaps, draft stoppers",            "service_id": 68, "price_min": 35,  "price_max": 75},
]

# Update CATEGORY_META with hardware
CATEGORY_META["hardware"] = {"label": "🔧 Hardware", "order": 5}
