"""Offline safety and API tests for the PhaseGate *synthetic* console."""
import datetime
import http.client
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from console.server import Handler, overview, synthetic_events, synthetic_snapshot


class ModelTests(unittest.TestCase):
    def test_reproducible_synthetic_data(self):
        t = datetime.datetime(2026,10,22,tzinfo=datetime.timezone.utc)
        a = synthetic_snapshot(t)
        self.assertEqual(a, synthetic_snapshot(t))
        self.assertEqual(a["mode"], "SYNTHETIC")
        self.assertEqual(len(a["samples"]), 60)
        self.assertEqual(len(a["stations"]), 2)
        self.assertTrue(all(s["link"]=="NO HARDWARE" for s in a["stations"]))

    def test_reject_naive_time(self):
        with self.assertRaises(ValueError):
            synthetic_snapshot(datetime.datetime(2026, 10, 22))

    def test_real_registry_counts_and_absence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertIsNone(overview(root)["sources"])
            for filename, field, values in [
                ("data/literature/sources.json","sources",[1,2]),
                ("data/hypotheses/hypotheses.json","hypotheses",[1]),
                ("data/experiments/manifest.json","experiments",[])]:
                path=root/filename
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(json.dumps({field:values}),encoding="utf8")
            self.assertEqual(overview(root)["sources"],2)
            self.assertEqual(overview(root)["experiment_records"],0)
            self.assertFalse(overview(root)["physical_transfer_verified"])

    def test_events_never_claim_observation(self):
        self.assertEqual(synthetic_events()["mode"],"SYNTHETIC")


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        cls.server.daemon_threads=True
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self,method,path):
        conn=http.client.HTTPConnection("127.0.0.1",self.server.server_port,timeout=5)
        try:
            conn.request(method,path)
            res=conn.getresponse()
            return res.status,res.read(),dict(res.getheaders())
        finally:
            conn.close()

    def test_get_api_and_headers(self):
        status,body,h=self.request("GET","/api/overview")
        self.assertEqual(status,200)
        self.assertEqual(json.loads(body)["mode"],"SYNTHETIC")
        self.assertEqual(h["X-Content-Type-Options"],"nosniff")

    def test_no_mutations_or_file_leak(self):
        self.assertEqual(self.request("POST","/api/overview")[0],405)
        self.assertEqual(self.request("GET","/../.env")[0],404)
        self.assertEqual(self.request("GET","/data/experiments/manifest.json")[0],404)

    def test_ui(self):
        status,body,_=self.request("GET","/")
        self.assertEqual(status,200)
        self.assertIn(b"DPN PhaseGate",body)


if __name__=="__main__":
    unittest.main()
