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
from products import PRODUCTS, get_products_by_category, CATEGORY_META, get_product

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
    return result


@app.get("/api/products/{product_id}")
def get_product_api(product_id: str):
    """Get single product with all fields"""
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
