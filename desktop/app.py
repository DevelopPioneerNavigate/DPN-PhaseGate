"""Native Qt entrypoint and noninteractive desktop smoke checks."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description="DPN PhaseGate native research console")
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--screenshot", type=Path, default=None)
    parser.add_argument("--screenshot-evidence", type=Path, default=None,
                        help="capture Calibration and Evidence Lab native page")
    parser.add_argument("--screenshot-assembly", type=Path, default=None,
                        help="capture actual interactive Qt Assembly Studio design page")
    parser.add_argument("--screenshot-build", type=Path, default=None,
                        help="capture real dimensioned PG-01 native engineering workbench")
    parser.add_argument("--screenshot-stations", type=Path, default=None,
                        help="render the redesigned native station matrix")
    parser.add_argument("--screenshot-reference", type=Path, default=None,
                        help="capture offline Reference Event Lab with no camera access")
    parser.add_argument("--screenshot-optical", type=Path, default=None,
                        help="capture opt-in Optical Evidence Lab without opening any camera")
    parser.add_argument("--screenshot-hardware", type=Path, default=None,
                        help="capture the real USB Hardware Lab on the Qt native interface")
    args = parser.parse_args(argv)

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from desktop.model import inventory, VERSION
    from desktop.window import ResearchWindow, app_icon

    application = QApplication.instance() or QApplication(sys.argv[:1])
    application.setApplicationName("DPN PhaseGate")
    application.setOrganizationName("DPN Technology")
    application.setApplicationVersion(VERSION)
    application.setWindowIcon(app_icon())

    records = inventory()
    if args.self_test and any(records[name] is None for name in ("sources", "hypotheses", "experiments")):
        return 2
    window = ResearchWindow()
    window.setWindowIcon(app_icon())
    if args.smoke_test or args.self_test:
        window.resize(1600, 980)
    window.show()
    if args.smoke_test or args.self_test:
        def complete():
            result = 0
            # Ensure every native page, including operator USB/evidence pages,
            # remains navigable without needing hardware, dialogs, or network.
            for page_name in window.pages:
                window.navigate(page_name)
                application.processEvents()
                if window.pages[window.stack.currentIndex()] != page_name:
                    result = 6
            window.navigate("Command Center")
            application.processEvents()
            # Functional & structural UX gate: real native stage, slim instrument
            # dock and actions must exist in the rendered application.
            if (window.rail.width() > 190 or
                not window.nexus_deck.stage.isVisible() or
                window.nexus_deck.stage.width() < 260 or
                len(window.nav) != len(window.pages) or len(window.pages)!=13):
                result = 9
            if args.screenshot:
                try:
                    args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                    if not window.grab().save(str(args.screenshot), "PNG"):
                        raise OSError("Qt native-window screenshot could not be saved")
                    if args.screenshot.stat().st_size < 1000:
                        raise OSError("Qt screenshot is empty")
                except OSError:
                    result = 3
            if args.screenshot_hardware:
                try:
                    window.navigate("Hardware Lab")
                    application.processEvents()
                    args.screenshot_hardware.parent.mkdir(parents=True, exist_ok=True)
                    if not window.grab().save(str(args.screenshot_hardware), "PNG"):
                        raise OSError("Qt Hardware Lab screenshot could not be saved")
                    if args.screenshot_hardware.stat().st_size < 1000:
                        raise OSError("Qt Hardware Lab screenshot is empty")
                except (OSError, ValueError):
                    result = 4
            if args.screenshot_evidence:
                try:
                    window.navigate("Calibration & Evidence")
                    application.processEvents()
                    args.screenshot_evidence.parent.mkdir(parents=True, exist_ok=True)
                    if not window.grab().save(str(args.screenshot_evidence), "PNG"):
                        raise OSError("Qt Calibration & Evidence screenshot missing")
                    if args.screenshot_evidence.stat().st_size < 1000:
                        raise OSError("Qt calibration screenshot empty")
                except (OSError, ValueError):
                    result = 5
            if args.screenshot_optical:
                try:
                    window.navigate("Optical Evidence")
                    application.processEvents()
                    args.screenshot_optical.parent.mkdir(parents=True, exist_ok=True)
                    if not window.grab().save(str(args.screenshot_optical), "PNG"):
                        raise OSError("Optical page screenshot not saved")
                    if args.screenshot_optical.stat().st_size < 1000:
                        raise OSError("Optical page screenshot empty")
                    # No camera preview or recording is started by screenshots.
                    if window.optical_lab.workers:
                        raise OSError("Camera opened during native screenshot smoke test")
                except (OSError,ValueError):
                    result = 7
            if args.screenshot_reference:
                try:
                    window.navigate("Reference Events")
                    application.processEvents()
                    args.screenshot_reference.parent.mkdir(parents=True, exist_ok=True)
                    if not window.grab().save(str(args.screenshot_reference),"PNG"):
                        raise OSError("Reference Event Lab screenshot not saved")
                    if args.screenshot_reference.stat().st_size < 1000:
                        raise OSError("Reference screenshot empty")
                    if window.optical_lab.workers:
                        raise OSError("Camera opened during reference smoke test")
                except (OSError,ValueError):
                    result = 8
            if args.screenshot_stations:
                try:
                    window.navigate("Station Matrix")
                    application.processEvents()
                    args.screenshot_stations.parent.mkdir(parents=True, exist_ok=True)
                    if not window.grab().save(str(args.screenshot_stations),"PNG"):
                        raise OSError("Station Matrix screenshot missing")
                    if args.screenshot_stations.stat().st_size < 1000:
                        raise OSError("Station Matrix screenshot empty")
                except (OSError, ValueError):
                    result = 10
            if args.screenshot_build:
                try:
                    window.navigate("Gate Engineering")
                    application.processEvents()
                    args.screenshot_build.parent.mkdir(parents=True, exist_ok=True)
                    if not window.grab().save(str(args.screenshot_build), "PNG"):
                        raise OSError("Native Build Lab screenshot missing")
                    if args.screenshot_build.stat().st_size < 1000:
                        raise OSError("Build Lab screenshot empty")
                    if not window.build_lab.manifest["components"]:
                        raise OSError("Missing build engineering manifest in runtime")
                except (OSError,ValueError):
                    result = 11
            if args.screenshot_assembly:
                try:
                    window.navigate("Assembly Studio")
                    application.processEvents()
                    studio=window.assembly_studio
                    if (len(studio.design["assemblies"])<12 or
                        not all(c["passed"] for c in studio.fits) or
                        not studio.canvas.isVisible()):
                        raise OSError("Assembly Studio failed geometry or native view smoke")
                    studio.canvas.set_explode(38)
                    studio.choose_part("B-RING")
                    application.processEvents()
                    args.screenshot_assembly.parent.mkdir(parents=True,exist_ok=True)
                    if not window.grab().save(str(args.screenshot_assembly),"PNG"):
                        raise OSError("Assembly native screenshot missing")
                    if args.screenshot_assembly.stat().st_size<1000:
                        raise OSError("Assembly native screenshot empty")
                    if window.optical_lab.workers:
                        raise OSError("Assembly view activated a camera")
                except (OSError,ValueError):
                    result=12
            window.close()
            application.exit(result)
        QTimer.singleShot(900, complete)
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
