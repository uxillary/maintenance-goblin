"""Release metadata consistency checks."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseMetadataTests(unittest.TestCase):
    def test_versions_are_consistent(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        source = (ROOT / "src" / "maintenance_goblin.py").read_text(encoding="utf-8")
        versionfile = (ROOT / "versionfile.txt").read_text(encoding="utf-8")
        installer = (ROOT / "installer.nsi").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        project_version = re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE)
        source_version = re.search(r'^__version__ = "([^"]+)"', source, re.MULTILINE)
        file_version = re.search(
            r"StringStruct\('FileVersion', '([^']+)'\)", versionfile
        )
        product_version = re.search(
            r"StringStruct\('ProductVersion', '([^']+)'\)", versionfile
        )
        numeric_file_version = re.search(r"filevers=\(([^)]+)\)", versionfile)
        installer_version = re.search(
            r'^!define APP_VERSION "([^"]+)"', installer, re.MULTILINE
        )
        changelog_version = re.search(r"^## \[([^]]+)]", changelog, re.MULTILINE)

        self.assertIsNotNone(project_version)
        self.assertIsNotNone(source_version)
        self.assertIsNotNone(file_version)
        self.assertIsNotNone(product_version)
        self.assertIsNotNone(numeric_file_version)
        self.assertIsNotNone(installer_version)
        self.assertIsNotNone(changelog_version)
        self.assertEqual(
            {
                project_version.group(1),
                source_version.group(1),
                file_version.group(1),
                product_version.group(1),
                installer_version.group(1),
                changelog_version.group(1),
            },
            {project_version.group(1)},
        )
        expected_tuple = ", ".join(project_version.group(1).split(".") + ["0"])
        self.assertEqual(numeric_file_version.group(1), expected_tuple)


if __name__ == "__main__":
    unittest.main()
