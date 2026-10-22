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
            window.close()
            application.exit(result)
        QTimer.singleShot(900, complete)
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
