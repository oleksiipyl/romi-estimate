"""
ROMI Estimate — FastAPI server
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from database import get_db, init_db, seed_services, seed_zip_multipliers, seed_modifiers, seed_settings
from calculator import calculate, parse_dimensions
from products import PRODUCTS, get_products_by_category, CATEGORY_META, get_product, HARDWARE_PRODUCTS
import admin_auth

# Init DB on startup
init_db()
seed_services()
seed_zip_multipliers()
seed_modifiers()
seed_settings()
admin_auth.ensure_admin_tables()
admin_auth.seed_admin_user_from_env()

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
    product_min_charge: float = 0.0  # min charge from products.py


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


class AdminLoginRequest(BaseModel):
    login: str = Field(..., description="User ID or email")
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotUserIdRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


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
        product_min_charge=req.product_min_charge or 0.0,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ─────────────────────────────────────────────────────────
# ADMIN ENDPOINTS
# ─────────────────────────────────────────────────────────

def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def require_admin(authorization: Optional[str] = Header(None), x_admin_token: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_admin_token:
        token = x_admin_token.strip()
    user = admin_auth.get_user_for_session(token or "")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@app.get("/admin")
def admin_page():
    admin = os.path.join(frontend_path, "admin.html")
    if os.path.exists(admin):
        return FileResponse(admin)
    return {"message": "Admin panel not built yet"}


@app.get("/api/admin/auth/status")
def admin_auth_status():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) AS c FROM admin_users").fetchone()["c"]
    conn.close()
    return {
        "users_configured": count > 0,
        "smtp_configured": admin_auth.smtp_configured(),
        "needs_bootstrap": count == 0,
    }


@app.post("/api/admin/auth/login")
def admin_login(req: AdminLoginRequest, request: Request):
    ip = _client_ip(request)
    if not admin_auth.check_rate_limit(f"login:{ip}"):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

    user = admin_auth.find_user_by_login(req.login)
    if not user or not admin_auth.verify_password(req.password, user["password_hash"], user["salt"]):
        raise HTTPException(status_code=401, detail="Invalid User ID/email or password")

    token = admin_auth.create_session(user["id"])
    return {
        "token": token,
        "user_id": user["user_id"],
        "email": user["email"],
        "expires_hours": admin_auth.SESSION_HOURS,
    }


@app.post("/api/admin/auth/logout")
def admin_logout(authorization: Optional[str] = Header(None), x_admin_token: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_admin_token:
        token = x_admin_token.strip()
    admin_auth.revoke_session(token or "")
    return {"ok": True}


@app.get("/api/admin/auth/me")
def admin_me(authorization: Optional[str] = Header(None), x_admin_token: Optional[str] = Header(None)):
    user = require_admin(authorization, x_admin_token)
    return {"user_id": user["user_id"], "email": user["email"]}


@app.post("/api/admin/auth/forgot-password")
def admin_forgot_password(req: ForgotPasswordRequest, request: Request):
    ip = _client_ip(request)
    if not admin_auth.check_rate_limit(f"forgot-pw:{ip}"):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

    # Always same response (no email enumeration)
    generic = {
        "ok": True,
        "message": "If that email is registered, reset instructions were sent.",
    }
    user = admin_auth.find_user_by_email(req.email)
    if user:
        token = admin_auth.create_recovery_token(user["id"], "reset_password")
        admin_auth.password_reset_email(user["email"], user["user_id"], token)
    return generic


@app.post("/api/admin/auth/forgot-user-id")
def admin_forgot_user_id(req: ForgotUserIdRequest, request: Request):
    ip = _client_ip(request)
    if not admin_auth.check_rate_limit(f"forgot-uid:{ip}"):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

    generic = {
        "ok": True,
        "message": "If that email is registered, the User ID reminder was sent.",
    }
    user = admin_auth.find_user_by_email(req.email)
    if user:
        admin_auth.user_id_reminder_email(user["email"], user["user_id"])
    return generic


@app.post("/api/admin/auth/reset-password")
def admin_reset_password(req: ResetPasswordRequest, request: Request):
    ip = _client_ip(request)
    if not admin_auth.check_rate_limit(f"reset-pw:{ip}"):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

    row = admin_auth.consume_recovery_token(req.token, "reset_password")
    if not row:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")

    admin_auth.set_password(row["user_pk"], req.new_password)
    token = admin_auth.create_session(row["user_pk"])
    return {
        "ok": True,
        "token": token,
        "user_id": row["user_id"],
        "email": row["email"],
        "message": "Password updated. All previous sessions were signed out.",
    }


@app.get("/api/admin/services")
def admin_get_services(authorization: Optional[str] = Header(None), x_admin_token: Optional[str] = Header(None)):
    require_admin(authorization, x_admin_token)
    conn = get_db()
    rows = conn.execute("SELECT * FROM services ORDER BY category, id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.put("/api/admin/services/{service_id}")
def admin_update_service(
    service_id: int,
    req: UpdateServiceRequest,
    authorization: Optional[str] = Header(None),
    x_admin_token: Optional[str] = Header(None),
):
    require_admin(authorization, x_admin_token)

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
def admin_get_settings(authorization: Optional[str] = Header(None), x_admin_token: Optional[str] = Header(None)):
    require_admin(authorization, x_admin_token)
    conn = get_db()
    rows = conn.execute("SELECT * FROM settings ORDER BY key").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.put("/api/admin/settings/{key}")
def admin_update_setting(
    key: str,
    req: UpdateSettingRequest,
    authorization: Optional[str] = Header(None),
    x_admin_token: Optional[str] = Header(None),
):
    require_admin(authorization, x_admin_token)
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
