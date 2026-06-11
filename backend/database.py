"""
ROMI Estimate — Database setup and seeding
SQLite database with all 51 services from price list
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "estimate.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    # Services table
    c.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit TEXT DEFAULT 'per sq ft',
            material_min REAL NOT NULL,
            material_max REAL NOT NULL,
            labor_min REAL NOT NULL,
            labor_max REAL NOT NULL,
            price_min REAL NOT NULL,
            price_max REAL NOT NULL,
            margin REAL DEFAULT 0.60,
            notes TEXT,
            enabled INTEGER DEFAULT 1
        )
    """)

    # ZIP codes multipliers table
    c.execute("""
        CREATE TABLE IF NOT EXISTS zip_multipliers (
            zip_code TEXT PRIMARY KEY,
            city TEXT,
            multiplier REAL DEFAULT 1.0,
            travel_minutes INTEGER DEFAULT 30
        )
    """)

    # Settings table
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            description TEXT
        )
    """)

    # Modifiers table (extra work)
    c.execute("""
        CREATE TABLE IF NOT EXISTS modifiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price_type TEXT DEFAULT 'fixed',
            price REAL NOT NULL,
            enabled INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


def seed_services():
    """Seed all 51 services from price_list_extended.py"""
    conn = get_db()
    c = conn.cursor()

    # Check if already seeded
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    services = [
        # RESIDENTIAL
        (1, "Single Pane Glass Replacement", "Residential", "per sq ft", 3, 5, 15, 20, 18, 25, 0.65, "Standard installation"),
        (2, "Double Pane (IGU) Glass Replacement", "Residential", "per sq ft", 8, 12, 20, 25, 28, 37, 0.60, "Energy efficient"),
        (3, "Tempered Glass", "Residential", "per sq ft", 12, 20, 25, 35, 40, 60, 0.60, "Safety glass"),
        (4, "Low-E Insulated Glass", "Residential", "per sq ft", 20, 35, 25, 35, 50, 75, 0.58, "Energy saving coating"),
        (5, "Solarban 70 Glass", "Residential", "per sq ft", 25, 40, 25, 35, 55, 85, 0.58, "Solar control glass"),
        (6, "Laminated Safety Glass", "Residential", "per sq ft", 15, 25, 20, 30, 40, 65, 0.58, "Interlayer protection"),
        (7, "Obscure/Frosted Glass", "Residential", "per sq ft", 8, 15, 15, 25, 28, 48, 0.60, "Privacy glass"),
        (8, "Tinted Glass", "Residential", "per sq ft", 8, 14, 15, 22, 27, 45, 0.60, "UV protection"),
        (9, "Plate Glass (Large)", "Residential", "per sq ft", 6, 10, 18, 28, 28, 45, 0.60, "Large panels"),
        (10, "Sliding Door Glass Replacement", "Residential", "per unit", 150, 300, 100, 200, 350, 650, 0.55, "Patio/sliding doors"),
        (11, "Window Screen Replacement", "Residential", "per unit", 15, 30, 20, 35, 45, 75, 0.65, "Fiberglass or aluminum"),
        (12, "Window Reglazing", "Residential", "per sq ft", 2, 4, 10, 18, 15, 28, 0.70, "Rebed existing glass"),
        (13, "Foggy/Cloudy IGU Replacement", "Residential", "per unit", 80, 150, 50, 100, 160, 300, 0.55, "Failed seal replacement"),
        (14, "Broken Window Emergency", "Residential", "per sq ft", 5, 10, 25, 40, 45, 80, 0.60, "Emergency service"),
        (15, "Picture Window Glass", "Residential", "per sq ft", 5, 9, 18, 28, 28, 45, 0.60, "Fixed large windows"),
        (16, "Bay Window Glass", "Residential", "per unit", 200, 400, 150, 300, 450, 850, 0.55, "Multi-panel bay"),

        # COMMERCIAL
        (17, "Storefront Glass Replacement", "Commercial", "per sq ft", 15, 25, 25, 40, 50, 85, 0.55, "Commercial entry"),
        (18, "Commercial Tempered Glass", "Commercial", "per sq ft", 18, 30, 30, 45, 60, 100, 0.55, "Safety requirement"),
        (19, "Office Partition Glass", "Commercial", "per sq ft", 20, 35, 30, 50, 65, 110, 0.55, "Interior partitions"),
        (20, "Curtain Wall Glass", "Commercial", "per sq ft", 40, 80, 50, 100, 120, 250, 0.50, "Building facade"),
        (21, "Spandrel Glass", "Commercial", "per sq ft", 25, 45, 30, 50, 70, 130, 0.52, "Non-vision areas"),
        (22, "Emergency Board-Up", "Commercial", "per sq ft", 2, 4, 15, 25, 25, 50, 0.70, "Temporary protection"),
        (23, "Commercial Door Glass", "Commercial", "per unit", 200, 500, 100, 250, 400, 900, 0.55, "Entry door glass"),
        (24, "Glass Canopy/Awning", "Commercial", "per sq ft", 35, 65, 40, 70, 100, 200, 0.50, "Structural glass"),
        (25, "Bullet Resistant Glass", "Commercial", "per sq ft", 100, 300, 80, 150, 250, 600, 0.45, "Security glass"),
        (26, "Anti-Graffiti Film + Glass", "Commercial", "per sq ft", 15, 30, 15, 25, 40, 75, 0.60, "Protective coating"),
        (27, "Skylights Glass", "Commercial", "per sq ft", 30, 60, 40, 80, 100, 200, 0.50, "Overhead glazing"),

        # WINDOW TINT
        (28, "Residential Solar Tint", "Window Tint", "per sq ft", 2, 4, 6, 10, 8, 18, 0.70, "Heat/UV reduction"),
        (29, "Commercial Solar Tint", "Window Tint", "per sq ft", 3, 5, 8, 12, 12, 22, 0.68, "Energy savings"),
        (30, "Decorative/Frosted Film", "Window Tint", "per sq ft", 3, 6, 6, 10, 10, 20, 0.68, "Privacy film"),
        (31, "Safety/Security Film", "Window Tint", "per sq ft", 5, 10, 8, 14, 15, 30, 0.65, "Shatter protection"),
        (32, "Ceramic Tint (Residential)", "Window Tint", "per sq ft", 6, 10, 8, 12, 18, 30, 0.65, "Premium heat block"),
        (33, "Ceramic Tint (Commercial)", "Window Tint", "per sq ft", 8, 14, 10, 16, 22, 38, 0.62, "Commercial grade"),
        (34, "One-Way Mirror Film", "Window Tint", "per sq ft", 5, 9, 7, 12, 14, 26, 0.65, "Privacy daytime"),
        (35, "Anti-Graffiti Film", "Window Tint", "per sq ft", 8, 15, 8, 14, 18, 35, 0.65, "Sacrificial layer"),
        (36, "Blackout Film", "Window Tint", "per sq ft", 3, 6, 6, 10, 10, 20, 0.68, "Complete blackout"),

        # AUTO GLASS
        (37, "Windshield Replacement", "Auto Glass", "per unit", 150, 400, 80, 150, 280, 650, 0.55, "OEM or aftermarket"),
        (38, "Side Window Replacement", "Auto Glass", "per unit", 80, 200, 60, 100, 170, 380, 0.58, "Door glass"),
        (39, "Rear Window Replacement", "Auto Glass", "per unit", 120, 350, 80, 150, 240, 600, 0.55, "Heated or standard"),
        (40, "Windshield Chip Repair", "Auto Glass", "per chip", 5, 10, 30, 50, 45, 75, 0.75, "Resin injection"),
        (41, "Sunroof Glass Replacement", "Auto Glass", "per unit", 200, 500, 100, 200, 380, 850, 0.52, "Panoramic or standard"),
        (42, "Classic Car Glass", "Auto Glass", "per unit", 200, 600, 100, 250, 400, 1000, 0.50, "Custom cut"),
        (43, "Fleet Vehicle Glass", "Auto Glass", "per unit", 100, 300, 60, 120, 200, 550, 0.55, "Volume pricing"),
        (44, "ADAS Recalibration", "Auto Glass", "per service", 50, 100, 100, 200, 200, 400, 0.60, "Camera calibration"),
        (45, "Mobile Auto Glass", "Auto Glass", "per service", 0, 0, 50, 100, 75, 150, 0.80, "On-site service fee"),

        # SPECIALTY
        (46, "Structural Glass Floors", "Specialty", "per sq ft", 150, 300, 100, 200, 300, 600, 0.45, "Walk-on glass"),
        (47, "Frameless Glass Railings", "Specialty", "per linear ft", 100, 200, 80, 150, 220, 450, 0.48, "Balcony/stair"),
        (48, "Custom Decorative Glass", "Specialty", "per sq ft", 50, 150, 50, 100, 120, 340, 0.50, "Art/pattern glass"),

        # SHOWER/MIRROR
        (49, "Shower Door/Enclosure", "Shower & Mirror", "per unit", 300, 600, 200, 400, 40, 90, 0.50, "Frameless or framed"),
        (50, "Custom Mirror", "Shower & Mirror", "per sq ft", 15, 30, 20, 40, 33, 83, 0.55, "Cut and install"),

        # ADD-ON
        (51, "Tempered Glass Upgrade", "Add-on", "per sq ft", 8, 15, 5, 10, 15, 30, 0.60, "Upgrade to tempered"),
    ]

    c.executemany("""
        INSERT INTO services 
        (id, name, category, unit, material_min, material_max, 
         labor_min, labor_max, price_min, price_max, margin, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, services)

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(services)} services")


def seed_zip_multipliers():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM zip_multipliers")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    # Base: Northridge (91324) = 0 minutes travel
    zips = [
        # HIGH INCOME (1.25-1.35x)
        ("90210", "Beverly Hills", 1.35, 45),
        ("90272", "Pacific Palisades", 1.30, 50),
        ("90077", "Bel Air", 1.35, 50),
        ("90049", "Brentwood", 1.30, 45),
        ("90402", "Santa Monica", 1.25, 50),
        ("91011", "La Cañada Flintridge", 1.25, 40),
        ("91108", "San Marino", 1.25, 55),
        ("90274", "Palos Verdes Estates", 1.25, 70),

        # MEDIUM-HIGH (1.10-1.20x)
        ("90025", "West Los Angeles", 1.15, 45),
        ("90064", "Rancho Park", 1.15, 45),
        ("90024", "Westwood", 1.20, 45),
        ("90034", "Palms", 1.10, 45),
        ("91364", "Woodland Hills", 1.10, 15),
        ("91356", "Tarzana", 1.10, 20),
        ("91403", "Sherman Oaks", 1.10, 20),
        ("91604", "Studio City", 1.10, 25),
        ("91602", "North Hollywood", 1.05, 25),

        # BASE AREA (1.0x) — near Northridge
        ("91324", "Northridge", 1.00, 0),
        ("91325", "Northridge", 1.00, 5),
        ("91326", "Porter Ranch", 1.05, 10),
        ("91330", "Northridge (CSUN)", 1.00, 5),
        ("91344", "Granada Hills", 1.00, 10),
        ("91343", "North Hills", 1.00, 10),
        ("91345", "Mission Hills", 1.00, 10),
        ("91340", "San Fernando", 1.00, 15),
        ("91352", "Sun Valley", 1.00, 20),
        ("91606", "North Hollywood", 1.00, 25),

        # DISTANT (1.0x but travel cost applies)
        ("90001", "South Central", 1.00, 60),
        ("90011", "South Central", 1.00, 60),
        ("90019", "Mid-City", 1.05, 50),
        ("90028", "Hollywood", 1.10, 40),
        ("90038", "Hollywood", 1.10, 40),
        ("91214", "La Crescenta", 1.05, 40),
        ("91030", "South Pasadena", 1.10, 55),
        ("91101", "Pasadena", 1.10, 55),
        ("90731", "San Pedro", 1.00, 75),
        ("90802", "Long Beach", 1.00, 70),
    ]

    c.executemany("""
        INSERT INTO zip_multipliers (zip_code, city, multiplier, travel_minutes)
        VALUES (?,?,?,?)
    """, zips)

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(zips)} ZIP codes")


def seed_modifiers():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM modifiers")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    modifiers = [
        ("Polished Edge", "Ground and polished glass edge", "per_lf", 8.0),
        ("Drilled Holes", "Per hole drilled in glass", "per_unit", 25.0),
        ("Notch Cut", "Corner or notch cut", "per_unit", 35.0),
        ("Tempered Upgrade", "Upgrade any glass to tempered", "per_sqft", 15.0),
        ("Solarban Coating", "Add Solarban solar control", "per_sqft", 12.0),
        ("Low-E Coating", "Add Low-E energy coating", "per_sqft", 10.0),
        ("Screen Replacement", "Window screen", "per_unit", 55.0),
        ("Caulking/Sealing", "Full perimeter seal", "per_unit", 45.0),
        ("Frame Repair", "Minor frame fix", "per_unit", 85.0),
        ("Debris Cleanup", "Glass debris removal", "fixed", 35.0),
        ("Board-Up (temp)", "Temporary board protection", "per_sqft", 8.0),
        ("Hardware Replace", "Lock, handle, or hinge", "per_unit", 65.0),
    ]

    c.executemany("""
        INSERT INTO modifiers (name, description, price_type, price)
        VALUES (?,?,?,?)
    """, modifiers)

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(modifiers)} modifiers")


def seed_settings():
    conn = get_db()
    c = conn.cursor()

    settings = [
        ("labor_rate_per_hour", "85", "$/hour for 1 technician"),
        ("travel_rate_per_hour", "85", "$/hour travel time (each way)"),
        ("second_floor_surcharge", "200", "$ extra for 2nd floor"),
        ("third_floor_surcharge", "300", "$ extra for 3rd floor+"),
        ("scaffold_surcharge", "250", "$ extra if scaffold needed"),
        ("extra_tech_rate", "75", "$/hour for each additional technician"),
        ("urgent_multiplier", "1.30", "Multiplier for same-day service"),
        ("emergency_multiplier", "1.50", "Multiplier for emergency/after-hours"),
        ("min_job_price", "150", "Minimum job price"),
        ("tax_rate", "0.1025", "LA County sales tax (10.25%)"),
        ("material_markup", "2.75", "Material cost × this = sell price"),
        ("base_zip", "91324", "Base location ZIP (Northridge)"),
        ("company_name", "Fast Glass & Windows", "Company name"),
        ("company_phone", "213-566-8886", "Main phone"),
    ]

    c.executemany("""
        INSERT OR IGNORE INTO settings (key, value, description)
        VALUES (?,?,?)
    """, settings)

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(settings)} settings")


if __name__ == "__main__":
    init_db()
    seed_services()
    seed_zip_multipliers()
    seed_modifiers()
    seed_settings()
    print("✅ Database ready!")
