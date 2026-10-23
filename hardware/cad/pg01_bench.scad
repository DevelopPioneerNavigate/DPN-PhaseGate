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

part="assembly"; // [assembly,ring_segment,camera_bracket,payload_tray,fit_coupon,stop_flag]
$fn=60;

// Reference from data/engineering/pg01-rig-manifest.json revision v0.2 and pg01-manufacturing-v0.2.json
outer_d=360;
aperture_d=260;
segment_count=6;
ring_depth=18;
segment_radial=(outer_d-aperture_d)/2;
gate_separation=800;             // nominal gate center-to-center
gate_center_z=270;
rail_length=1200;
rail_center_z=183;            // corrected: rail passes through clear aperture
rail_cross_height=14;
tray_bottom_z=211;
station_visit_y=420;         // center visits ±420; gate centers ±400
endstop_y=540;
minimum_clearance=12;
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
  // Independent metrology plate is OUTSIDE the ring opening and isolated
  // from the carriage support; payload is manually moved onto the scale.
  extrusion_at([178,gate_y,205],[120,120,8],[.18,.42,.48]);
  extrusion_at([178,gate_y,100],[24,30,188],[.29,.42,.55]);
}

module rail() {
  // Real geometric fix: the former rail z=27 and payload z=56 were BELOW
  // the 260mm clear aperture. Guide center z=183 puts all guide corners
  // inside the aperture with a provisional >=12mm radial buffer.
  for(x=[-rail_spacing/2,rail_spacing/2]){
    extrusion_at([x,0,rail_center_z],[15,rail_length,rail_cross_height],[.5,.59,.66]);
    for(y=[-endstop_y,endstop_y])
      extrusion_at([x,y,rail_center_z+19],[23,14,26],[.85,.52,.19]); // trial stop placeholders only
    for(y=[-520,0,520])  // never cross a ring plane with full-height support legs
      extrusion_at([x,y,rail_center_z/2],[20,20,rail_center_z],[.35,.43,.52]);
  }
  extrusion_at([0,0,202],[platform_w,platform_l,18],[.31,.46,.57]);
  translate([0,0,tray_bottom_z+4]) payload_tray();
}


// Printed tolerance coupon gives practical hole fit feedback before ordering
// or printing twelve structural-looking segments. It is NOT proof of strength.
module fit_coupon() {
  difference(){
    cube([66,29,7],center=true);
    for(i=[0:3])
      translate([-24+i*16,0,0])
        cylinder(h=12,d=3.2+i*.2,center=true,$fn=32);
  }
}

module stop_flag() {
  // Fit-check geometry only. Commercially rated hard stops must be selected.
  difference(){
    union(){
      cube([50,25,8],center=true);
      translate([0,8,14]) cube([50,9,22],center=true);
    }
    for(x=[-17,17])
      translate([x,-6,0]) cylinder(h=16,d=3.5,center=true,$fn=28);
  }
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
else if(part=="fit_coupon") fit_coupon();
else if(part=="stop_flag") stop_flag();
else echo("ERROR: unknown CAD part");
