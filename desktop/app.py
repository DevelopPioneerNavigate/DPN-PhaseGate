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
    window.resize(1440, 900)
    window.show()
    if args.smoke_test or args.self_test:
        def complete():
            result = 0
            if args.screenshot:
                try:
                    args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                    if not window.grab().save(str(args.screenshot), "PNG"):
                        raise OSError("Qt native-window screenshot could not be saved")
                    if args.screenshot.stat().st_size < 1000:
                        raise OSError("Qt screenshot is empty")
                except OSError:
                    result = 3
            window.close()
            application.exit(result)
        QTimer.singleShot(900, complete)
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
