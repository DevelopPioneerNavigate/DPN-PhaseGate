"""Clock arrival cadence diagnostics are expressly not time synchronization."""
import unittest
from desktop.timing_quality import CadenceHealth


class TimingTests(unittest.TestCase):
    def test_untrained_health_reports_no_clock_sync(self):
        c=CadenceHealth()
        self.assertEqual(c.summary()["state"],"INSUFFICIENT SAMPLES")
        self.assertFalse(c.summary()["synchronized"])
        for i in range(1,8):
            c.observe(i*120, i*120_000_000 + (i%2)*2_000_000)
        report=c.summary()
        self.assertEqual(report["state"],"HOST ARRIVAL CADENCE ONLY")
        self.assertFalse(report["absolute_clock_offset_known"])
        self.assertFalse(report["synchronized"])
        self.assertGreater(report["arrival_jitter_ms"],0)

    def test_reset_invalidates_prior_cadence(self):
        c=CadenceHealth()
        for i in range(5):
            c.observe(i*125+1, i*125_000_000+1)
        c.observe(1,1)
        self.assertEqual(c.reset_count,1)
        self.assertEqual(c.summary()["interval_samples"],0)

    def test_reject_invalid_timestamps(self):
        c=CadenceHealth()
        with self.assertRaises(ValueError):
            c.observe(-1,1)
        with self.assertRaises(ValueError):
            c.observe("x",1)


if __name__=="__main__":
    unittest.main()
