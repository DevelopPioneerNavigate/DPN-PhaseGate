"""PG-01 arrival-cadence health, never clock synchronization.

USB receipt timestamps can identify stalls/latency variation; they do not reveal
absolute Pico-to-PC time offset or the time at which an external event happened.
"""
from __future__ import annotations

import math
import statistics
from collections import deque


class CadenceHealth:
    def __init__(self, maxlen=120):
        self.points=deque(maxlen=maxlen)
        self.reset_count=0

    def observe(self, device_uptime_ms, host_monotonic_ns):
        if not isinstance(device_uptime_ms,int) or not isinstance(host_monotonic_ns,int):
            raise ValueError("timing counters must be integer")
        if device_uptime_ms<0 or host_monotonic_ns<0:
            raise ValueError("timing counters cannot be negative")
        if self.points and (device_uptime_ms<=self.points[-1][0] or
                            host_monotonic_ns<=self.points[-1][1]):
            self.points.clear()
            self.reset_count+=1
        self.points.append((device_uptime_ms,host_monotonic_ns))

    def summary(self):
        if len(self.points)<3:
            return {"state":"INSUFFICIENT SAMPLES","interval_samples":0,
                    "absolute_clock_offset_known":False,"synchronized":False}
        entries = tuple(self.points)  # deque does not implement slice indexing
        device=[(b[0]-a[0]) for a,b in zip(entries,entries[1:])]
        host=[(b[1]-a[1])/1e6 for a,b in zip(entries,entries[1:])]
        if not device or min(device)<=0 or min(host)<=0:
            return {"state":"COUNTER ANOMALY","interval_samples":0,
                    "absolute_clock_offset_known":False,"synchronized":False}
        differences=[h-d for h,d in zip(host,device)]
        return {"state":"HOST ARRIVAL CADENCE ONLY","interval_samples":len(differences),
                "mean_interval_error_ms":statistics.mean(differences),
                "arrival_jitter_ms":statistics.pstdev(differences),
                "max_abs_interval_error_ms":max(abs(v) for v in differences),
                "absolute_clock_offset_known":False,
                "synchronized":False,
                "interpretation":"USB receive latency, buffering and MCU interval variability are conflated; "
                "cannot infer cross-station event timing."}
