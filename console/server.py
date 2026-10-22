"""DPN PhaseGate v0.5 local read-only console: synthetic data, no hardware."""
from __future__ import annotations
import argparse
import json
import math
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
WEB = Path(__file__).resolve().parent / "web"
ASSETS = {"/": ("index.html", "text/html; charset=utf-8"),
          "/index.html": ("index.html", "text/html; charset=utf-8"),
          "/styles.css": ("styles.css", "text/css; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8")}
WARNING = "SYNTHETIC DATA ONLY. No hardware connected; no physical object teleportation has been observed."


def overview(root=ROOT):
    def count(filename, field):
        try:
            x = json.loads((root / filename).read_text(encoding="utf8"))[field]
            return len(x) if isinstance(x, list) else None
        except (OSError, ValueError, KeyError, TypeError):
            return None
    return {"project":"DPN PhaseGate", "version":"0.5.0", "mode":"SYNTHETIC",
            "hardware_connected":False, "physical_transfer_verified":False,
            "sources":count("data/literature/sources.json", "sources"),
            "hypotheses":count("data/hypotheses/hypotheses.json", "hypotheses"),
            "experiment_records":count("data/experiments/manifest.json", "experiments"),
            "warning":WARNING}


def synthetic_snapshot(at=None):
    at = at or datetime.now(timezone.utc)
    if at.tzinfo is None or at.utcoffset() != timedelta(0):
        raise ValueError("time must be UTC with timezone")
    sec = int(at.timestamp())
    samples = []
    for i in range(60):
        t = sec - 59 + i
        timestamp = datetime.fromtimestamp(t, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        samples.append({"utc":timestamp, "A":round(45.0 + math.sin(t/7.0)*0.18,3),
                        "B":round(math.cos(t/9.0)*0.028,3)})
    return {"mode":"SYNTHETIC", "unit":"g", "samples":samples,
            "stations":[{"id":"A","mass_g":samples[-1]["A"],"link":"NO HARDWARE","state":"DEMO"},
                        {"id":"B","mass_g":samples[-1]["B"],"link":"NO HARDWARE","state":"DEMO"}],
            "warning":WARNING}


def synthetic_events():
    return {"mode":"SYNTHETIC", "events":[
        {"id":"SIM-001", "label":"Synthetic instrumentation initialized", "level":"info"},
        {"id":"SIM-002", "label":"Baseline B has no object (illustration only)", "level":"neutral"},
        {"id":"SIM-003", "label":"No experiment performed or approved", "level":"warning"}]}


class Handler(BaseHTTPRequestHandler):
    server_version = "PhaseGateDemo/0.5"

    def log_message(self, fmt, *args):
        return

    def answer(self, status, data, mime, head=False):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; img-src 'self' data:; script-src 'self'; "
                         "style-src 'self'; connect-src 'self'; object-src 'none'; "
                         "frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        if not head:
            self.wfile.write(data)

    def do_GET(self):
        self.dispatch(False)

    def do_HEAD(self):
        self.dispatch(True)

    def do_POST(self):
        self.answer(405, b"Read-only demonstration", "text/plain")

    def dispatch(self, head):
        path = urlsplit(self.path).path
        api = {"/api/overview":overview, "/api/telemetry":synthetic_snapshot,
               "/api/events":synthetic_events}
        if path in api:
            return self.answer(200, json.dumps(api[path](), allow_nan=False).encode(),
                               "application/json; charset=utf-8", head)
        if path in ASSETS:
            name, mime = ASSETS[path]
            try:
                data = (WEB / name).read_bytes()
            except OSError:
                return self.answer(503, b"UI unavailable", "text/plain", head)
            return self.answer(200, data, mime, head)
        return self.answer(404, b"Not found", "text/plain", head)


def main(argv=None):
    parser = argparse.ArgumentParser(description="PG-01 console (offline synthetic mode ONLY)")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    if args.port < 1024 or args.port > 65535:
        parser.error("Use port between 1024 and 65535")
    try:
        # Intentional: no option to expose an unauthenticated prototype to a network.
        with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
            server.daemon_threads = True
            print("DPN PhaseGate Console: http://127.0.0.1:" + str(args.port))
            print(WARNING)
            server.serve_forever(poll_interval=0.4)
    except KeyboardInterrupt:
        return 0
    except OSError as e:
        parser.exit(2, "Cannot open console: " + str(e) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
