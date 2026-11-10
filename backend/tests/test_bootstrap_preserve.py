"""
BLOCKER 1 regression: seed_admin_user_from_env must not revert passwords or kill sessions.

Isolated tempfile SQLite. No production env/credential changes, no network.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import admin_auth  # noqa: E402
import database  # noqa: E402


BOOT_PASSWORD = "bootstrap-password-AAAA"
CHANGED_PASSWORD = "changed-password-BBBB"


class BootstrapPreserveTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self.db_path = self._tmp.name
        self._db_patch = mock.patch.object(database, "DB_PATH", self.db_path)
        self._db_patch.start()
        # admin_auth imports get_db from database by name — patch both modules' binding
        self._getdb_patch = mock.patch.object(admin_auth, "get_db", database.get_db)
        self._getdb_patch.start()
        admin_auth.ensure_admin_tables()

    def tearDown(self) -> None:
        self._getdb_patch.stop()
        self._db_patch.stop()
        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    def test_repeated_boot_preserves_changed_password_and_session(self) -> None:
        env = {
            "ADMIN_EMAIL": "owner@example.invalid",
            "ADMIN_USER_ID": "owner.test",
            "ADMIN_DISPLAY_NAME": "Owner Test",
            "ADMIN_PASSWORD": BOOT_PASSWORD,
        }
        with mock.patch.dict(os.environ, env, clear=False), mock.patch.object(
            admin_auth, "invite_set_password_email", return_value=False
        ):
            admin_auth.seed_admin_user_from_env()
            user = admin_auth.find_user_by_login("owner.test")
            self.assertIsNotNone(user)
            self.assertTrue(
                admin_auth.verify_password(BOOT_PASSWORD, user["password_hash"], user["salt"])
            )

            admin_auth.set_password(user["id"], CHANGED_PASSWORD)
            user_after_change = admin_auth.find_user_by_login("owner.test")
            changed_password_valid_before_boot = admin_auth.verify_password(
                CHANGED_PASSWORD,
                user_after_change["password_hash"],
                user_after_change["salt"],
            )
            self.assertTrue(changed_password_valid_before_boot)

            token = admin_auth.create_session(user["id"])
            self.assertIsNotNone(admin_auth.get_user_for_session(token))

            # Second boot with same ADMIN_PASSWORD still in env — must not revert
            admin_auth.seed_admin_user_from_env()
            user_after_boot = admin_auth.find_user_by_login("owner.test")
            after_boot = admin_auth.verify_password(
                CHANGED_PASSWORD,
                user_after_boot["password_hash"],
                user_after_boot["salt"],
            )
            bootstrap_password_restored = admin_auth.verify_password(
                BOOT_PASSWORD,
                user_after_boot["password_hash"],
                user_after_boot["salt"],
            )
            session_survives_boot = admin_auth.get_user_for_session(token) is not None

            self.assertTrue(after_boot, "changed password must remain valid after repeated boot")
            self.assertFalse(
                bootstrap_password_restored,
                "ADMIN_PASSWORD must not implicitly restore after password change",
            )
            self.assertTrue(session_survives_boot, "sessions must survive repeated boot")

    def test_first_boot_uses_admin_password_once(self) -> None:
        env = {
            "ADMIN_EMAIL": "fresh@example.invalid",
            "ADMIN_USER_ID": "fresh.owner",
            "ADMIN_DISPLAY_NAME": "Fresh",
            "ADMIN_PASSWORD": BOOT_PASSWORD,
        }
        with mock.patch.dict(os.environ, env, clear=False):
            admin_auth.seed_admin_user_from_env()
            user = admin_auth.find_user_by_login("fresh.owner")
            self.assertTrue(
                admin_auth.verify_password(BOOT_PASSWORD, user["password_hash"], user["salt"])
            )
            # Third boot still preserves first-boot password (never changed by user)
            admin_auth.seed_admin_user_from_env()
            user2 = admin_auth.find_user_by_login("fresh.owner")
            self.assertTrue(
                admin_auth.verify_password(BOOT_PASSWORD, user2["password_hash"], user2["salt"])
            )
            self.assertEqual(user["id"], user2["id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
