import tempfile
import unittest
from pathlib import Path

from auth_store import authenticate, create_initial_user, has_users


class AuthStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "auth.json"
        create_initial_user("Alexis Pittaluga", "UnaClaveSegura-2026", "2411", self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_password_login(self):
        ok, _ = authenticate("Alexis Pittaluga", "UnaClaveSegura-2026", "password", self.path)
        self.assertTrue(ok)

    def test_pin_login(self):
        ok, _ = authenticate("alexis pittaluga", "2411", "pin", self.path)
        self.assertTrue(ok)

    def test_wrong_credential_rejected(self):
        ok, _ = authenticate("Alexis Pittaluga", "0000", "pin", self.path)
        self.assertFalse(ok)

    def test_secrets_not_stored_in_plain_text(self):
        raw = self.path.read_text(encoding="utf-8")
        self.assertNotIn("UnaClaveSegura-2026", raw)
        self.assertNotIn('"2411"', raw)

    def test_first_user_required_and_unique(self):
        self.assertTrue(has_users(self.path))
        with self.assertRaises(ValueError):
            create_initial_user("Other", "OtraClaveSegura-2026", "1234", self.path)

    def test_password_minimum_length(self):
        with self.assertRaises(ValueError):
            create_initial_user("Other", "corta", "1234", Path(self.tmp.name) / "other.json")


if __name__ == "__main__":
    unittest.main()
