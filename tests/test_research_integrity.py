"""Regression tests for record integrity. Does not validate extraordinary physics."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_research import audit, utc_timestamp


class ResearchIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        for folder in ["data/literature", "data/hypotheses", "data/experiments"]:
            (self.root / folder).mkdir(parents=True)
        self.sources = {"version": 1, "reviewed_on": "2026-10-22", "sources": [
            {"id": "SRC-001", "title": "Test publication", "authors": "Researcher",
             "year": 2020, "type": "peer_reviewed", "doi": "10.1000/test",
             "url": "https://example.org/paper", "claim": "Observed test information only",
             "non_claim": "No physical transfer demonstrated"}]}
        self.hypotheses = {"version": 1, "hypotheses": [
            {"id": "H-PG-001", "title": "Controlled null baseline",
             "status": "proposed", "source_ids": ["SRC-001"],
             "statement": "Null baseline has no verified object transfer",
             "falsifier": "A replicated physical object crossing",
             "prediction": "No macroscopic transfer occurs in sham",
             "limitations": "Only an instrumentation null test"}]}
        self.manifest = {"version": 1, "experiments": []}
        self.save()

    def write(self, path, data):
        (self.root / path).write_text(json.dumps(data), encoding="utf-8")

    def save(self):
        self.write("data/literature/sources.json", self.sources)
        self.write("data/hypotheses/hypotheses.json", self.hypotheses)
        self.write("data/experiments/manifest.json", self.manifest)

    def test_valid_empty_real_run_manifest(self):
        self.assertEqual(audit(self.root), [])

    def test_catches_duplicate_sources(self):
        self.sources["sources"].append(dict(self.sources["sources"][0]))
        self.save()
        self.assertTrue(any("duplicate source" in error for error in audit(self.root)))

    def test_catches_unknown_source_reference(self):
        self.hypotheses["hypotheses"][0]["source_ids"] = ["SRC-999"]
        self.save()
        self.assertTrue(any("unknown source" in error for error in audit(self.root)))

    def test_catches_missing_run(self):
        self.manifest["experiments"].append("PG-20261022-001")
        self.save()
        self.assertTrue(any("cannot load JSON" in error for error in audit(self.root)))

    def test_catches_unregistered_run_file(self):
        self.write("data/experiments/PG-20261022-001.json", {"id": "PG-20261022-001"})
        self.assertTrue(any("unregistered run" in error for error in audit(self.root)))

    def test_rejects_non_utc_clock(self):
        with self.assertRaises(ValueError):
            utc_timestamp("2026-10-22T11:00:00-04:00")


if __name__ == "__main__":
    unittest.main()
