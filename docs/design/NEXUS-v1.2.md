# PhaseGate NEXUS v1.2 — Native UI Reconstruction

[← Main README](../../README.md) · [Windows EXE builds](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml) · [Research evidence rules](../physics/EVIDENCE-WORKFLOW.md)

## What changed

NEXUS is a **significant application-shell and command-center replacement**, not a recolor of AURORA. It is rendered using native Windows Qt widgets, with procedural original DPN art. It does not embed a browser, use online image assets or activate any cameras, serial ports or equipment as a result of navigation.

| Old PhaseGate UI | NEXUS v1.2 |
|---|---|
| 244px conventional text sidebar | 181px compressed research-workspace dock, keyboard navigation and hide/show |
| Large rectangular banner with modest concentric ring | Full-sized QPainter volumetric **NEXUS concept machine** illustration, with hangar grid, gantry, isometric platform, illuminated segmented toroidal coils, halo and particles |
| Sequential card-like home page | Single coordinated cinematic dashboard: main vector stage, operator station controls, bottom scientific inventory readouts and clear safety state |
| Multiple repetitive headings and disclaimers above content | High-density permanent top mission bar, station panel and persistent evidence/verification footer |
| Generic station circles | Reused large NEXUS vector stations with independent A/B demo readouts |
| One-size-fits-all styling | DPN Obsidian palette with violet-lit action hierarchy, bright cyan data markers, stronger typography and reworked tables/forms/cards |

### Actual native controls

**Command Center:** working actions open Hardware Lab, Optical Evidence or Reference Events. The main program data come from the same real local read-only research inventory, not invented numbers.

**Every screen:** Ctrl+K opens the existing searchable native command palette. Ctrl+1..9 (and Ctrl+0 for the tenth screen) navigate; the eleventh is available in the dock/command palette. Ctrl+B hides/restores the compact workspace dock; F11 toggles fullscreen.

**Reduced motion:** Preferences → Disable animated visualizations pauses the NEXUS stage and station vector artwork; it does not affect physical USB device state.

**Scientific segregation:** NEXUS scene is *concept artwork*, not a physically measured portal, real camera feed or predictive physics model. Existing Hardware Lab, Calibration & Evidence, Optical Evidence and Reference Events remain separate workspaces with the previously implemented explicit operator consent and BENCH-only provenance restrictions. No recording automatically becomes a scientific experiment.

## Release verification

Windows GitHub Actions must pass:
- Python scientific integrity, documentation and all existing regression tests;
- an **11-workspace navigation test** with no camera auto-open;
- structural UX assertions for the compact dock and real visible vector-stage widget;
- actual native screenshots of the command center, **redesigned Station Matrix** and existing lab screens;
- packaging and launching `DPN-PhaseGate.exe` in the Windows runner before uploading artifacts.

Open a successful run in [Native Windows EXE](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml) and download `DPN-PhaseGate-Native-Windows-v1.2`. The `DPN-PhaseGate-Native-Preview-v1.2` artifact shows actual Qt screenshots from the build.

## Honest progress

A functional standalone Windows UI with camera/USB evidence software is useful for research design, but no physical device has established bidirectional intact-object transfer. Firmware compatibility, hardware timing, actual cameras, sample calibration and validated scientific trials remain physical validation gates.
