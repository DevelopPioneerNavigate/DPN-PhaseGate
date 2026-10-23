// DPN PhaseGate PG-01 Rev B — mechanical interfaces and actual fit-check exports.
// OpenSCAD assembled 3D study; manufactured parts require mechanical review.
// No energized ring, high-current supply, motor or portal-field construction.
// This file deliberately supersedes the original Rev A rail height; the old
// pg01_bench.scad remains as an archived reference for source compatibility.
//
// CLI: openscad -o build/Joint-Splice.stl --export-format asciistl
//        -D 'part="joint_splice"' hardware/cad/pg01_assembly_v1_5.scad
use <pg01_bench.scad>

part="assembly";  // [assembly,joint_splice,rail_clamp,cable_clip]
$fn=64;

// design reference: data/engineering/pg01-assembly-v1.5.json
center_z=270;
station_pitch=800;
rail_length=1200;
rail_z=191;
gate_outer=360;
gate_inner=260;
spoke_length=48;

// Printed trial design ONLY. Screw sizes and load paths aren't approved.
module joint_splice(){
    difference(){
        union(){
            cube([48,22,6],center=true);
            translate([0,0,4])cube([25,15,2],center=true);
        }
        for(x=[-11,11])
            translate([x,0,0]) cylinder(d=3.4,h=14,center=true);
    }
}

// Rail clamp is an adaptation blank: actual purchased guide profile may differ.
module rail_clamp(){
    difference(){
        cube([55,42,13],center=true);
        translate([0,0,5])
            cube([21,48,11],center=true);
        // Keep 4.5mm mounting bores clear of the 21mm-wide rail groove.
        for(x=[-17,17])
            translate([x,0,0])
                cylinder(d=4.5,h=25,center=true);
    }
}

// Cable clip has open saddle for a low-voltage strain relief fit check only.
module cable_clip(){
    difference(){
        union(){
            cube([44,24,8],center=true);
            translate([0,0,8])
                cube([19,24,17],center=true);
        }
        translate([0,0,12])
            cube([12,30,15],center=true);
        for(x=[-16,16])
            translate([x,0,0]) cylinder(d=3.4,h=19,center=true);
    }
}

module safe_passive_guide(){
    for(x=[-45,45]){
        color([.37,.62,.76])
            translate([x,0,rail_z])cube([16,rail_length,19],center=true);
        for(y=[-578,578])
            color([.85,.46,.28])
                translate([x,y,rail_z+10])cube([38,18,28],center=true);
    }
    // Tray surface at 205mm; keep non-load rated placeholder geometry.
    color([.49,.73,.78])
        translate([0,0,198])cube([100,130,14],center=true);
    color([.22,.34,.52])
        translate([0,0,206])cube([100,130,2],center=true);
}

module documented_cable_run(y){
    // Physical cable route is a provisional path; no wires connected.
    color([.34,.8,.89])
    for(z=[68,110,152,194,236,278,320]){
        translate([-205,y,z])sphere(r=2);
    }
    translate([-205,y,180])
        color([.19,.43,.59]) cube([6,15,245],center=true);
}

module assembled_fitcheck(){
    // Existing Rev A ring geometry and updated Rev B guide elevation.
    gate_support(-station_pitch/2);
    gate_support(+station_pitch/2);
    safe_passive_guide();
    // Distinct visible splice blanks are mounted for design-reference only.
    for(y=[-station_pitch/2,station_pitch/2])
        for(a=[0:5]){
            rotate([0,0,a*60])
                translate([0,y,center_z])
                    rotate([90,0,0])
                        translate([0,157,0])
                            color([.65,.62,.85]) joint_splice();
        }
    for(y=[-station_pitch/2,station_pitch/2]){
        documented_cable_run(y);
        color([.91,.74,.40])
            translate([-182,y-25,395])cube([34,44,32],center=true);
    }
    for(y=[-450,450]){
        for(x=[-45,45])
            color([.46,.68,.78])
                translate([x,y,rail_z-18])rail_clamp();
    }
}

if(part=="joint_splice") joint_splice();
else if(part=="rail_clamp") rail_clamp();
else if(part=="cable_clip") cable_clip();
else if(part=="assembly") assembled_fitcheck();
else echo("ERROR: invalid Rev B mechanical part selector");
