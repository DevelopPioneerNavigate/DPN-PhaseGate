"""PG-01 Rev B coordinate model invariants; no physical device needed."""
import copy
import tempfile
import unittest
from desktop.assembly_model import read_assembly, validate_assembly, fit_checks, component_detail
from desktop.build_plan import read_manifest, RigError


class AssemblyChecks(unittest.TestCase):
    def setUp(self):
        self.rig=read_manifest()
        self.model=read_assembly()

    def test_actual_coordinate_model_and_complete_layers(self):
        self.assertEqual(self.model["schema"],"PG01-MECHANICAL-ASSEMBLY-1")
        self.assertEqual(len(self.model["assemblies"]),15)
        self.assertEqual(len(self.model["view_layers"]),6)
        self.assertTrue(all(x["passed"] for x in fit_checks(self.model,self.rig["dimensions_mm"])))
        self.assertEqual(component_detail(self.model,"B-RING")["layer"],"STRUCTURE")

    def test_rail_travel_must_reach_both_station_centerlines(self):
        modified=copy.deepcopy(self.rig)
        modified["dimensions_mm"]["rail_travel_design_goal"]=680
        with self.assertRaisesRegex(RigError,"cannot move from Station A"):
            validate_assembly(self.model,modified)

    def test_original_rail_height_fails_clearance(self):
        model=copy.deepcopy(self.model)
        model["geometry_mm"]["rail_z"]=174
        model["assemblies"][4]["center_mm"][2]=174
        model["assemblies"][5]["center_mm"][2]=174
        with self.assertRaisesRegex(RigError,"Rail bounding edge"):
            validate_assembly(model,self.rig)

    def test_payload_above_or_below_aperture_must_fail(self):
        model=copy.deepcopy(self.model)
        model["geometry_mm"]["carriage_tray_surface_z"]=390
        model["geometry_mm"]["payload_bottom_z"]=390
        with self.assertRaisesRegex(RigError,"Payload bounding box"):
            validate_assembly(model,self.rig)

    def test_ring_dimensions_must_agree_with_source_manifest(self):
        model=copy.deepcopy(self.model)
        part=next(x for x in model["assemblies"] if x["id"]=="A-RING")
        part["diameter_mm"]=320
        with self.assertRaisesRegex(RigError,"ring dimensions"):
            validate_assembly(model,self.rig)

    def test_duplicate_part_and_bad_usb_cable_path_are_rejected(self):
        model=copy.deepcopy(self.model)
        model["assemblies"][-1]["id"]=model["assemblies"][0]["id"]
        with self.assertRaisesRegex(RigError,"repeated"):
            validate_assembly(model,self.rig)
        model=copy.deepcopy(self.model)
        route=next(x for x in model["assemblies"] if x["id"]=="CBL-A")
        route["points_mm"]=[[1,2,float("nan")],[1,2,1]]
        with self.assertRaisesRegex(RigError,"coordinate"):
            validate_assembly(model,self.rig)

    def test_duplicate_and_fabrication_status_not_asserted_by_design(self):
        m=self.model
        self.assertIn("no assembled",m["maturity"].lower())
        self.assertTrue(any("no field emitter" in t.lower() for t in m["warnings"]))


if __name__=="__main__":
    unittest.main()
