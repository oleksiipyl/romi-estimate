"""
BLOCKER 2: public access-request responses must be identity-invariant.

Offline synthetic DB + provider stubs. No real email/network.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple
from unittest import mock

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import admin_auth  # noqa: E402
import database  # noqa: E402
import main as app_main  # noqa: E402

NEW_EMAIL = "new.staff@example.invalid"
PENDING_EMAIL = "pending.staff@example.invalid"
KNOWN_EMAIL = "known.staff@example.invalid"


class AccessRequestPrivacyTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self.db_path = self._tmp.name
        self._db_patch = mock.patch.object(database, "DB_PATH", self.db_path)
        self._db_patch.start()
        self._getdb_aa = mock.patch.object(admin_auth, "get_db", database.get_db)
        self._getdb_aa.start()
        admin_auth.ensure_admin_tables()

        # Seed a known account and a pending request in the isolated DB
        admin_auth.create_user(
            user_id="known.staff",
            email=KNOWN_EMAIL,
            display_name="Known Staff",
            password="not-used-in-tests-xx",
            send_invite=False,
        )
        admin_auth.create_access_request(
            email=PENDING_EMAIL,
            display_name="Pending Staff",
            desired_user_id="pending.staff",
            note="already pending",
        )

        self.client = TestClient(app_main.app)
        self._rate = mock.patch.object(admin_auth, "check_rate_limit", return_value=True)
        self._rate.start()

    def tearDown(self) -> None:
        self._rate.stop()
        self._getdb_aa.stop()
        self._db_patch.stop()
        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    def _post(self, email: str, name: str = "Staff") -> Tuple[int, Dict[str, Any], bytes]:
        res = self.client.post(
            "/api/access-requests",
            json={
                "email": email,
                "display_name": name,
                "desired_user_id": email.split("@")[0],
                "note": "synthetic",
            },
        )
        try:
            body = res.json()
        except Exception:
            body = {}
        return res.status_code, body, res.content

    def test_known_pending_new_public_equality(self) -> None:
        notify_calls: List[tuple] = []

        def capture_notify(*args, **kwargs):
            notify_calls.append((args, kwargs))

        with mock.patch.object(
            admin_auth, "notify_owner_of_access_request", side_effect=capture_notify
        ), mock.patch.object(admin_auth, "create_user") as create_user:
            known = self._post(KNOWN_EMAIL)
            pending = self._post(PENDING_EMAIL)
            fresh = self._post(NEW_EMAIL)

        for label, resp in (("known", known), ("pending", pending), ("new", fresh)):
            self.assertEqual(resp[0], 200, label)
            self.assertEqual(resp[1], app_main._ACCESS_REQUEST_ACCEPTED, label)
            self.assertNotIn("id", resp[1])
            self.assertNotIn("owner_notified", resp[1])
            self.assertNotIn("already exists", json.dumps(resp[1]).lower())
            self.assertNotIn("pending request", json.dumps(resp[1]).lower())

        self.assertEqual(known[1], pending[1])
        self.assertEqual(pending[1], fresh[1])
        self.assertEqual(known[2], pending[2])
        self.assertEqual(pending[2], fresh[2])

        # Only the new identity schedules owner notify; no duplicate accounts
        self.assertEqual(len(notify_calls), 1)
        self.assertEqual(notify_calls[0][0][0], NEW_EMAIL)
        create_user.assert_not_called()

        # Pending row count for PENDING_EMAIL stays 1; NEW gets exactly 1
        rows = admin_auth.list_access_requests("pending")
        pending_count = sum(1 for r in rows if r["email"] == PENDING_EMAIL)
        new_count = sum(1 for r in rows if r["email"] == NEW_EMAIL)
        self.assertEqual(pending_count, 1)
        self.assertEqual(new_count, 1)
        self.assertIsNone(admin_auth.find_user_by_email(NEW_EMAIL))

    def test_provider_failure_and_exception_do_not_change_public_body(self) -> None:
        def fail_send(*_a, **_k):
            return False

        def boom(*_a, **_k):
            raise RuntimeError("secret-provider-trace")

        with mock.patch.object(admin_auth, "send_email", side_effect=fail_send):
            # Force a new create path with real background notify runner
            a = self._post("fail.case@example.invalid", "Fail Case")
        with mock.patch.object(admin_auth, "send_email", side_effect=boom):
            b = self._post("boom.case@example.invalid", "Boom Case")

        for resp in (a, b):
            self.assertEqual(resp[0], 200)
            self.assertEqual(resp[1], app_main._ACCESS_REQUEST_ACCEPTED)
            self.assertNotIn("secret-provider-trace", json.dumps(resp[1]))

    def test_handler_exception_still_uniform(self) -> None:
        with mock.patch.object(
            admin_auth, "create_access_request", side_effect=RuntimeError("db-fail")
        ):
            a = self._post(NEW_EMAIL)
            b = self._post(KNOWN_EMAIL)
        self.assertEqual(a[0], b[0])
        self.assertEqual(a[1], b[1])
        self.assertEqual(a[1], app_main._ACCESS_REQUEST_ACCEPTED)

    def test_validation_still_account_independent(self) -> None:
        bad = self.client.post(
            "/api/access-requests",
            json={"email": "not-an-email", "display_name": "X"},
        )
        missing = self.client.post(
            "/api/access-requests",
            json={"email": "ok@example.invalid", "display_name": ""},
        )
        self.assertEqual(bad.status_code, 400)
        self.assertEqual(missing.status_code, 400)
        self.assertNotIn("already exists", bad.json().get("detail", "").lower())

    def test_asgi_response_before_owner_notify(self) -> None:
        events: List[str] = []

        def notify(*_a, **_k):
            events.append("notify")

        async def run(email: str) -> None:
            scope = {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "POST",
                "scheme": "http",
                "path": "/api/access-requests",
                "raw_path": b"/api/access-requests",
                "query_string": b"",
                "headers": [(b"content-type", b"application/json"), (b"host", b"test")],
                "client": ("127.0.0.1", 125),
                "server": ("test", 80),
            }
            body = json.dumps(
                {
                    "email": email,
                    "display_name": "ASGI Staff",
                    "desired_user_id": "asgi.staff",
                    "note": "",
                }
            ).encode()
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

            with mock.patch.object(
                admin_auth, "notify_owner_of_access_request", side_effect=notify
            ):
                await app_main.app(scope, receive, send)

        import anyio

        events.clear()
        anyio.run(run, "asgi.new@example.invalid")
        self.assertLess(events.index("response_body_done"), events.index("notify"))

        events.clear()
        anyio.run(run, KNOWN_EMAIL)
        self.assertEqual(events, ["response_start", "response_body_done"])

    def test_admin_approve_workflow_preserved(self) -> None:
        # Create pending via internal helper, approve as synthetic superadmin
        created = admin_auth.create_access_request(
            email="approve.me@example.invalid",
            display_name="Approve Me",
            desired_user_id="approve.me",
        )
        self.assertEqual(created["outcome"], "created")
        owner = admin_auth.create_user(
            user_id="qa.super",
            email="qa.super@example.invalid",
            role="superadmin",
            password="qa-super-password-xx",
            send_invite=False,
        )
        # create_user returns dict; decide expects row-like with id
        reviewer = admin_auth.find_user_by_login("qa.super")
        with mock.patch.object(admin_auth, "send_email", return_value=True), mock.patch.object(
            admin_auth, "invite_set_password_email", return_value=True
        ):
            decided = admin_auth.decide_access_request(
                created["id"], approve=True, reviewer=reviewer
            )
        self.assertEqual(decided["status"], "approved")
        self.assertIsNotNone(decided.get("user"))
        self.assertIsNotNone(admin_auth.find_user_by_email("approve.me@example.invalid"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
