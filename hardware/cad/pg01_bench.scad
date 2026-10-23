// DPN PhaseGate PG-01 dual-gate bench metrology chassis.
// OpenSCAD parametric engineering envelope and STL-generating fit-check parts.
// Mechanical concept, NOT final manufacture design or an energized portal.
// Units: mm. Inspect printed samples, tolerances, stability, wiring and materials
// with a qualified engineer before fabrication. Do NOT load a ring structurally.
//
// Export assembly: openscad -o build/pg01-bench-assembly.stl pg01_bench.scad
// Export a single print test:
// openscad -o build/gate_segment.stl -D 'part="ring_segment"' pg01_bench.scad
// Use -D 'part="camera_bracket"' for a printable trial bracket.

part="assembly"; // [assembly,ring_segment,camera_bracket,payload_tray]
$fn=60;

// Reference from data/engineering/pg01-rig-manifest.json revision v0.1
outer_d=360;
aperture_d=260;
segment_count=6;
ring_depth=18;
segment_radial=(outer_d-aperture_d)/2;
gate_separation=800;             // nominal gate center-to-center
gate_center_z=270;
rail_length=1200;
rail_spacing=90;
platform_w=100;
platform_l=130;
base_w=420;
base_l=270;
base_z=18;
fit_clearance=0.45;             // trial FDM allowance, not process-validated
m3_clearance=3.4;

// Ring segment is a printable trial part. No field-generation component exists.
// Nominal hole locations need engineer-verified structural analysis.
module ring_segment(theta=360/segment_count) {
  difference() {
    rotate_extrude(angle=theta,convexity=8,$fn=72)
      translate([aperture_d/2,0,0])
        square([segment_radial,ring_depth],center=false);
    for (a=[8,theta-8]) {
      rotate([0,0,a])
        translate([aperture_d/2+segment_radial/2,0,ring_depth/2])
          cylinder(h=ring_depth+3,d=m3_clearance,center=true,$fn=24);
    }
  }
}

module gate_ring() {
  for (i=[0:segment_count-1])
    rotate([0,0,i*360/segment_count])
      color(i%2 ? [0.29,0.42,0.65]:[0.39,0.51,0.72])
        ring_segment();
}

// Only these covers simulate engineered external styling; NO coils.
module sensor_bracket() {
  difference(){
    cube([34,28,8],center=true);
    translate([-11,0,0]) cylinder(h=15,d=m3_clearance,center=true);
    translate([11,0,0]) cylinder(h=15,d=m3_clearance,center=true);
  }
}

module payload_tray() {
  color([.48,.57,.66])
    difference(){
      cube([platform_w,platform_l,8],center=true);
      translate([0,0,4]) cube([platform_w-12,platform_l-12,4],center=true);
    }
}

module extrusion_at(pos,dims,metal=[.34,.44,.58]){
  color(metal) translate(pos) cube(dims,center=true);
}

module gate_support(gate_y=0){
  // Uprights and crossbar are design envelope only. T-slot joints are not
  // defined as production-quality load-bearing connections.
  for(x=[-140,140]){
    extrusion_at([x,gate_y,gate_center_z/2],[20,20,gate_center_z]);
    extrusion_at([x,gate_y,base_z],[55,base_l,base_z]);
  }
  extrusion_at([0,gate_y,gate_center_z-outer_d/2-13],[330,22,22]);
  translate([0,gate_y,gate_center_z])
    rotate([90,0,0]) gate_ring();
  // A/B independent load-sensor platform on frame base, not on rail.
  extrusion_at([0,gate_y-42,base_z+18],[145,120,8],[.18,.42,.48]);
}

module rail() {
  // Two separated passive guides. Proper carriage/bearing/stop selection is
  // a separate rated hardware work package; geometry is illustrative.
  for(x=[-rail_spacing/2,rail_spacing/2]){
    extrusion_at([x,0,27],[15,rail_length,18],[.5,.59,.66]);
    for(y=[-rail_length/2+20,rail_length/2-20])
      extrusion_at([x,y,38],[28,14,22],[.85,.52,.19]); // stop placeholders
  }
  extrusion_at([0,0,46],[platform_w,platform_l,12],[.31,.46,.57]);
  translate([0,0,56]) payload_tray();
}

module assembly(){
  // For visually reviewing collisions at the proposed overall envelope
  // and exporting a preliminary CAD model; not construction authority.
  gate_support(-gate_separation/2);
  gate_support(+gate_separation/2);
  rail();
  // Camera mount envelopes on separate accessible brackets.
  for(y=[-gate_separation/2,gate_separation/2]){
    extrusion_at([-165,y-30,305],[20,20,170],[.33,.35,.38]);
    color([.26,.68,.78]) translate([-165,y-30,390]) sensor_bracket();
  }
}

// Switchable output lets maintainers build separate parts using OpenSCAD.
// One gate segment is less than ~190mm wide for a common large FDM bed;
// slicer fit, wall thickness and strength still require physical confirmation.
if(part=="assembly") assembly();
else if(part=="ring_segment") ring_segment();
else if(part=="camera_bracket") sensor_bracket();
else if(part=="payload_tray") payload_tray();
else echo("ERROR: unknown CAD part");
