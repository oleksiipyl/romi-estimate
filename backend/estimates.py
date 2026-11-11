"""Saved / signed estimates for staff and superadmin oversight."""

from __future__ import annotations

import json
from typing import Any, Optional

from admin_auth import _iso, _utcnow, is_superadmin
from database import get_db


def _require_project_number(project_number: Optional[str]) -> str:
    pn = (project_number or "").strip()
    if not pn:
        raise ValueError("Project / estimate ID number is required")
    if len(pn) > 64:
        raise ValueError("Project number is too long")
    return pn


def _write_audit(
    *,
    action: str,
    estimate_id: Optional[int],
    project_number: Optional[str],
    title_snapshot: Optional[str],
    status_before: Optional[str],
    status_after: Optional[str],
    actor,
    detail: Optional[dict] = None,
) -> None:
    conn = get_db()
    conn.execute(
        """
        INSERT INTO estimate_audit_log
        (action, estimate_id, project_number, title_snapshot, status_before, status_after,
         actor_pk, actor_user_id, detail_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            action,
            estimate_id,
            project_number,
            title_snapshot,
            status_before,
            status_after,
            actor["id"] if actor else None,
            actor["user_id"] if actor else None,
            json.dumps(detail or {}, ensure_ascii=False),
            _iso(_utcnow()),
        ),
    )
    conn.commit()
    conn.close()


def create_estimate(
    user_pk: int,
    title: str,
    payload: dict,
    mid_price: Optional[float] = None,
    range_min: Optional[float] = None,
    range_max: Optional[float] = None,
    notes: str = "",
    project_number: Optional[str] = None,
    actor=None,
) -> dict:
    pn = _require_project_number(project_number)
    now = _iso(_utcnow())
    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO estimates
        (user_pk, title, status, mid_price, range_min, range_max, payload_json, notes,
         created_at, updated_at, project_number)
        VALUES (?, ?, 'saved', ?, ?, ?, ?, ?, ?, ?, ?)
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
            pn,
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
    if actor:
        _write_audit(
            action="created",
            estimate_id=pk,
            project_number=pn,
            title_snapshot=row["title"],
            status_before=None,
            status_after="saved",
            actor=actor,
            detail={"mid_price": mid_price},
        )
    return _serialize(row)


def list_estimates(viewer, mine_only: bool = False, status: Optional[str] = None) -> list:
    conn = get_db()
    clauses = []
    params: list = []
    if mine_only or not is_superadmin(viewer):
        clauses.append("e.user_pk = ?")
        params.append(viewer["id"])
    if status in ("saved", "signed", "unsigned"):
        if status == "unsigned":
            clauses.append("e.status != 'signed'")
        else:
            clauses.append("e.status = ?")
            params.append(status)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"""
        SELECT e.*, u.user_id, u.display_name, u.email,
               s.user_id AS signed_by_user_id
        FROM estimates e
        JOIN admin_users u ON u.id = e.user_pk
        LEFT JOIN admin_users s ON s.id = e.signed_by_pk
        {where}
        ORDER BY
          CASE WHEN e.project_number IS NULL OR e.project_number = '' THEN 1 ELSE 0 END,
          e.project_number COLLATE NOCASE ASC,
          e.updated_at DESC
    """
    rows = conn.execute(sql, params).fetchall()
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


def find_by_project_number(project_number: str, viewer) -> list:
    pn = (project_number or "").strip()
    if not pn:
        return []
    conn = get_db()
    if is_superadmin(viewer):
        rows = conn.execute(
            """
            SELECT e.*, u.user_id, u.display_name, u.email,
                   s.user_id AS signed_by_user_id
            FROM estimates e
            JOIN admin_users u ON u.id = e.user_pk
            LEFT JOIN admin_users s ON s.id = e.signed_by_pk
            WHERE lower(e.project_number) = lower(?)
            ORDER BY e.updated_at DESC
            """,
            (pn,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT e.*, u.user_id, u.display_name, u.email,
                   s.user_id AS signed_by_user_id
            FROM estimates e
            JOIN admin_users u ON u.id = e.user_pk
            LEFT JOIN admin_users s ON s.id = e.signed_by_pk
            WHERE e.user_pk = ? AND lower(e.project_number) = lower(?)
            ORDER BY e.updated_at DESC
            """,
            (viewer["id"], pn),
        ).fetchall()
    conn.close()
    return [_serialize(r, include_payload=False) for r in rows]


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
    _write_audit(
        action="signed",
        estimate_id=estimate_id,
        project_number=row.get("project_number"),
        title_snapshot=row.get("title"),
        status_before=row.get("status") or "saved",
        status_after="signed",
        actor=viewer,
    )
    return get_estimate(estimate_id, viewer)


def update_estimate(
    estimate_id: int,
    viewer,
    *,
    title: str,
    payload: dict,
    mid_price: Optional[float] = None,
    range_min: Optional[float] = None,
    range_max: Optional[float] = None,
    notes: str = "",
    project_number: Optional[str] = None,
) -> Optional[dict]:
    """Update an unsigned estimate owned by viewer (or any if superadmin)."""
    pn = _require_project_number(project_number)
    conn = get_db()
    row = conn.execute("SELECT * FROM estimates WHERE id = ?", (estimate_id,)).fetchone()
    if not row:
        conn.close()
        return None
    if row["user_pk"] != viewer["id"] and not is_superadmin(viewer):
        conn.close()
        return None
    if row["status"] == "signed":
        conn.close()
        raise ValueError("Signed quotes cannot be edited")
    now = _iso(_utcnow())
    conn.execute(
        """
        UPDATE estimates
        SET title = ?, mid_price = ?, range_min = ?, range_max = ?,
            payload_json = ?, notes = ?, updated_at = ?, project_number = ?
        WHERE id = ?
        """,
        (
            (title or "").strip() or "Estimate",
            mid_price,
            range_min,
            range_max,
            json.dumps(payload or {}, ensure_ascii=False),
            notes or "",
            now,
            pn,
            estimate_id,
        ),
    )
    conn.commit()
    conn.close()
    _write_audit(
        action="updated",
        estimate_id=estimate_id,
        project_number=pn,
        title_snapshot=(title or "").strip() or "Estimate",
        status_before="saved",
        status_after="saved",
        actor=viewer,
    )
    return get_estimate(estimate_id, viewer)


def delete_estimate(estimate_id: int, viewer) -> bool:
    """Delete an unsigned estimate. Returns False if missing/forbidden, raises if signed."""
    conn = get_db()
    row = conn.execute("SELECT * FROM estimates WHERE id = ?", (estimate_id,)).fetchone()
    if not row:
        conn.close()
        return False
    if row["user_pk"] != viewer["id"] and not is_superadmin(viewer):
        conn.close()
        return False
    if row["status"] == "signed":
        conn.close()
        raise ValueError("Signed quotes cannot be deleted")
    snapshot = {
        "title": row["title"],
        "project_number": row["project_number"] if "project_number" in row.keys() else None,
        "mid_price": row["mid_price"],
        "status": row["status"],
    }
    conn.execute("DELETE FROM estimates WHERE id = ?", (estimate_id,))
    conn.commit()
    conn.close()
    _write_audit(
        action="deleted",
        estimate_id=estimate_id,
        project_number=snapshot["project_number"],
        title_snapshot=snapshot["title"],
        status_before=snapshot["status"],
        status_after=None,
        actor=viewer,
        detail=snapshot,
    )
    return True


def list_audit_log(viewer, limit: int = 100) -> list:
    """Superadmin sees all; staff see events they caused or on their estimates."""
    conn = get_db()
    limit = max(1, min(int(limit or 100), 500))
    if is_superadmin(viewer):
        rows = conn.execute(
            """
            SELECT * FROM estimate_audit_log
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT a.* FROM estimate_audit_log a
            WHERE a.actor_pk = ?
               OR a.estimate_id IN (SELECT id FROM estimates WHERE user_pk = ?)
            ORDER BY a.created_at DESC, a.id DESC
            LIMIT ?
            """,
            (viewer["id"], viewer["id"], limit),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _serialize(row: Any, include_payload: bool = True) -> dict:
    keys = row.keys()
    data = {
        "id": row["id"],
        "title": row["title"],
        "status": row["status"],
        "project_number": row["project_number"] if "project_number" in keys else None,
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
        "signed_by_user_id": row["signed_by_user_id"] if "signed_by_user_id" in keys else None,
    }
    if include_payload:
        try:
            data["payload"] = json.loads(row["payload_json"] or "{}")
        except json.JSONDecodeError:
            data["payload"] = {}
    return data
