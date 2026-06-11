"""
ROMI Estimate — FastAPI server
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from database import get_db, init_db, seed_services, seed_zip_multipliers, seed_modifiers, seed_settings
from calculator import calculate, parse_dimensions
from products import PRODUCTS, get_products_by_category, CATEGORY_META, get_product, HARDWARE_PRODUCTS

# Init DB on startup
init_db()
seed_services()
seed_zip_multipliers()
seed_modifiers()
seed_settings()

app = FastAPI(title="ROMI Estimate API", version="1.0.0")

# CORS — allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# ─────────────────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────────────────

class CalculateRequest(BaseModel):
    service_id: int
    width_ft: int = 0
    width_in: int = 0
    width_frac: str = "0"
    height_ft: int = 0
    height_in: int = 0
    height_frac: str = "0"
    quantity: int = 1
    zip_code: str = "91324"
    floor: int = 1
    num_technicians: int = 1
    urgency: str = "normal"
    modifier_ids: Optional[List[int]] = []
    notes: str = ""
    product_options: Optional[dict] = {}
    options_add_sqft: float = 0.0  # pre-calculated surcharge from product options


class UpdateServiceRequest(BaseModel):
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    material_min: Optional[float] = None
    material_max: Optional[float] = None
    labor_min: Optional[float] = None
    labor_max: Optional[float] = None
    enabled: Optional[int] = None


class UpdateSettingRequest(BaseModel):
    value: str


# ─────────────────────────────────────────────────────────
# PUBLIC ENDPOINTS
# ─────────────────────────────────────────────────────────

@app.get("/")
def root():
    index = os.path.join(frontend_path, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"message": "ROMI Estimate API", "docs": "/docs"}


@app.get("/api/services")
def get_services(category: Optional[str] = None):
    """Get all enabled services, optionally filtered by category"""
    conn = get_db()
    if category:
        rows = conn.execute(
            "SELECT * FROM services WHERE enabled = 1 AND category = ? ORDER BY id",
            (category,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM services WHERE enabled = 1 ORDER BY category, id"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/products")
def get_products_api():
    """Get all products grouped by category — new Victor structure"""
    by_cat = get_products_by_category()
    result = []
    for cat_id, meta in sorted(CATEGORY_META.items(), key=lambda x: x[1]["order"]):
        if cat_id in by_cat:
            result.append({
                "category_id": cat_id,
                "category_label": meta["label"],
                "products": by_cat[cat_id]
            })
    # Add hardware category
    result.append({
        "category_id": "hardware",
        "category_label": "🔧 Hardware",
        "products": [
            {"id": p["id"], "label": p["label"], "description": p["description"],
             "price_per_sqft_min": p["price_min"], "price_per_sqft_max": p["price_max"],
             "min_charge": p.get("min_charge", 0), "category": "hardware"}
            for p in HARDWARE_PRODUCTS
        ]
    })
    return result


@app.get("/api/products/{product_id}")
def get_product_api(product_id: str):
    """Get single product with all fields"""
    # Check hardware products first
    hw = next((p for p in HARDWARE_PRODUCTS if p["id"] == product_id), None)
    if hw:
        return {
            "id": hw["id"],
            "label": hw["label"],
            "description": hw["description"],
            "category": "hardware",
            "service_id": hw["service_id"],
            "price_min": hw["price_min"],
            "price_max": hw["price_max"],
            "min_charge": hw.get("min_charge", 0),
            "is_flat_price": True,
            "fields": [
                {
                    "id": "condition",
                    "label": "Condition",
                    "type": "radio",
                    "default": "standard",
                    "options": [
                        {"value": "standard", "label": "Standard",        "price_add_unit": 0},
                        {"value": "difficult", "label": "Difficult access", "price_add_unit": 25},
                        {"value": "damaged",   "label": "Extra damage",    "price_add_unit": 40},
                    ]
                }
            ]
        }
    p = get_product(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@app.get("/api/services/categories")
def get_categories():
    """Get list of service categories"""
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT category FROM services WHERE enabled = 1 ORDER BY category"
    ).fetchall()
    conn.close()
    return [r["category"] for r in rows]


@app.get("/api/modifiers")
def get_modifiers():
    """Get all enabled modifiers"""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM modifiers WHERE enabled = 1 ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/zip/{zip_code}")
def lookup_zip(zip_code: str):
    """Look up ZIP code details"""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM zip_multipliers WHERE zip_code = ?",
        (zip_code,)
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"zip_code": zip_code, "city": "Unknown", "multiplier": 1.0, "travel_minutes": 45}


@app.post("/api/calculate")
def calculate_price(req: CalculateRequest):
    """Calculate price estimate"""
    # Parse dimensions
    width_inches = parse_dimensions(req.width_ft, req.width_in, req.width_frac)
    height_inches = parse_dimensions(req.height_ft, req.height_in, req.height_frac)

    if width_inches <= 0 or height_inches <= 0:
        raise HTTPException(status_code=400, detail="Width and height must be greater than 0")

    # Use pre-calculated surcharge from frontend
    options_add_sqft = req.options_add_sqft or 0.0

    result = calculate(
        service_id=req.service_id,
        width_inches=width_inches,
        height_inches=height_inches,
        quantity=req.quantity,
        zip_code=req.zip_code,
        floor=req.floor,
        num_technicians=req.num_technicians,
        urgency=req.urgency,
        modifier_ids=req.modifier_ids or [],
        notes=req.notes,
        options_add_sqft=options_add_sqft,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ─────────────────────────────────────────────────────────
# ADMIN ENDPOINTS
# ─────────────────────────────────────────────────────────

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "fastglass2026")


@app.get("/admin")
def admin_page():
    admin = os.path.join(frontend_path, "admin.html")
    if os.path.exists(admin):
        return FileResponse(admin)
    return {"message": "Admin panel not built yet"}


@app.get("/api/admin/services")
def admin_get_services(password: str = ""):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Wrong password")
    conn = get_db()
    rows = conn.execute("SELECT * FROM services ORDER BY category, id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.put("/api/admin/services/{service_id}")
def admin_update_service(service_id: int, req: UpdateServiceRequest, password: str = ""):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Wrong password")

    conn = get_db()
    updates = {k: v for k, v in req.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Nothing to update")

    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [service_id]
    conn.execute(f"UPDATE services SET {set_clause} WHERE id = ?", values)
    conn.commit()

    row = conn.execute("SELECT * FROM services WHERE id = ?", (service_id,)).fetchone()
    conn.close()
    return dict(row)


@app.get("/api/admin/settings")
def admin_get_settings(password: str = ""):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Wrong password")
    conn = get_db()
    rows = conn.execute("SELECT * FROM settings ORDER BY key").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.put("/api/admin/settings/{key}")
def admin_update_setting(key: str, req: UpdateSettingRequest, password: str = ""):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Wrong password")
    conn = get_db()
    conn.execute("UPDATE settings SET value = ? WHERE key = ?", (req.value, key))
    conn.commit()
    conn.close()
    return {"key": key, "value": req.value, "updated": True}


@app.get("/api/similar-jobs")
def get_similar_jobs(
    category: str,
    area_sqft: float,
    tolerance: float = 0.4
):
    """Find similar past jobs from HCP history"""
    import sqlite3 as sq
    db_path = os.path.join(os.path.dirname(__file__), 'pricing_history.db')
    if not os.path.exists(db_path):
        return []
    conn = sq.connect(db_path)
    conn.row_factory = sq.Row
    low = area_sqft * (1 - tolerance)
    high = area_sqft * (1 + tolerance)
    rows = conn.execute("""
        SELECT invoice, description_en, area_sqft, price, price_per_sqft,
               zip_code, date, features, hcp_job_id
        FROM job_history
        WHERE category = ?
        AND area_sqft BETWEEN ? AND ?
        AND status NOT IN ('pro canceled','user canceled')
        ORDER BY ABS(area_sqft - ?) ASC
        LIMIT 5
    """, (category, low, high, area_sqft)).fetchall()
    conn.close()
    result = []
    for r in rows:
        feats = []
        try:
            feats = json.loads(r['features'] or '[]')
        except:
            pass
        result.append({
            'invoice': r['invoice'],
            'description': r['description_en'],
            'area_sqft': round(r['area_sqft'] or 0, 1),
            'price': r['price'],
            'price_per_sqft': round(r['price_per_sqft'] or 0, 1),
            'zip_code': r['zip_code'],
            'date': r['date'],
            'features': feats,
            'hcp_url': f"https://pro.housecallpro.com/pro/jobs/{r['hcp_job_id']}" if r['hcp_job_id'] else ''
        })
    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
