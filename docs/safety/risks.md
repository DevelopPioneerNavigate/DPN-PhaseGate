# Risk register

**[Safety command](SAFETY-COMMAND.md) · [Experiment protocol](../protocols/PG-PROT-NULL-001.md)**

<img src="../../assets/phasegate-safety-gates.svg" width="100%" alt="How safety mitigations are verified"/>

> **Visual guide:** Every listed risk stays open until the relevant hardware-specific mitigation and responsible reviewer have been documented.

---

| ID | Risk | Safeguard | Status |
|---|---|---|---|
| HZ-001 | Electrical/fire hazard | Low-voltage rated supplies, inspection, protection | Open |
| HZ-002 | False mass/identity event | Calibration + unique blind tag + witnessed baseline | Open |
| HZ-003 | Timestamp/data mismatch | Independent UTC logs and clock-offset measurement | Open |
| HZ-004 | Concealed substitution/path | Transparent enclosure, tamper seals, spatial inspection | Open |
| HZ-005 | Missing/altered raw evidence | Immutable storage, hashes, chain of custody | Open |
| HZ-006 | Hazardous experimental escalation | No-go pending qualified external safety review | Blocked |
| HZ-007 | Misleading claims | Explicit claim levels and independent review | Open |
Owners and approvals remain unassigned until real people accept responsibility.
