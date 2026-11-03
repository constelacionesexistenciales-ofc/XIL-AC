import unittest
from pathlib import Path


INSTALLER = Path(__file__).resolve().parents[1] / "installer.iss"


class InstallerArchitectureTests(unittest.TestCase):
    def test_installer_is_limited_to_x64_compatible_systems(self):
        content = INSTALLER.read_text(encoding="utf-8")
        active_lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip() and not line.lstrip().startswith(";")
        ]
        architecture_directives = [
            line.split("=", 1)[1].strip()
            for line in active_lines
            if line.startswith(
                ("ArchitecturesAllowed=", "ArchitecturesInstallIn64BitMode=")
            )
        ]
        self.assertEqual(
            architecture_directives,
            ["x64compatible", "x64compatible"],
        )


if __name__ == "__main__":
    unittest.main()
