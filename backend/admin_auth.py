"""
Admin authentication: user_id + email + password, session tokens,
and email recovery (forgot password / remind user_id).
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import smtplib
import ssl
import time
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Optional, Tuple

from database import get_db

PBKDF2_ITERATIONS = 210_000
SESSION_HOURS = 12
RESET_TOKEN_MINUTES = 30
RATE_WINDOW_SEC = 900
RATE_MAX_ATTEMPTS = 5


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()
    return digest, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    digest, _ = hash_password(password, salt)
    return hmac.compare_digest(digest, password_hash)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def ensure_admin_tables() -> None:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            display_name TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cols = {row[1] for row in c.execute("PRAGMA table_info(admin_users)").fetchall()}
    if "role" not in cols:
        c.execute("ALTER TABLE admin_users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
        c.execute(
            """
            UPDATE admin_users
            SET role = 'superadmin'
            WHERE id = (SELECT MIN(id) FROM admin_users)
            """
        )
    if "display_name" not in cols:
        c.execute("ALTER TABLE admin_users ADD COLUMN display_name TEXT")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_sessions (
            token_hash TEXT PRIMARY KEY,
            user_pk INTEGER NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_pk) REFERENCES admin_users(id)
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_recovery_tokens (
            token_hash TEXT PRIMARY KEY,
            user_pk INTEGER NOT NULL,
            purpose TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_pk) REFERENCES admin_users(id)
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_rate_limits (
            bucket TEXT PRIMARY KEY,
            count INTEGER NOT NULL,
            window_start INTEGER NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_pk INTEGER NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'saved',
            mid_price REAL,
            range_min REAL,
            range_max REAL,
            payload_json TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            signed_at TEXT,
            signed_by_pk INTEGER,
            FOREIGN KEY(user_pk) REFERENCES admin_users(id),
            FOREIGN KEY(signed_by_pk) REFERENCES admin_users(id)
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS access_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            display_name TEXT NOT NULL,
            desired_user_id TEXT,
            note TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            decided_at TEXT,
            decided_by_pk INTEGER,
            FOREIGN KEY(decided_by_pk) REFERENCES admin_users(id)
        )
        """
    )
    conn.commit()
    conn.close()


# Product owner defaults (override via Railway env if needed)
DEFAULT_OWNER_EMAIL = "oleksii.pyl@gmail.com"
DEFAULT_OWNER_USER_ID = "oleksii.pyl"
DEFAULT_OWNER_DISPLAY = "Oleksii Pyl"
# Company mailbox used for access-request alerts (override with OWNER_NOTIFY_EMAIL)
DEFAULT_OWNER_NOTIFY = "a.olwin@olwininc.com"


def owner_notify_email() -> str:
    return (
        os.getenv("OWNER_NOTIFY_EMAIL")
        or DEFAULT_OWNER_NOTIFY
        or os.getenv("ADMIN_EMAIL")
        or DEFAULT_OWNER_EMAIL
    ).strip().lower()


def seed_admin_user_from_env() -> None:
    """Ensure product-owner superadmin exists.

    Identity defaults to oleksii.pyl / oleksii.pyl@gmail.com.
    ADMIN_PASSWORD is used only when creating the owner for the first time.
    Repeated boots must not overwrite a changed password or revoke sessions.
    """
    email = (os.getenv("ADMIN_EMAIL") or DEFAULT_OWNER_EMAIL).strip().lower()
    user_id = (os.getenv("ADMIN_USER_ID") or DEFAULT_OWNER_USER_ID).strip().lower()
    display = (os.getenv("ADMIN_DISPLAY_NAME") or DEFAULT_OWNER_DISPLAY).strip()
    env_password = (os.getenv("ADMIN_PASSWORD") or "").strip()
    if not email or not user_id:
        return

    existing = find_user_by_email(email) or find_user_by_login(user_id)
    if existing:
        # Existing owner: preserve password hash, salt, and sessions across boots.
        if (existing["role"] if "role" in existing.keys() else "user") != "superadmin":
            conn = get_db()
            conn.execute(
                "UPDATE admin_users SET role = 'superadmin', updated_at = ? WHERE id = ?",
                (_iso(_utcnow()), existing["id"]),
            )
            conn.commit()
            conn.close()
            print(f"[admin_auth] Owner role ensured superadmin for user_pk={existing['id']}")
        return

    password = env_password or secrets.token_urlsafe(18)
    pw_hash, salt = hash_password(password)
    now = _iso(_utcnow())
    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO admin_users
        (user_id, email, password_hash, salt, role, display_name, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'superadmin', ?, ?, ?)
        """,
        (user_id, email, pw_hash, salt, display, now, now),
    )
    pk = cur.lastrowid
    conn.commit()
    conn.close()

    if not env_password:
        token = create_recovery_token(pk, "reset_password")
        invite_set_password_email(email, user_id, token)
        print(f"[admin_auth] Superadmin ready: user_id={user_id} email={email} (set password via invite/reset link or ADMIN_PASSWORD)")
    else:
        print(f"[admin_auth] Superadmin ready: user_id={user_id} email={email} (password from ADMIN_PASSWORD)")


def notify_owner_of_access_request(
    email: str,
    display_name: str,
    desired_user_id: str,
    note: str,
    correlation_id: str = "",
) -> None:
    """Background owner alert for a newly recorded access request."""
    cid = correlation_id or new_mail_correlation_id()
    try:
        notify = owner_notify_email()
        body = (
            f"New access request for ROMI Estimate\n\n"
            f"Name: {display_name}\n"
            f"Email: {email}\n"
            f"Requested User ID: {desired_user_id or '(auto)'}\n"
            f"Note: {note or '—'}\n\n"
            f"Approve or reject in Admin → Access requests.\n"
        )
        ok = send_email(notify, "ROMI Estimate — access request", body, correlation_id=cid)
        if not ok:
            log_mail_event("access_request", category="provider_failed", correlation_id=cid)
    except Exception:
        log_mail_event("access_request", category="provider_exception", correlation_id=cid)


def create_access_request(email: str, display_name: str, desired_user_id: str = "", note: str = "") -> dict:
    """Record an access request when appropriate.

    Returns an internal outcome for the caller. Public HTTP must not expose
    existing-account vs pending vs newly-created differences.
    Does not send mail synchronously — caller may schedule notify_owner_of_access_request
    only when outcome == 'created'.
    """
    email = (email or "").strip().lower()
    display_name = (display_name or "").strip()
    desired_user_id = (desired_user_id or "").strip().lower()
    note = (note or "").strip()
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Valid email is required")
    if not display_name:
        raise ValueError("Name is required")

    if find_user_by_email(email):
        return {
            "outcome": "existing_account",
            "created": False,
            "email": email,
            "status": None,
            "id": None,
        }

    conn = get_db()
    pending = conn.execute(
        "SELECT id FROM access_requests WHERE lower(email) = ? AND status = 'pending'",
        (email,),
    ).fetchone()
    if pending:
        conn.close()
        return {
            "outcome": "already_pending",
            "created": False,
            "email": email,
            "status": "pending",
            "id": pending["id"],
        }

    now = _iso(_utcnow())
    cur = conn.execute(
        """
        INSERT INTO access_requests
        (email, display_name, desired_user_id, note, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)
        """,
        (email, display_name, desired_user_id or None, note, now),
    )
    pk = cur.lastrowid
    conn.commit()
    conn.close()
    return {
        "outcome": "created",
        "created": True,
        "email": email,
        "status": "pending",
        "id": pk,
        "display_name": display_name,
        "desired_user_id": desired_user_id,
        "note": note,
    }


def list_access_requests(status: str = "pending") -> list:
    conn = get_db()
    if status == "all":
        rows = conn.execute(
            "SELECT * FROM access_requests ORDER BY created_at DESC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM access_requests WHERE status = ? ORDER BY created_at DESC",
            (status,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def decide_access_request(request_id: int, approve: bool, reviewer) -> dict:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM access_requests WHERE id = ?",
        (request_id,),
    ).fetchone()
    if not row:
        conn.close()
        raise ValueError("Request not found")
    if row["status"] != "pending":
        conn.close()
        raise ValueError("Request already decided")

    now = _iso(_utcnow())
    new_status = "approved" if approve else "rejected"
    conn.execute(
        """
        UPDATE access_requests
        SET status = ?, decided_at = ?, decided_by_pk = ?
        WHERE id = ?
        """,
        (new_status, now, reviewer["id"], request_id),
    )
    conn.commit()
    conn.close()

    created_user = None
    if approve:
        base = (row["desired_user_id"] or row["email"].split("@")[0]).strip().lower()
        base = "".join(ch if ch.isalnum() or ch in "._-" else "." for ch in base) or "user"
        candidate = base
        n = 1
        while find_user_by_login(candidate):
            n += 1
            candidate = f"{base}{n}"
        created_user = create_user(
            user_id=candidate,
            email=row["email"],
            role="user",
            display_name=row["display_name"],
            send_invite=True,
        )
        send_email(
            row["email"],
            "ROMI Estimate — access approved",
            (
                f"Hello {row['display_name']},\n\n"
                f"Your access request was approved.\n"
                f"User ID: {created_user['user_id']}\n"
                f"Check your email for the set-password link, then sign in at /login.\n"
            ),
        )
    else:
        send_email(
            row["email"],
            "ROMI Estimate — access not approved",
            (
                f"Hello {row['display_name']},\n\n"
                f"Your access request for ROMI Estimate was not approved.\n"
                f"Contact your manager if you need access.\n"
            ),
        )

    return {"id": request_id, "status": new_status, "user": created_user}


def is_superadmin(user) -> bool:
    return bool(user) and (user["role"] if "role" in user.keys() else "user") == "superadmin"


def public_user(user) -> dict:
    return {
        "id": user["id"],
        "user_id": user["user_id"],
        "email": user["email"],
        "role": user["role"] if "role" in user.keys() else "user",
        "display_name": user["display_name"] if "display_name" in user.keys() else None,
    }


def create_user(
    user_id: str,
    email: str,
    role: str = "user",
    display_name: str = "",
    password: Optional[str] = None,
    send_invite: bool = True,
) -> dict:
    user_id = (user_id or "").strip().lower()
    email = (email or "").strip().lower()
    role = role if role in ("superadmin", "user") else "user"
    if not user_id or not email:
        raise ValueError("user_id and email are required")
    if find_user_by_login(user_id) or find_user_by_email(email):
        raise ValueError("User ID or email already exists")

    temp = password or secrets.token_urlsafe(12)
    pw_hash, salt = hash_password(temp)
    now = _iso(_utcnow())
    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO admin_users
        (user_id, email, password_hash, salt, role, display_name, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, email, pw_hash, salt, role, display_name or user_id, now, now),
    )
    pk = cur.lastrowid
    conn.commit()
    conn.close()

    invite_sent = False
    if send_invite:
        token = create_recovery_token(pk, "reset_password")
        invite_sent = invite_set_password_email(email, user_id, token)

    return {
        "id": pk,
        "user_id": user_id,
        "email": email,
        "role": role,
        "display_name": display_name or user_id,
        "invite_sent": invite_sent,
    }


def list_users() -> list:
    conn = get_db()
    rows = conn.execute(
        """
        SELECT id, user_id, email, role, display_name, created_at, updated_at
        FROM admin_users
        ORDER BY role DESC, user_id ASC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def check_rate_limit(bucket: str) -> bool:
    """Return True if allowed, False if limited."""
    now = int(time.time())
    conn = get_db()
    row = conn.execute(
        "SELECT count, window_start FROM admin_rate_limits WHERE bucket = ?",
        (bucket,),
    ).fetchone()
    if not row or now - row["window_start"] > RATE_WINDOW_SEC:
        conn.execute(
            """
            INSERT INTO admin_rate_limits (bucket, count, window_start)
            VALUES (?, 1, ?)
            ON CONFLICT(bucket) DO UPDATE SET count = 1, window_start = excluded.window_start
            """,
            (bucket, now),
        )
        conn.commit()
        conn.close()
        return True

    if row["count"] >= RATE_MAX_ATTEMPTS:
        conn.close()
        return False

    conn.execute(
        "UPDATE admin_rate_limits SET count = count + 1 WHERE bucket = ?",
        (bucket,),
    )
    conn.commit()
    conn.close()
    return True


def find_user_by_login(login: str):
    login = (login or "").strip().lower()
    if not login:
        return None
    conn = get_db()
    row = conn.execute(
        """
        SELECT * FROM admin_users
        WHERE lower(user_id) = ? OR lower(email) = ?
        """,
        (login, login),
    ).fetchone()
    conn.close()
    return row


def find_user_by_email(email: str):
    email = (email or "").strip().lower()
    if not email:
        return None
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM admin_users WHERE lower(email) = ?",
        (email,),
    ).fetchone()
    conn.close()
    return row


def create_session(user_pk: int) -> str:
    token = secrets.token_urlsafe(32)
    expires = _utcnow() + timedelta(hours=SESSION_HOURS)
    conn = get_db()
    conn.execute(
        """
        INSERT INTO admin_sessions (token_hash, user_pk, expires_at, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (hash_token(token), user_pk, _iso(expires), _iso(_utcnow())),
    )
    conn.commit()
    conn.close()
    return token


def revoke_session(token: str) -> None:
    if not token:
        return
    conn = get_db()
    conn.execute(
        "DELETE FROM admin_sessions WHERE token_hash = ?",
        (hash_token(token),),
    )
    conn.commit()
    conn.close()


def revoke_all_sessions(user_pk: int) -> None:
    conn = get_db()
    conn.execute("DELETE FROM admin_sessions WHERE user_pk = ?", (user_pk,))
    conn.commit()
    conn.close()


def get_user_for_session(token: str):
    if not token:
        return None
    conn = get_db()
    row = conn.execute(
        """
        SELECT u.*, s.expires_at AS session_expires
        FROM admin_sessions s
        JOIN admin_users u ON u.id = s.user_pk
        WHERE s.token_hash = ?
        """,
        (hash_token(token),),
    ).fetchone()
    if not row:
        conn.close()
        return None
    expires = datetime.fromisoformat(row["session_expires"])
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < _utcnow():
        conn.execute(
            "DELETE FROM admin_sessions WHERE token_hash = ?",
            (hash_token(token),),
        )
        conn.commit()
        conn.close()
        return None
    conn.close()
    return row


def create_recovery_token(user_pk: int, purpose: str) -> str:
    token = secrets.token_urlsafe(32)
    expires = _utcnow() + timedelta(minutes=RESET_TOKEN_MINUTES)
    conn = get_db()
    # Invalidate previous unused tokens of same purpose
    conn.execute(
        """
        UPDATE admin_recovery_tokens
        SET used_at = ?
        WHERE user_pk = ? AND purpose = ? AND used_at IS NULL
        """,
        (_iso(_utcnow()), user_pk, purpose),
    )
    conn.execute(
        """
        INSERT INTO admin_recovery_tokens
        (token_hash, user_pk, purpose, expires_at, used_at, created_at)
        VALUES (?, ?, ?, ?, NULL, ?)
        """,
        (hash_token(token), user_pk, purpose, _iso(expires), _iso(_utcnow())),
    )
    conn.commit()
    conn.close()
    return token


def consume_recovery_token(token: str, purpose: str):
    conn = get_db()
    row = conn.execute(
        """
        SELECT t.*, u.user_id, u.email
        FROM admin_recovery_tokens t
        JOIN admin_users u ON u.id = t.user_pk
        WHERE t.token_hash = ? AND t.purpose = ?
        """,
        (hash_token(token), purpose),
    ).fetchone()
    if not row or row["used_at"]:
        conn.close()
        return None
    expires = datetime.fromisoformat(row["expires_at"])
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < _utcnow():
        conn.close()
        return None
    conn.execute(
        "UPDATE admin_recovery_tokens SET used_at = ? WHERE token_hash = ?",
        (_iso(_utcnow()), hash_token(token)),
    )
    conn.commit()
    conn.close()
    return row


def set_password(user_pk: int, new_password: str) -> None:
    pw_hash, salt = hash_password(new_password)
    conn = get_db()
    conn.execute(
        """
        UPDATE admin_users
        SET password_hash = ?, salt = ?, updated_at = ?
        WHERE id = ?
        """,
        (pw_hash, salt, _iso(_utcnow()), user_pk),
    )
    conn.commit()
    conn.close()
    revoke_all_sessions(user_pk)


def mail_configured() -> bool:
    """True if Resend API or SMTP credentials are present (not a live health check)."""
    if os.getenv("RESEND_API_KEY") and (os.getenv("SMTP_FROM") or os.getenv("MAIL_FROM")):
        return True
    return bool(os.getenv("SMTP_HOST") and (os.getenv("SMTP_FROM") or os.getenv("MAIL_FROM")))


def smtp_configured() -> bool:
    # Back-compat alias used by /api/admin/auth/status
    return mail_configured()


def app_base_url() -> str:
    raw = (os.getenv("APP_BASE_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN") or "").strip().rstrip("/")
    if not raw:
        return ""
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    return f"https://{raw}"


def new_mail_correlation_id() -> str:
    return secrets.token_hex(8)


def log_mail_event(event: str, *, category: str, correlation_id: str = "", detail: str = "") -> None:
    """Operator-safe mail diagnostics. Never log address, subject, body, token, or raw provider errors."""
    parts = [f"[admin_auth] mail event={event}", f"category={category}"]
    if correlation_id:
        parts.append(f"correlation_id={correlation_id}")
    if detail:
        # Only allow short allow-listed detail tokens (status codes, stage names).
        safe = "".join(ch for ch in detail if ch.isalnum() or ch in ("_", "-", "=", "."))[:64]
        if safe:
            parts.append(f"detail={safe}")
    print(" ".join(parts))


def send_email(to_email: str, subject: str, body: str, *, correlation_id: str = "") -> bool:
    from_addr = (os.getenv("SMTP_FROM") or os.getenv("MAIL_FROM") or "").strip()
    resend_key = (os.getenv("RESEND_API_KEY") or "").strip()
    cid = correlation_id or new_mail_correlation_id()

    # Prefer Resend HTTP API when configured (simpler on Railway than SMTP)
    if resend_key and from_addr:
        import json as _json
        import urllib.error
        import urllib.request

        payload = _json.dumps(
            {
                "from": from_addr,
                "to": [to_email],
                "subject": subject,
                "text": body,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                ok = 200 <= resp.status < 300
                if not ok:
                    log_mail_event(
                        "send",
                        category="provider_http",
                        correlation_id=cid,
                        detail=f"status={resp.status}",
                    )
                else:
                    log_mail_event("send", category="provider_accepted", correlation_id=cid)
                return ok
        except TimeoutError:
            log_mail_event("send", category="provider_timeout", correlation_id=cid)
            return False
        except urllib.error.HTTPError as e:
            log_mail_event(
                "send",
                category="provider_http",
                correlation_id=cid,
                detail=f"status={getattr(e, 'code', 0)}",
            )
            return False
        except urllib.error.URLError as e:
            reason = getattr(e, "reason", None)
            cat = "provider_timeout" if isinstance(reason, TimeoutError) else "provider_exception"
            log_mail_event("send", category=cat, correlation_id=cid)
            return False
        except Exception:
            log_mail_event("send", category="provider_exception", correlation_id=cid)
            return False

    host = os.getenv("SMTP_HOST")
    if not host or not from_addr:
        # Ops visibility only — never print recipient, subject, or body
        log_mail_event("send", category="not_configured", correlation_id=cid)
        return False

    port = int(os.getenv("SMTP_PORT") or "587")
    user = os.getenv("SMTP_USER") or ""
    password = os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD") or ""
    use_tls = (os.getenv("SMTP_TLS") or "true").lower() != "false"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.set_content(body)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            if use_tls:
                server.starttls(context=context)
            if user:
                server.login(user, password)
            server.send_message(msg)
        log_mail_event("send", category="provider_accepted", correlation_id=cid)
        return True
    except (TimeoutError, smtplib.SMTPServerDisconnected):
        log_mail_event("send", category="provider_timeout", correlation_id=cid)
        return False
    except smtplib.SMTPException:
        log_mail_event("send", category="provider_exception", correlation_id=cid)
        return False
    except OSError:
        log_mail_event("send", category="provider_exception", correlation_id=cid)
        return False
    except Exception:
        log_mail_event("send", category="provider_exception", correlation_id=cid)
        return False


def _login_link(token: Optional[str] = None) -> str:
    base = app_base_url()
    path = f"/login?reset={token}" if token else "/login"
    return f"{base}{path}" if base else path


def password_reset_email(email: str, user_id: str, token: str, *, correlation_id: str = "") -> bool:
    link = _login_link(token)
    body = (
        f"Hello,\n\n"
        f"Password reset was requested for ROMI Estimate (User ID: {user_id}).\n"
        f"Open this one-time link within {RESET_TOKEN_MINUTES} minutes, then enter your NEW password:\n\n"
        f"{link}\n\n"
        f"If you did not request this, ignore this email.\n"
    )
    return send_email(email, "ROMI Estimate — password reset", body, correlation_id=correlation_id)


def invite_set_password_email(email: str, user_id: str, token: str, *, correlation_id: str = "") -> bool:
    link = _login_link(token)
    body = (
        f"Hello,\n\n"
        f"Your ROMI Estimate account was created.\n"
        f"User ID: {user_id}\n"
        f"Set your password with this one-time link (valid {RESET_TOKEN_MINUTES} minutes):\n\n"
        f"{link}\n\n"
        f"After that you can sign in at /login and open My Estimates.\n"
    )
    return send_email(email, "ROMI Estimate — set your password", body, correlation_id=correlation_id)


def user_id_reminder_email(email: str, user_id: str, *, correlation_id: str = "") -> bool:
    body = (
        f"Hello,\n\n"
        f"Your ROMI Estimate User ID is: {user_id}\n"
        f"Sign in at /login with this User ID (or this email) and your password.\n\n"
        f"If you did not request this, ignore this email.\n"
    )
    return send_email(email, "ROMI Estimate — User ID reminder", body, correlation_id=correlation_id)


def run_password_reset_delivery(user_pk: int, email: str, user_id: str, correlation_id: str) -> None:
    """Background recovery mail: token + send. Failures stay in operator logs only."""
    try:
        token = create_recovery_token(user_pk, "reset_password")
        ok = password_reset_email(email, user_id, token, correlation_id=correlation_id)
        if not ok:
            log_mail_event(
                "recovery_password",
                category="provider_failed",
                correlation_id=correlation_id,
            )
    except Exception:
        log_mail_event(
            "recovery_password",
            category="provider_exception",
            correlation_id=correlation_id,
        )


def run_user_id_reminder_delivery(email: str, user_id: str, correlation_id: str) -> None:
    """Background User ID reminder. Failures stay in operator logs only."""
    try:
        ok = user_id_reminder_email(email, user_id, correlation_id=correlation_id)
        if not ok:
            log_mail_event(
                "recovery_user_id",
                category="provider_failed",
                correlation_id=correlation_id,
            )
    except Exception:
        log_mail_event(
            "recovery_user_id",
            category="provider_exception",
            correlation_id=correlation_id,
        )
