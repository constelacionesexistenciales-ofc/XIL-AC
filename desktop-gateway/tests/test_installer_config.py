import re
import unittest
from pathlib import Path


INSTALLER = Path(__file__).resolve().parents[1] / "installer.iss"


class InstallerArchitectureTests(unittest.TestCase):
    def test_installer_is_limited_to_x64_compatible_systems(self):
        content = INSTALLER.read_text(encoding="utf-8")
        self.assertRegex(content, r"(?m)^ArchitecturesAllowed=x64compatible$")
        self.assertRegex(
            content,
            r"(?m)^ArchitecturesInstallIn64BitMode=x64compatible$",
        )

    def test_deprecated_x64_architecture_identifier_is_not_used(self):
        content = INSTALLER.read_text(encoding="utf-8")
        deprecated_identifiers = re.findall(
            r"(?<![A-Za-z0-9_])x64(?![A-Za-z0-9_])",
            content,
        )
        self.assertEqual(deprecated_identifiers, [])


if __name__ == "__main__":
    unittest.main()
