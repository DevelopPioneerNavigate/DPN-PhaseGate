# PG-PROT-NULL-001 | Proposed blinded paired-station null study

**[Evidence workflow](../physics/EVIDENCE-WORKFLOW.md) · [Safety guide](../safety/SAFETY-COMMAND.md)**

<img src="../../assets/phasegate-research-pipeline.svg" width="100%" alt="Pre-registered sham and null controls"/>

> **Visual guide:** This remains a draft instrumentation test. No real physical experiment or transfer event has occurred, and the diagram does not authorize testing.

---


**STATE: DRAFT, NOT AUTHORIZED TO PERFORM.** No data collected; no PhaseGate apparatus exists. Formal preregistration requires a versioned signed protocol and real qualified safety review.

**Question:** When isolated stations A and B have no physical transit path, can we operate an observation workflow without falsely classifying a sensor glitch, lighting event, substitution or timing issue as an object crossing?

## Hypothesis & null expectation
Linked **H-PG-001**. Baseline predicts **no genuine object transfer** between separated stations. This study is about **false positives**, not creating a physical portal.

## Proposed measurement
- Object: inert, individually tamper-marked nonhazardous sample, mass and photographs documented.
- Stations: separated, transparent, independently sealed/inspected units; no hidden physical connection or moving device.
- Instruments: two calibrated scales; independent and redundant video; local environmental readings and time-offset logs.
- **Primary outcome:** erroneous 'arrival at empty B' classifications during predeclared sham trials after independent human confirmation.
- **Secondary outcomes:** sensor drift, dropout rate, observed clock skew, missed camera events and disagreement between witnesses.

## Planned pilot protocol (revise before authorization)
1. Record operators, approvals, identifiers, signed calibration and independent enclosure inspection.
2. Record pre-trial scale-zero and reference masses at each unit; quantify repeatability by repeated measures.
3. Pre-register sham/control trial counts and statistical analysis **before** collecting any real data (no post hoc favorable exclusion).
4. Randomly assign disguised trial labels; reserve an independent custodian of assignments.
5. Capture continuous independent video and all raw sensor data for each trial. Conduct safe null conditions only.
6. Process data while classification is blinded, then unblind and compare events.
7. Recheck calibration and clock drift after sessions, preserve source files unmodified and compute SHA-256.
8. Document all missing or inconclusive data, errors, false positives and null results; do not remove unfavorable observations.

## Criteria and stop rules
A sensor excursion alone **never counts as transfer**. A candidate event requires cross-modal synchronized evidence and independent verification; before any physics claim, exclude conventional routes, intentional or accidental replacement, electronics, synchronisation and processing artifacts. Stop if power faults, overheating, compromised seals or unsafe conditions occur.

A project-specific sample size, tolerances, false-alarm threshold and uncertainty budget must be approved before this protocol moves beyond draft. They are not invented here.

## Recordkeeping
Create `data/experiments/PG-YYYYMMDD-NNN.json` only for **actually conducted and reviewed** studies. Synthetic/demo files must remain outside the manifest. A green validator is not scientific validation.
