"""PG-01 physical CAD interface checks: catch the specific Rev A defects."""
import copy
import unittest

from desktop.manufacturing import (
    InterfaceError, evaluate_project, evaluate_geometry, cutlist_report,
    load_interface
)


class MechanicalFitChecks(unittest.TestCase):
    def test_corrected_gate_alignment_works(self):
        result=evaluate_project()
        self.assertEqual(result["status"],"PASS PRELIMINARY FIT CHECK")
        self.assertTrue(all(x["pass"] for x in result["checks"]))
        self.assertGreaterEqual(result["rail_clearance_mm"],12)
        self.assertGreaterEqual(result["payload_clearance_mm"],12)
        self.assertGreaterEqual(result["endstop_margin_mm"],12)
        self.assertFalse(result["independent_mechanical_review_complete"])
        self.assertFalse(result["independent_electrical_review_complete"])

    def test_legacy_rail_height_fails_aperture(self):
        g=copy.deepcopy(load_interface()["geometry"])
        g["rail_guide_center_height_mm"]=27
        g["shuttle_tray_bottom_z_mm"]=52
        summary=evaluate_geometry(g)
        self.assertEqual(summary["status"],"BLOCK DESIGN")
        self.assertFalse(next(c for c in summary["checks"] if c["id"]=="M2")["pass"])
        self.assertFalse(next(c for c in summary["checks"] if c["id"]=="M3")["pass"])

    def test_legacy_travel_cannot_reach_stations(self):
        g=copy.deepcopy(load_interface()["geometry"])
        g["shuttle_center_span_y_mm"]=[-340,340]
        result=evaluate_geometry(g)
        self.assertFalse(next(c for c in result["checks"] if c["id"]=="M1")["pass"])

    def test_rail_endstop_collision_blocks_design(self):
        g=copy.deepcopy(load_interface()["geometry"])
        g["rail_endstop_centres_y_mm"]=[-470,470]
        result=evaluate_geometry(g)
        self.assertFalse(next(c for c in result["checks"] if c["id"]=="M4")["pass"])

    def test_oversized_sample_fails_clearance(self):
        g=copy.deepcopy(load_interface()["geometry"])
        g["sample_height_allowance_mm"]=280
        result=evaluate_geometry(g)
        self.assertFalse(next(c for c in result["checks"] if c["id"]=="M3")["pass"])

    def test_nan_and_missing_inputs_rejected(self):
        g=copy.deepcopy(load_interface()["geometry"])
        g["rail_length_mm"]=float("nan")
        with self.assertRaises(InterfaceError):
            evaluate_geometry(g)
        g=copy.deepcopy(load_interface()["geometry"])
        g.pop("rail_guide_width_mm")
        with self.assertRaises(InterfaceError):
            evaluate_geometry(g)

    def test_manufacturing_cutlist_is_explicitly_preliminary(self):
        out=cutlist_report()
        self.assertEqual(out["total_ring_segments"],12)
        self.assertEqual(out["manual_guide_length_mm"],1200)
        self.assertEqual(out["drawing_approval"],"NOT APPROVED")
        self.assertIn("UNASSIGNED",out["actual_extrusion_cut_schedule"])


if __name__=="__main__":
    unittest.main()
