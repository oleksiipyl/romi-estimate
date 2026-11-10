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
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
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
    conn.commit()
    conn.close()


def seed_admin_user_from_env() -> None:
    """Create first admin from ADMIN_EMAIL + ADMIN_PASSWORD (+ optional ADMIN_USER_ID)."""
    email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD") or ""
    user_id = (os.getenv("ADMIN_USER_ID") or "alex").strip().lower()
    if not email or not password:
        return

    conn = get_db()
    row = conn.execute("SELECT id FROM admin_users LIMIT 1").fetchone()
    if row:
        conn.close()
        return

    pw_hash, salt = hash_password(password)
    now = _iso(_utcnow())
    conn.execute(
        """
        INSERT INTO admin_users (user_id, email, password_hash, salt, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, email, pw_hash, salt, now, now),
    )
    conn.commit()
    conn.close()


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


def smtp_configured() -> bool:
    return bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_FROM"))


def app_base_url() -> str:
    return (os.getenv("APP_BASE_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN") or "").rstrip("/")


def send_email(to_email: str, subject: str, body: str) -> bool:
    host = os.getenv("SMTP_HOST")
    from_addr = os.getenv("SMTP_FROM")
    if not host or not from_addr:
        # Ops visibility only — never return link to client
        print(f"[admin_auth] SMTP not configured. Would email {to_email}: {subject}")
        print(body)
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
    with smtplib.SMTP(host, port, timeout=20) as server:
        if use_tls:
            server.starttls(context=context)
        if user:
            server.login(user, password)
        server.send_message(msg)
    return True


def password_reset_email(email: str, user_id: str, token: str) -> bool:
    base = app_base_url()
    link = f"{base}/admin?reset={token}" if base else f"/admin?reset={token}"
    body = (
        f"Hello,\n\n"
        f"Password reset was requested for ROMI Estimate admin (user ID: {user_id}).\n"
        f"Open this one-time link within {RESET_TOKEN_MINUTES} minutes:\n\n"
        f"{link}\n\n"
        f"If you did not request this, ignore this email.\n"
    )
    return send_email(email, "ROMI Estimate — password reset", body)


def user_id_reminder_email(email: str, user_id: str) -> bool:
    body = (
        f"Hello,\n\n"
        f"Your ROMI Estimate admin User ID is: {user_id}\n"
        f"Sign in at /admin with this User ID (or this email) and your password.\n\n"
        f"If you did not request this, ignore this email.\n"
    )
    return send_email(email, "ROMI Estimate — User ID reminder", body)
