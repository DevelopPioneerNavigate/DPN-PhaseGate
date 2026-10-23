"""PG-01 build workbench regressions, independent of hardware procurement."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from desktop.build_plan import (
    RigError, validate_manifest, read_manifest, read_progress, save_progress,
    task_status, report_status, gate_review, export_bom_csv
)


def fixture():
    return read_manifest()


class BuildPlanTests(unittest.TestCase):
    def test_repository_manifest_and_reference_dimensions(self):
        plan=fixture()
        self.assertEqual(plan["schema"],"DPN-PG01-RIG-1")
        self.assertEqual(len(plan["stations"]),2)
        self.assertEqual({x["id"] for x in plan["stations"]},{"A","B"})
        self.assertGreaterEqual(len(plan["components"]),12)
        self.assertGreaterEqual(len(plan["work_packages"]),9)
        self.assertGreater(plan["dimensions_mm"]["gate_outer_diameter"],
                           plan["dimensions_mm"]["clear_aperture_diameter"])

    def test_initial_state_never_auto_finishes(self):
        plan=fixture()
        with tempfile.TemporaryDirectory() as td:
            progress=read_progress(Path(td)/"nonexistent.json")
            self.assertTrue(all(task_status(t["id"],progress)=="planned"
                                for t in plan["work_packages"]))
            self.assertFalse(any(x["operator_reported_ready"]
                                for x in gate_review(plan,progress)))

    def test_dependency_gate_blocks_fabricated_completion(self):
        plan=fixture()
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/"pg01-build-progress.json"
            progress=read_progress(file)
            with self.assertRaises(RigError):
                report_status(plan,progress,"WP-04","operator_reported_complete",
                              "Tester","photo reference and dry rail check")
            report_status(plan,progress,"WP-01","operator_reported_complete",
                          "Tester","example CAD review evidence location")
            self.assertEqual(task_status("WP-01",progress),"operator_reported_complete")
            self.assertFalse(gate_review(plan,progress)[0]["operator_reported_ready"])
            save_progress(progress,file)
            loaded=read_progress(file)
            self.assertEqual(task_status("WP-01",loaded),"operator_reported_complete")
            self.assertIn("OPERATOR",loaded["classification"])

    def test_requires_reviewable_evidence_and_human_operator(self):
        plan=fixture()
        progress={"work_packages":{}}
        with self.assertRaises(RigError):
            report_status(plan,progress,"WP-01","operator_reported_complete",
                          "","evidence note for board inspection")
        with self.assertRaises(RigError):
            report_status(plan,progress,"WP-01","operator_reported_complete",
                          "Inspector","no")
        with self.assertRaises(RigError):
            report_status(plan,progress,"WP-01","approved",
                          "Inspector","supporting lab approval evidence")

    def test_manifest_rejects_dependency_cycle(self):
        bad=json.loads(json.dumps(fixture()))
        bad["work_packages"][0]["depends_on"]=["WP-09"]
        with self.assertRaises(RigError):
            validate_manifest(bad)

    def test_progress_tampering_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"pg01-build-progress.json"
            state=read_progress(path)
            save_progress(state,path)
            loaded=json.loads(path.read_text())
            loaded["work_packages"]["WP-01"]={"status":"operator_reported_complete"}
            path.write_text(json.dumps(loaded))
            with self.assertRaises(RigError):
                read_progress(path)

    def test_proposed_bom_export_is_real_csv(self):
        doc=fixture()
        lines=export_bom_csv(doc)
        import io
        rows=list(csv.DictReader(io.StringIO(lines)))
        self.assertEqual(len(rows),len(doc["components"]))
        self.assertEqual(rows[0]["procurement_status"],"not purchased")


if __name__=="__main__":
    unittest.main()
