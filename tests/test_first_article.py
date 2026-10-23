"""First article inspection is operator-observed and non-authorizing."""
import copy
import csv
import io
import math
import tempfile
import unittest
from pathlib import Path

from desktop.build_plan import RigError, read_progress, save_progress
from desktop.assembly_model import read_assembly
from tools.export_pg01_inspection_drawings import trial_fastener_schedule, specimen_svg, blank_template
from desktop.first_article import (
    read_plan, validate_plan, record_pair, review_specimen,
    inspection_csv, specimen_key, PLAN_SCHEMA
)


class TrialInspectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=read_plan()

    def test_four_actual_cad_trials_have_drawings_and_checks(self):
        plan=self.plan
        self.assertEqual(plan["schema"],PLAN_SCHEMA)
        self.assertEqual(len(plan["items"]),4)
        self.assertEqual(sum(len(p["checks"]) for p in plan["items"]),19)
        self.assertEqual(plan["items"][1]["checks"][3]["nominal_mm"],34)
        self.assertFalse(plan["inspection_policy"]["independent_approval"])

    def test_proposed_fastener_schedule_never_approves_load_or_torque(self):
        rows=list(csv.DictReader(io.StringIO(trial_fastener_schedule(read_assembly()))))
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[1]["hole_pitch_mm"],"34")
        self.assertTrue(all(x["torque_setting"]=="NO TORQUE VALUE APPROVED"
                            for x in rows))
        self.assertTrue(all(x["approval"]=="NOT APPROVED FOR LOAD" for x in rows))
        self.assertEqual(sum(int(x["nominal_hole_count"]) for x in rows),40)

    def test_generated_drawing_is_valid_svg_with_trial_hold(self):
        from xml.etree import ElementTree as ET
        raw=specimen_svg(self.plan["items"][0])
        self.assertEqual(ET.fromstring(raw).tag,
                         "{http://www.w3.org/2000/svg}svg")
        self.assertIn("NOT APPROVED FOR FABRICATION",raw)
        self.assertEqual(len(list(csv.DictReader(
            io.StringIO(blank_template(self.plan))))),19)

    def test_empty_is_hold_not_pass(self):
        r=review_specimen(self.plan,{}, "FA-01","TEST-001")
        self.assertFalse(r["complete_candidate_fit_review"])
        self.assertFalse(r["independently_approved"])
        self.assertEqual(len(r["rows"]),5)

    def test_one_record_is_insufficient(self):
        state={}
        record_pair(self.plan,state,"FA-01","TEST-001","L",
                    48.1,47.9,"Inspector","CALIPER-A17","lab sheet record 01")
        r=review_specimen(self.plan,state,"FA-01","TEST-001")
        self.assertFalse(r["complete_candidate_fit_review"])
        self.assertTrue(r["rows"][0]["within_trial_range"])
        self.assertFalse(r["rows"][1]["within_trial_range"])

    def test_out_of_range_observation_prevents_candidate_fit_label(self):
        state={}
        for c in self.plan["items"][0]["checks"]:
            v=c["nominal_mm"]
            record_pair(self.plan,state,"FA-01","TEST-001",c["id"],
                        v,v,"Inspector","CALIPER-A17","evidence lab sheet 21")
        self.assertTrue(review_specimen(self.plan,state,"FA-01","TEST-001")[
            "complete_candidate_fit_review"])
        self.assertFalse(review_specimen(self.plan,state,"FA-01","TEST-001")[
            "independently_approved"])
        record_pair(self.plan,state,"FA-01","TEST-001","L",
                    48,52,"Inspector","CALIPER-A17","evidence lab sheet 22")
        self.assertFalse(review_specimen(self.plan,state,"FA-01","TEST-001")[
            "complete_candidate_fit_review"])

    def test_reject_nan_fake_evidence_or_unknown_part(self):
        state={}
        with self.assertRaises(RigError):
            record_pair(self.plan,state,"FA-01","TEST-001","L",
                        float("nan"),48,"Inspector","CALIPER-A17","lab sheet 003")
        with self.assertRaises(RigError):
            record_pair(self.plan,state,"FA-01","TEST-001","L",
                        True,48,"Inspector","CALIPER-A17","lab sheet 003")
        with self.assertRaises(RigError):
            record_pair(self.plan,state,"FA-01","bad","L",
                        48,48,"Inspector","CALIPER-A17","lab sheet 003")
        with self.assertRaises(RigError):
            record_pair(self.plan,state,"FA-01","TEST-001","L",
                        48,48,"Inspector","CALIPER-A17","short")
        with self.assertRaises(RigError):
            record_pair(self.plan,state,"FA-99","TEST-001","L",
                        48,48,"Inspector","CALIPER-A17","lab sheet 003")
        self.assertFalse(bool(state))

    def test_cross_part_isolation_and_csv_with_provenance(self):
        state={}
        record_pair(self.plan,state,"FA-02","TEST-002","P",
                    34.05,33.96,"Inspector","CALIPER-B10","photo sheet entry 11")
        r=review_specimen(self.plan,state,"FA-01","TEST-002")
        self.assertFalse(any(a["observations_recorded"] for a in r["rows"]))
        data=list(csv.DictReader(io.StringIO(inspection_csv(self.plan,state))))
        match=[row for row in data if row["part"]=="FA-02"
               and row["characteristic"]=="Two-hole center spacing"]
        self.assertEqual(len(match),1)
        self.assertEqual(match[0]["equipment"],"CALIPER-B10")
        self.assertEqual(match[0]["obs_1_mm"],"34.05")
        self.assertIn("NOT INDEPENDENTLY APPROVED",match[0]["interpretation"])

    def test_local_progress_roundtrip_and_checksum(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"pg01-build-progress.json"
            state=read_progress(path)
            record_pair(self.plan,state,"FA-03","TEST-003","P",
                        32,32.1,"Inspector","CALIPER-C7","receiving log 301")
            save_progress(state,path)
            recovered=read_progress(path)
            assert specimen_key("FA-03","TEST-003") in recovered["first_article"]
            self.assertTrue(review_specimen(self.plan,recovered,"FA-03","TEST-003")[
                "rows"][2]["within_trial_range"])

    def test_drawing_guard_rejects_changed_tolerance(self):
        bad=copy.deepcopy(self.plan)
        bad["items"][0]["checks"][0]["tolerance_mm"]=float("inf")
        with self.assertRaises(RigError):
            validate_plan(bad)


if __name__=="__main__":
    unittest.main()
