"""
Offline acceptance matrix for forgot-password / forgot-user-id anti-enumeration.

No external network. Fake DB rows + fake providers only.
Independent QA must re-run before release; author PASS is not acceptance.
"""

from __future__ import annotations

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import admin_auth  # noqa: E402
import main as app_main  # noqa: E402

KNOWN_EMAIL = "known.user@example.invalid"
UNKNOWN_EMAIL = "unknown.user@example.invalid"
SYNTH_TOKEN = "synth-reset-token-AAAAAAAA"
SYNTH_USER = {
    "id": 42,
    "user_id": "known.user",
    "email": KNOWN_EMAIL,
    "role": "user",
    "display_name": "Known",
}

ENDPOINTS = (
    "/api/admin/auth/forgot-password",
    "/api/admin/auth/forgot-user-id",
)


def _body_for(path: str) -> Dict[str, Any]:
    if path.endswith("forgot-password"):
        return dict(app_main._RECOVERY_ACCEPTED_PASSWORD)
    return dict(app_main._RECOVERY_ACCEPTED_USER_ID)


class RecoveryPrivacyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app: FastAPI = app_main.app
        self.client = TestClient(self.app)
        # Isolate rate-limit counters per test (account-independent IP bucket).
        self._rate_patch = mock.patch.object(admin_auth, "check_rate_limit", return_value=True)
        self._rate_patch.start()

    def tearDown(self) -> None:
        self._rate_patch.stop()

    def _post(self, path: str, email: str) -> Tuple[int, Dict[str, Any], bytes]:
        res = self.client.post(path, json={"email": email})
        try:
            body = res.json()
        except Exception:
            body = {}
        return res.status_code, body, res.content

    def _assert_equal_public(
        self,
        a: Tuple[int, Dict[str, Any], bytes],
        b: Tuple[int, Dict[str, Any], bytes],
    ) -> None:
        self.assertEqual(a[0], b[0], "HTTP status must match for known/unknown")
        self.assertEqual(a[1], b[1], "JSON body must match exactly for known/unknown")
        self.assertEqual(a[2], b[2], "Raw response bytes must match for known/unknown")

    def test_unconfigured_equal_and_no_lookup(self) -> None:
        """Globally unavailable before account lookup; same body for known/unknown."""
        for path in ENDPOINTS:
            with self.subTest(path=path):
                lookup = mock.Mock()
                with mock.patch.object(admin_auth, "mail_configured", return_value=False), mock.patch.object(
                    admin_auth, "find_user_by_email", lookup
                ), mock.patch.object(
                    admin_auth, "run_password_reset_delivery"
                ) as pw, mock.patch.object(
                    admin_auth, "run_user_id_reminder_delivery"
                ) as uid:
                    known = self._post(path, KNOWN_EMAIL)
                    unknown = self._post(path, UNKNOWN_EMAIL)
                self._assert_equal_public(known, unknown)
                self.assertEqual(known[0], 200)
                self.assertEqual(known[1], app_main._RECOVERY_UNAVAILABLE)
                self.assertFalse(known[1]["ok"])
                self.assertEqual(known[1]["email_delivery"], "not_configured")
                # No public provider / Railway / credential instructions
                msg = known[1]["message"].lower()
                for needle in (
                    "railway",
                    "resend",
                    "smtp",
                    "mail_from",
                    "api_key",
                    "password",
                    KNOWN_EMAIL.lower(),
                    "token",
                ):
                    self.assertNotIn(needle, msg)
                lookup.assert_not_called()
                pw.assert_not_called()
                uid.assert_not_called()

    def test_configured_success_equal_known_gets_mail_unknown_zero(self) -> None:
        for path in ENDPOINTS:
            with self.subTest(path=path):
                mail_calls: List[tuple] = []

                def find(email: str):
                    return SYNTH_USER if email == KNOWN_EMAIL else None

                def capture_pw(*args, **kwargs):
                    mail_calls.append(("pw", args, kwargs))

                def capture_uid(*args, **kwargs):
                    mail_calls.append(("uid", args, kwargs))

                with mock.patch.object(admin_auth, "mail_configured", return_value=True), mock.patch.object(
                    admin_auth, "find_user_by_email", side_effect=find
                ), mock.patch.object(
                    admin_auth, "run_password_reset_delivery", side_effect=capture_pw
                ), mock.patch.object(
                    admin_auth, "run_user_id_reminder_delivery", side_effect=capture_uid
                ), mock.patch.object(
                    admin_auth, "create_user"
                ) as create_user:
                    known = self._post(path, KNOWN_EMAIL)
                    unknown = self._post(path, UNKNOWN_EMAIL)

                self._assert_equal_public(known, unknown)
                self.assertEqual(known[0], 200)
                self.assertEqual(known[1], _body_for(path))
                self.assertTrue(known[1]["ok"])
                self.assertEqual(known[1]["email_delivery"], "accepted")
                # Known schedules exactly one delivery; unknown zero; no account creation
                if path.endswith("forgot-password"):
                    self.assertEqual([c[0] for c in mail_calls], ["pw"])
                    self.assertEqual(mail_calls[0][1][0], SYNTH_USER["id"])
                else:
                    self.assertEqual([c[0] for c in mail_calls], ["uid"])
                    self.assertEqual(mail_calls[0][1][0], KNOWN_EMAIL)
                create_user.assert_not_called()

    def test_configured_provider_failure_still_equal(self) -> None:
        """Provider failure must not change public response vs unknown."""

        def find(email: str):
            return SYNTH_USER if email == KNOWN_EMAIL else None

        def fail_pw(*_a, **_k):
            return False

        def fail_uid(*_a, **_k):
            return False

        for path in ENDPOINTS:
            with self.subTest(path=path):
                with mock.patch.object(admin_auth, "mail_configured", return_value=True), mock.patch.object(
                    admin_auth, "find_user_by_email", side_effect=find
                ), mock.patch.object(
                    admin_auth, "create_recovery_token", return_value=SYNTH_TOKEN
                ), mock.patch.object(
                    admin_auth, "password_reset_email", side_effect=fail_pw
                ), mock.patch.object(
                    admin_auth, "user_id_reminder_email", side_effect=fail_uid
                ):
                    # Use real background runners so provider_failed is exercised
                    known = self._post(path, KNOWN_EMAIL)
                    unknown = self._post(path, UNKNOWN_EMAIL)
                self._assert_equal_public(known, unknown)
                self.assertEqual(known[1], _body_for(path))

    def test_configured_provider_exception_still_equal(self) -> None:
        def find(email: str):
            return SYNTH_USER if email == KNOWN_EMAIL else None

        def boom(*_a, **_k):
            raise RuntimeError("raw provider boom should never reach client")

        for path in ENDPOINTS:
            with self.subTest(path=path):
                with mock.patch.object(admin_auth, "mail_configured", return_value=True), mock.patch.object(
                    admin_auth, "find_user_by_email", side_effect=find
                ), mock.patch.object(
                    admin_auth, "create_recovery_token", return_value=SYNTH_TOKEN
                ), mock.patch.object(
                    admin_auth, "password_reset_email", side_effect=boom
                ), mock.patch.object(
                    admin_auth, "user_id_reminder_email", side_effect=boom
                ):
                    known = self._post(path, KNOWN_EMAIL)
                    unknown = self._post(path, UNKNOWN_EMAIL)
                self._assert_equal_public(known, unknown)
                self.assertEqual(known[1], _body_for(path))
                self.assertNotIn("raw provider boom", known[1]["message"])

    def test_handler_lookup_exception_equal_to_unknown(self) -> None:
        def find_boom(email: str):
            if email == KNOWN_EMAIL:
                raise RuntimeError("db blew up")
            return None

        for path in ENDPOINTS:
            with self.subTest(path=path):
                with mock.patch.object(admin_auth, "mail_configured", return_value=True), mock.patch.object(
                    admin_auth, "find_user_by_email", side_effect=find_boom
                ), mock.patch.object(
                    admin_auth, "run_password_reset_delivery"
                ) as pw, mock.patch.object(
                    admin_auth, "run_user_id_reminder_delivery"
                ) as uid:
                    known = self._post(path, KNOWN_EMAIL)
                    unknown = self._post(path, UNKNOWN_EMAIL)
                self._assert_equal_public(known, unknown)
                self.assertEqual(known[1], _body_for(path))
                pw.assert_not_called()
                uid.assert_not_called()

    def test_malformed_email_stable_validation(self) -> None:
        for path in ENDPOINTS:
            with self.subTest(path=path):
                with mock.patch.object(admin_auth, "mail_configured", return_value=True), mock.patch.object(
                    admin_auth, "find_user_by_email"
                ) as lookup:
                    a = self.client.post(path, json={"email": "not-an-email"})
                    b = self.client.post(path, json={"email": "also-bad"})
                    missing = self.client.post(path, json={})
                self.assertEqual(a.status_code, 400)
                self.assertEqual(b.status_code, 400)
                self.assertEqual(a.json(), b.json())
                self.assertEqual(a.json()["detail"], "Enter a valid email address")
                self.assertEqual(missing.status_code, 422)
                lookup.assert_not_called()

    def test_rate_limit_account_independent(self) -> None:
        self._rate_patch.stop()
        try:
            with mock.patch.object(admin_auth, "check_rate_limit", return_value=False), mock.patch.object(
                admin_auth, "mail_configured", return_value=True
            ), mock.patch.object(admin_auth, "find_user_by_email") as lookup:
                for path in ENDPOINTS:
                    with self.subTest(path=path):
                        k = self.client.post(path, json={"email": KNOWN_EMAIL})
                        u = self.client.post(path, json={"email": UNKNOWN_EMAIL})
                        self.assertEqual(k.status_code, 429)
                        self.assertEqual(u.status_code, 429)
                        self.assertEqual(k.json(), u.json())
                lookup.assert_not_called()
        finally:
            self._rate_patch = mock.patch.object(admin_auth, "check_rate_limit", return_value=True)
            self._rate_patch.start()

    def test_logs_omit_secrets_and_addresses(self) -> None:
        buf = io.StringIO()
        def find(email: str):
            return SYNTH_USER if email == KNOWN_EMAIL else None

        with mock.patch.object(admin_auth, "mail_configured", return_value=True), mock.patch.object(
            admin_auth, "find_user_by_email", side_effect=find
        ), mock.patch.object(
            admin_auth, "create_recovery_token", return_value=SYNTH_TOKEN
        ), mock.patch.object(
            admin_auth, "password_reset_email", return_value=True
        ), mock.patch.object(
            admin_auth, "user_id_reminder_email", return_value=True
        ), redirect_stdout(buf):
            self._post("/api/admin/auth/forgot-password", KNOWN_EMAIL)
            self._post("/api/admin/auth/forgot-user-id", UNKNOWN_EMAIL)
            # Direct send_email not_configured / exception paths
            with mock.patch.dict(os.environ, {"RESEND_API_KEY": "", "SMTP_HOST": "", "MAIL_FROM": "", "SMTP_FROM": ""}, clear=False):
                admin_auth.send_email(
                    "leak@example.invalid",
                    "SECRET-SUBJECT",
                    f"body with token={SYNTH_TOKEN}",
                    correlation_id="cidtest01",
                )
            with mock.patch.dict(
                os.environ,
                {"RESEND_API_KEY": "re_test", "MAIL_FROM": "ops@example.invalid", "SMTP_FROM": ""},
                clear=False,
            ), mock.patch("urllib.request.urlopen", side_effect=TimeoutError()):
                admin_auth.send_email(
                    "leak@example.invalid",
                    "SECRET-SUBJECT",
                    f"body with token={SYNTH_TOKEN}",
                    correlation_id="cidtest02",
                )

        logged = buf.getvalue()
        for needle in (
            KNOWN_EMAIL,
            UNKNOWN_EMAIL,
            "leak@example.invalid",
            SYNTH_TOKEN,
            "SECRET-SUBJECT",
            "body with token",
            "re_test",
        ):
            self.assertNotIn(needle, logged)
        self.assertIn("category=not_configured", logged)
        self.assertIn("category=provider_timeout", logged)

    def test_asgi_response_emitted_before_mail_send(self) -> None:
        """Inspect ASGI emission order: response completes before background mail runs."""
        events: List[str] = []
        release = mock.Mock()

        def find(email: str):
            return SYNTH_USER if email == KNOWN_EMAIL else None

        def slow_delivery(*_a, **_k):
            events.append("mail_send")

        async def run() -> None:
            scope = {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "POST",
                "scheme": "http",
                "path": "/api/admin/auth/forgot-password",
                "raw_path": b"/api/admin/auth/forgot-password",
                "query_string": b"",
                "headers": [(b"content-type", b"application/json"), (b"host", b"test")],
                "client": ("127.0.0.1", 123),
                "server": ("test", 80),
            }
            body = json.dumps({"email": KNOWN_EMAIL}).encode()
            state = {"sent": False}

            async def receive():
                if not state["sent"]:
                    state["sent"] = True
                    return {"type": "http.request", "body": body, "more_body": False}
                return {"type": "http.request", "body": b"", "more_body": False}

            async def send(message):
                if message["type"] == "http.response.start":
                    events.append("response_start")
                elif message["type"] == "http.response.body" and not message.get("more_body", False):
                    events.append("response_body_done")

            with mock.patch.object(admin_auth, "mail_configured", return_value=True), mock.patch.object(
                admin_auth, "find_user_by_email", side_effect=find
            ), mock.patch.object(
                admin_auth, "run_password_reset_delivery", side_effect=slow_delivery
            ):
                await self.app(scope, receive, send)

        import anyio

        anyio.run(run)
        self.assertIn("response_start", events)
        self.assertIn("response_body_done", events)
        self.assertIn("mail_send", events)
        self.assertLess(events.index("response_body_done"), events.index("mail_send"))
        # Unknown: response only, zero mail
        events.clear()

        async def run_unknown() -> None:
            scope = {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "POST",
                "scheme": "http",
                "path": "/api/admin/auth/forgot-password",
                "raw_path": b"/api/admin/auth/forgot-password",
                "query_string": b"",
                "headers": [(b"content-type", b"application/json"), (b"host", b"test")],
                "client": ("127.0.0.1", 124),
                "server": ("test", 80),
            }
            body = json.dumps({"email": UNKNOWN_EMAIL}).encode()
            state = {"sent": False}

            async def receive():
                if not state["sent"]:
                    state["sent"] = True
                    return {"type": "http.request", "body": body, "more_body": False}
                return {"type": "http.request", "body": b"", "more_body": False}

            async def send(message):
                if message["type"] == "http.response.start":
                    events.append("response_start")
                elif message["type"] == "http.response.body" and not message.get("more_body", False):
                    events.append("response_body_done")

            with mock.patch.object(admin_auth, "mail_configured", return_value=True), mock.patch.object(
                admin_auth, "find_user_by_email", return_value=None
            ), mock.patch.object(
                admin_auth, "run_password_reset_delivery", side_effect=slow_delivery
            ):
                await self.app(scope, receive, send)

        anyio.run(run_unknown)
        self.assertEqual(events, ["response_start", "response_body_done"])

    def test_smtp_and_resend_exception_categories(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf), mock.patch.dict(
            os.environ,
            {
                "RESEND_API_KEY": "re_x",
                "MAIL_FROM": "ops@example.invalid",
                "SMTP_FROM": "",
                "SMTP_HOST": "",
            },
            clear=False,
        ), mock.patch("urllib.request.urlopen", side_effect=Exception("secret-resend-trace")):
            ok = admin_auth.send_email("a@b.invalid", "subj", "body", correlation_id="c1")
            self.assertFalse(ok)

        with redirect_stdout(buf), mock.patch.dict(
            os.environ,
            {
                "RESEND_API_KEY": "",
                "MAIL_FROM": "ops@example.invalid",
                "SMTP_FROM": "ops@example.invalid",
                "SMTP_HOST": "smtp.example.invalid",
                "SMTP_PORT": "587",
                "SMTP_USER": "u",
                "SMTP_PASS": "p",
            },
            clear=False,
        ), mock.patch("smtplib.SMTP", side_effect=OSError("secret-smtp-trace")):
            ok = admin_auth.send_email("a@b.invalid", "subj", "body", correlation_id="c2")
            self.assertFalse(ok)

        logged = buf.getvalue()
        self.assertIn("category=provider_exception", logged)
        self.assertNotIn("secret-resend-trace", logged)
        self.assertNotIn("secret-smtp-trace", logged)
        self.assertNotIn("a@b.invalid", logged)

    def test_configuration_presence_is_not_provider_health(self) -> None:
        """mail_configured True with failing provider still returns accepted publicly."""
        def find(email: str):
            return SYNTH_USER if email == KNOWN_EMAIL else None

        with mock.patch.object(admin_auth, "mail_configured", return_value=True), mock.patch.object(
            admin_auth, "find_user_by_email", side_effect=find
        ), mock.patch.object(
            admin_auth, "create_recovery_token", return_value=SYNTH_TOKEN
        ), mock.patch.object(
            admin_auth, "password_reset_email", return_value=False
        ):
            known = self._post("/api/admin/auth/forgot-password", KNOWN_EMAIL)
            unknown = self._post("/api/admin/auth/forgot-password", UNKNOWN_EMAIL)
        self._assert_equal_public(known, unknown)
        self.assertEqual(known[1]["email_delivery"], "accepted")

    def test_frontend_has_no_account_specific_recovery_states(self) -> None:
        root = BACKEND_DIR.parent / "frontend"
        for name in ("login.html", "admin.html"):
            text = (root / name).read_text(encoding="utf-8")
            with self.subTest(file=name):
                self.assertNotIn("email_delivery", text)
                self.assertNotIn("not_configured", text)
                # Forgot handlers only surface message + ok — no known/unknown branching
                self.assertNotIn("registered user", text.lower())
                self.assertIn("forgot-password", text)
                self.assertIn("forgot-user-id", text)


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RecoveryPrivacyTests)
    return suite


if __name__ == "__main__":
    # Exact command (from repo root or backend/):
    #   python -m unittest backend.tests.test_recovery_privacy -v
    # or:
    #   cd backend && python -m unittest tests.test_recovery_privacy -v
    unittest.main(verbosity=2)
