# Ship-plans playbook (Royal Caroline 1:48 POF) — how to extract parts from 2D plans with POINTS and SPLINES only

Audience: an AI agent (or a human) who gets scanned plans of a ship (body plan, half-breadth/waterline plan, sheer plan, deck plans, profile with deck details) plus the builder's STEP/3dm files, and must produce approved lines, frames and a 3D model with the builder approving every step.

Read in this order:
1. `01_rules.md` — non-negotiable rules (read twice).
2. `02_workflow.md` — the phases and the approval gates.
3. `03_calibration.md` — how to bring every plan into model millimetres (and how to register a re-sent scan).
4. `04_points_and_splines.md` — how to get points (never by tracing) and how to make splines.
5. `05_frames.md` — the frame rule (outer iron line, keel/keelson seat, inner line, blank, laser marks).
6. `06_bow.md` — rabbet, stem, 5 plank planes, deck waterline, bulwark line (the hardest part).
7. `07_rhino_delivery.md` — Rhino/3dm/STEP delivery and the library pitfalls.
8. `08_problems_and_fixes.md` — every problem met so far: symptom, cause, how not to repeat it.
9. `09_open_items.md` — what is still open for the Royal Caroline.
`scripts/` holds the working scripts (copy, then adapt); `data_examples/` holds small data files showing the formats.
`README_HE.md` is a short Hebrew summary for the builder.
