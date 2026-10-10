import unittest

from privacy_engine import review_text

class PrivacyEngineTests(unittest.TestCase):
    def test_email_is_flagged_without_echoing_value(self):
        secret = "alexis@example.com"
        result = review_text("Contacto: " + secret)
        self.assertEqual(result.decision, "REVIEW_REQUIRED")
        self.assertIn("correo electrónico", result.categories)
        self.assertNotIn(secret, repr(result))

    def test_high_sensitivity_is_denied(self):
        result = review_text("La persona menciona ideación suicida.")
        self.assertEqual(result.decision, "DENY")
        self.assertEqual(result.risk, "high")

    def test_neutral_text_still_cannot_be_sent(self):
        result = review_text("Quiero investigar cómo se construyen las decisiones en los vínculos.")
        self.assertEqual(result.decision, "REVIEW_REQUIRED")
        self.assertEqual(result.risk, "no_signal_detected")
        self.assertIn("no prueba", result.message)

    def test_empty_text_fails_closed(self):
        result = review_text(" ")
        self.assertEqual(result.decision, "REVIEW_REQUIRED")
        self.assertEqual(result.risk, "unknown")

if __name__ == "__main__":
    unittest.main()
