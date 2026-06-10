"""
ROMI Estimate — Price calculation engine
Pure math, no AI needed. Just area × rates from database.
"""

from database import get_db


def inches_to_sqft(width_inches: float, height_inches: float) -> float:
    """Convert dimensions in inches to square feet"""
    return (width_inches / 12) * (height_inches / 12)


def parse_dimensions(feet: int, inches: int, fraction: str) -> float:
    """Parse feet + inches + fraction → total inches
    fraction: '0', '1/8', '1/4', '3/8', '1/2', '5/8', '3/4', '7/8'
    """
    fraction_map = {
        '0': 0, '1/8': 0.125, '1/4': 0.25, '3/8': 0.375,
        '1/2': 0.5, '5/8': 0.625, '3/4': 0.75, '7/8': 0.875
    }
    frac_val = fraction_map.get(fraction, 0)
    return (feet * 12) + inches + frac_val


def get_zip_data(zip_code: str) -> dict:
    """Get multiplier and travel time for ZIP code"""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM zip_multipliers WHERE zip_code = ?",
        (zip_code,)
    ).fetchone()
    conn.close()

    if row:
        return {
            "city": row["city"],
            "multiplier": row["multiplier"],
            "travel_minutes": row["travel_minutes"]
        }
    # Unknown ZIP — default values
    return {"city": "Unknown", "multiplier": 1.0, "travel_minutes": 45}


def get_setting(key: str) -> float:
    """Get a setting value as float"""
    conn = get_db()
    row = conn.execute(
        "SELECT value FROM settings WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    return float(row["value"]) if row else 0.0


def calculate(
    service_id: int,
    width_inches: float,
    height_inches: float,
    quantity: int = 1,
    zip_code: str = "91324",
    floor: int = 1,
    num_technicians: int = 1,
    urgency: str = "normal",  # normal, urgent, emergency
    modifier_ids: list = None,
    notes: str = ""
) -> dict:
    """
    Main calculation function.
    Returns detailed price breakdown.
    """

    conn = get_db()

    # Get service
    service = conn.execute(
        "SELECT * FROM services WHERE id = ? AND enabled = 1",
        (service_id,)
    ).fetchone()

    if not service:
        conn.close()
        return {"error": "Service not found"}

    # Get settings
    labor_rate = get_setting("labor_rate_per_hour")
    travel_rate = get_setting("travel_rate_per_hour")
    material_markup = get_setting("material_markup")
    min_price = get_setting("min_job_price")
    tax_rate = get_setting("tax_rate")
    urgent_mult = get_setting("urgent_multiplier")
    emergency_mult = get_setting("emergency_multiplier")

    # Calculate area
    area = inches_to_sqft(width_inches, height_inches)
    total_area = area * quantity

    # Minimum area check (min 2 sqft)
    calc_area = max(total_area, 2.0)

    # Material cost (from DB × markup)
    material_min = calc_area * service["material_min"] * material_markup
    material_max = calc_area * service["material_max"] * material_markup

    # Labor cost
    labor_min = calc_area * service["labor_min"]
    labor_max = calc_area * service["labor_max"]

    # ZIP multiplier and travel
    zip_data = get_zip_data(zip_code)
    zip_multiplier = zip_data["multiplier"]
    travel_minutes = zip_data["travel_minutes"]
    travel_cost = (travel_minutes / 60) * travel_rate * 2  # both ways

    # Floor surcharge
    floor_surcharge = 0
    floor_note = ""
    if floor == 2:
        floor_surcharge = get_setting("second_floor_surcharge")
        floor_note = "2nd floor — ladder required"
    elif floor >= 3:
        floor_surcharge = get_setting("third_floor_surcharge")
        floor_note = "3rd floor+ — scaffold may be needed"

    # Extra technicians
    extra_tech_cost = 0
    tech_note = ""
    if num_technicians > 1:
        extra_hours = 2.5  # assume 2.5hr job
        extra_tech_cost = (num_technicians - 1) * get_setting("extra_tech_rate") * extra_hours
        tech_note = f"{num_technicians} technicians needed"

    # Modifiers
    modifier_total = 0
    modifier_names = []
    if modifier_ids:
        for mod_id in modifier_ids:
            mod = conn.execute(
                "SELECT * FROM modifiers WHERE id = ? AND enabled = 1",
                (mod_id,)
            ).fetchone()
            if mod:
                if mod["price_type"] == "per_sqft":
                    modifier_total += mod["price"] * calc_area
                elif mod["price_type"] == "per_lf":
                    # Estimate perimeter
                    perimeter_lf = 2 * (width_inches + height_inches) / 12
                    modifier_total += mod["price"] * perimeter_lf * quantity
                else:
                    modifier_total += mod["price"] * quantity
                modifier_names.append(mod["name"])

    conn.close()

    # Subtotals before urgency
    subtotal_min = (material_min + labor_min) * zip_multiplier + travel_cost + floor_surcharge + extra_tech_cost + modifier_total
    subtotal_max = (material_max + labor_max) * zip_multiplier + travel_cost + floor_surcharge + extra_tech_cost + modifier_total

    # Urgency multiplier (on labor + material only)
    urgency_mult = 1.0
    urgency_label = ""
    if urgency == "urgent":
        urgency_mult = urgent_mult
        urgency_label = "Same-day service +30%"
    elif urgency == "emergency":
        urgency_mult = emergency_mult
        urgency_label = "Emergency/after-hours +50%"

    base_min = (material_min + labor_min) * zip_multiplier * urgency_mult
    base_max = (material_max + labor_max) * zip_multiplier * urgency_mult

    total_min = base_min + travel_cost + floor_surcharge + extra_tech_cost + modifier_total
    total_max = base_max + travel_cost + floor_surcharge + extra_tech_cost + modifier_total

    # Apply minimum
    total_min = max(total_min, min_price)
    total_max = max(total_max, min_price + 50)

    # Tax
    tax_min = total_min * tax_rate
    tax_max = total_max * tax_rate

    # Recommendations
    recommendations = []
    if floor >= 2 and num_technicians < 2:
        recommendations.append("⚠️ Recommend 2 technicians for 2nd floor work")
    if floor >= 3:
        recommendations.append("⚠️ Confirm scaffold availability before booking")
    if area < 1.0:
        recommendations.append("ℹ️ Minimum charge applies (small piece)")
    if travel_minutes > 60:
        recommendations.append(f"🚗 Long drive ({travel_minutes} min) — confirm traffic")

    return {
        "service_name": service["name"],
        "category": service["category"],
        "area_sqft": round(area, 2),
        "total_area_sqft": round(calc_area, 2),
        "quantity": quantity,
        "location": zip_data["city"],
        "zip_multiplier": zip_multiplier,
        "breakdown": {
            "material_min": round(material_min, 2),
            "material_max": round(material_max, 2),
            "labor_min": round(labor_min, 2),
            "labor_max": round(labor_max, 2),
            "travel_cost": round(travel_cost, 2),
            "floor_surcharge": round(floor_surcharge, 2),
            "extra_tech_cost": round(extra_tech_cost, 2),
            "modifiers_total": round(modifier_total, 2),
            "urgency_label": urgency_label,
        },
        "total_min": round(total_min, 2),
        "total_max": round(total_max, 2),
        "tax_min": round(tax_min, 2),
        "tax_max": round(tax_max, 2),
        "grand_total_min": round(total_min + tax_min, 2),
        "grand_total_max": round(total_max + tax_max, 2),
        "notes": [floor_note, tech_note] + modifier_names + recommendations,
        "recommendations": recommendations,
    }
