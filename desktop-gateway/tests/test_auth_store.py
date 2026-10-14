import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from auth_store import (
    LOCK_SECONDS,
    MAX_FAILURES,
    authenticate,
    create_initial_user,
    has_users,
)


TEST_USERNAME = "synthetic-test-user"
TEST_PASSWORD = "TestOnly-Password-2026"
TEST_PIN = "739152"


class AuthStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "auth.dat"
        create_initial_user(TEST_USERNAME, TEST_PASSWORD, TEST_PIN, self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_password_login(self):
        ok, _ = authenticate(TEST_USERNAME, TEST_PASSWORD, "password", self.path)
        self.assertTrue(ok)

    def test_pin_login(self):
        ok, _ = authenticate(TEST_USERNAME.upper(), TEST_PIN, "pin", self.path)
        self.assertTrue(ok)

    def test_wrong_credential_rejected(self):
        ok, _ = authenticate(TEST_USERNAME, "000000", "pin", self.path)
        self.assertFalse(ok)

    def test_credentials_not_stored_in_plain_text(self):
        raw = self.path.read_bytes()
        self.assertNotIn(TEST_PASSWORD.encode(), raw)
        self.assertNotIn(TEST_PIN.encode(), raw)

    def test_first_user_required_and_unique(self):
        self.assertTrue(has_users(self.path))
        with self.assertRaises(ValueError):
            create_initial_user(
                "second-synthetic-user",
                "Another-Test-Password-2026",
                "482615",
                self.path,
            )

    def test_password_minimum_length(self):
        with self.assertRaises(ValueError):
            create_initial_user(
                "other-synthetic-user",
                "short",
                "482615",
                Path(self.tmp.name) / "other.dat",
            )

    def test_lockout_after_maximum_failed_attempts(self):
        with patch("auth_store.time.time", return_value=1_000):
            for _ in range(MAX_FAILURES):
                ok, _ = authenticate(TEST_USERNAME, "wrong-credential", "password", self.path)
                self.assertFalse(ok)

            ok, message = authenticate(TEST_USERNAME, TEST_PASSWORD, "password", self.path)
            self.assertFalse(ok)
            self.assertIn("bloqueado", message)

        with patch("auth_store.time.time", return_value=1_000 + LOCK_SECONDS + 1):
            ok, _ = authenticate(TEST_USERNAME, TEST_PASSWORD, "password", self.path)
            self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
