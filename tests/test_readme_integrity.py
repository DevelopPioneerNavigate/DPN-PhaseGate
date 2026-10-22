"""Readme link and branding safety tests; all resources are synthetic."""
import tempfile
import unittest
from pathlib import Path

from tools.validate_readme import check_repo


class DocumentationIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "assets").mkdir()
        self.page = self.root / "README.md"
        self.page.write_text(
            "# DPN PHASEGATE\nResearch unverified measurement demonstration\n"
            '<img src="assets/icon.svg">\n', encoding="utf-8"
        )
        self.icon = self.root / "assets/icon.svg"
        self.icon.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'
            '<title>Experimental concept only</title><circle cx="10" cy="10" r="7"/></svg>',
            encoding="utf-8"
        )

    def test_valid_page_and_svg(self):
        self.assertEqual(check_repo(self.root, pages=["README.md"]), [])

    def test_broken_document_link(self):
        self.page.write_text(self.page.read_text() + "\n[Missing](docs/not-found.md)", encoding="utf-8")
        self.assertTrue(any("broken internal link" in issue for issue in check_repo(self.root, pages=["README.md"])))

    def test_reject_external_script_asset(self):
        self.icon.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'
            '<script>alert(1)</script></svg>', encoding="utf-8"
        )
        self.assertTrue(any("unsafe/externally dependent" in issue for issue in check_repo(self.root, pages=["README.md"])))

    def test_reject_path_traversal(self):
        self.page.write_text(self.page.read_text() + "\n[Out](../outside.md)", encoding="utf-8")
        self.assertTrue(any("escapes repository" in issue for issue in check_repo(self.root, pages=["README.md"])))

    def test_missing_context(self):
        self.page.write_text("# Nice project\n<img src=\"assets/icon.svg\">", encoding="utf-8")
        self.assertTrue(any("research context" in issue for issue in check_repo(self.root, pages=["README.md"])))

    def test_does_not_reject_https_badges(self):
        self.page.write_text(self.page.read_text() + "\n[CI](https://github.com/example/repo)", encoding="utf-8")
        self.assertEqual(check_repo(self.root, pages=["README.md"]), [])


if __name__ == "__main__":
    unittest.main()
