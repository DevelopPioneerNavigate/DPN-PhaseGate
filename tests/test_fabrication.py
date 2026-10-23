import tempfile
import unittest
from pathlib import Path
from desktop.build_plan import read_manifest, read_progress, save_progress, RigError
from desktop.fabrication import inspect_dimension, update_receiving, fabrication_summary

class FabricationTests(unittest.TestCase):
    def test_empty_is_not_built(self):
        m=read_manifest()
        with tempfile.TemporaryDirectory() as d:
            p=read_progress(Path(d)/"pg01-build-progress.json")
            s=fabrication_summary(m,p)
            self.assertEqual(s["operator_reported_receipt"],0)
            self.assertEqual(s["dimensions_inspected"],0)
            self.assertFalse(s["independent_approval"])

    def test_real_measurement_entry_requires_evidence_and_keeps_claim_unreviewed(self):
        m=read_manifest()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"pg01-build-progress.json"
            p=read_progress(path)
            inspect_dimension(m,p,"gate_outer_diameter",360.4,"Builder","caliper lab note #21")
            entry=p["dimensional_inspections"]["gate_outer_diameter"]["history"][0]
            self.assertTrue(entry["within_candidate_range"])
            self.assertFalse(entry["independently_verified"])
            save_progress(p,path)
            self.assertEqual(len(read_progress(path)["dimensional_inspections"]),1)
            with self.assertRaises(RigError):
                inspect_dimension(m,p,"rail_length",float("nan"),"Builder","caliper lab note #22")

    def test_receiving_rejects_unknown_parts_or_states(self):
        m=read_manifest()
        with tempfile.TemporaryDirectory() as d:
            p=read_progress(Path(d)/"pg01-build-progress.json")
            with self.assertRaises(RigError):
                update_receiving(m,p,"OTHER","ordered","Builder","Purchase order #23")
            with self.assertRaises(RigError):
                update_receiving(m,p,"PG-MECH-001","installed_and_approved","Builder","Receipt photo #9")
            update_receiving(m,p,"PG-MECH-001","received_uninspected","Builder","Supplier receipt #82")
            self.assertEqual(fabrication_summary(m,p)["operator_reported_receipt"],0)

if __name__=="__main__":
    unittest.main()
