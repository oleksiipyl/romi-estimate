"""Saved / signed estimates for staff and superadmin oversight."""

from __future__ import annotations

import json
from typing import Any, Optional

from admin_auth import _iso, _utcnow, is_superadmin
from database import get_db


def create_estimate(
    user_pk: int,
    title: str,
    payload: dict,
    mid_price: Optional[float] = None,
    range_min: Optional[float] = None,
    range_max: Optional[float] = None,
    notes: str = "",
) -> dict:
    now = _iso(_utcnow())
    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO estimates
        (user_pk, title, status, mid_price, range_min, range_max, payload_json, notes, created_at, updated_at)
        VALUES (?, ?, 'saved', ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_pk,
            title.strip() or "Estimate",
            mid_price,
            range_min,
            range_max,
            json.dumps(payload, ensure_ascii=False),
            notes or "",
            now,
            now,
        ),
    )
    pk = cur.lastrowid
    conn.commit()
    row = conn.execute(
        """
        SELECT e.*, u.user_id, u.display_name, u.email
        FROM estimates e
        JOIN admin_users u ON u.id = e.user_pk
        WHERE e.id = ?
        """,
        (pk,),
    ).fetchone()
    conn.close()
    return _serialize(row)


def list_estimates(viewer, mine_only: bool = False) -> list:
    conn = get_db()
    if mine_only or not is_superadmin(viewer):
        rows = conn.execute(
            """
            SELECT e.*, u.user_id, u.display_name, u.email,
                   s.user_id AS signed_by_user_id
            FROM estimates e
            JOIN admin_users u ON u.id = e.user_pk
            LEFT JOIN admin_users s ON s.id = e.signed_by_pk
            WHERE e.user_pk = ?
            ORDER BY e.created_at DESC
            """,
            (viewer["id"],),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT e.*, u.user_id, u.display_name, u.email,
                   s.user_id AS signed_by_user_id
            FROM estimates e
            JOIN admin_users u ON u.id = e.user_pk
            LEFT JOIN admin_users s ON s.id = e.signed_by_pk
            ORDER BY e.created_at DESC
            """
        ).fetchall()
    conn.close()
    return [_serialize(r, include_payload=False) for r in rows]


def get_estimate(estimate_id: int, viewer) -> Optional[dict]:
    conn = get_db()
    row = conn.execute(
        """
        SELECT e.*, u.user_id, u.display_name, u.email,
               s.user_id AS signed_by_user_id
        FROM estimates e
        JOIN admin_users u ON u.id = e.user_pk
        LEFT JOIN admin_users s ON s.id = e.signed_by_pk
        WHERE e.id = ?
        """,
        (estimate_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    if row["user_pk"] != viewer["id"] and not is_superadmin(viewer):
        return None
    return _serialize(row, include_payload=True)


def sign_estimate(estimate_id: int, viewer) -> Optional[dict]:
    row = get_estimate(estimate_id, viewer)
    if not row:
        return None
    if row["status"] == "signed":
        return row
    now = _iso(_utcnow())
    conn = get_db()
    conn.execute(
        """
        UPDATE estimates
        SET status = 'signed', signed_at = ?, signed_by_pk = ?, updated_at = ?
        WHERE id = ?
        """,
        (now, viewer["id"], now, estimate_id),
    )
    conn.commit()
    conn.close()
    return get_estimate(estimate_id, viewer)


def _serialize(row: Any, include_payload: bool = True) -> dict:
    data = {
        "id": row["id"],
        "title": row["title"],
        "status": row["status"],
        "mid_price": row["mid_price"],
        "range_min": row["range_min"],
        "range_max": row["range_max"],
        "notes": row["notes"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "signed_at": row["signed_at"],
        "owner": {
            "user_id": row["user_id"],
            "display_name": row["display_name"],
            "email": row["email"],
        },
        "signed_by_user_id": row["signed_by_user_id"] if "signed_by_user_id" in row.keys() else None,
    }
    if include_payload:
        try:
            data["payload"] = json.loads(row["payload_json"] or "{}")
        except json.JSONDecodeError:
            data["payload"] = {}
    return data
