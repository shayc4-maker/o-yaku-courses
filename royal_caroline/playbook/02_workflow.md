# 02 Workflow and approval gates

Phase 0 — Inventory. List every upload (plans TIFF/PNG/PDF, STEP, 3dm, DXF), say what each contains, what is missing. Check file sizes/pixels (a "same" scan can differ in size; compare bytes before assuming).
Phase 1 — Calibration (03). Output: calibration JSON + overlay with residuals. Gate: builder sees residuals.
Phase 2 — Reference lines, in this order, each as points -> 2D picture -> approval -> spline:
  1. body plan stations (all) — iron
  2. waterlines in the half-breadth plan (new waterlines are added to close mismatches)
  3. sheer-plan lines (side view): keel/keelson from the STEP (smooth ramp vertices are the spline, steps are notches)
  4. hull loft = lofted body plan; the section at any X is the exact hull line
Phase 3 — Frames. Outer lines per face (X-4, X, X+4) from points in space via waterline progression (05). Approved set is saved as `frames_outer_approved_vN.json` and is iron. Rounds of 5 frames.
Phase 4 — Bow (06): rabbet, stem continuation, planes, deck waterline, bulwark line, step = frame 1.
Phase 5 — 3D blanks per frame (A/F, common blank, laser marks), then keel/keelson context, then splitting into parts + marks + numbering (the builder has rules for the split; example in plan_6 sections b2/b3; do it only after he explains).
Phase 6 — Assembly checks (clashes, contact at keel/keelson), then delivery.

Gate protocol each round: (1) say in one line what you are about to show, (2) show the image, (3) list the open questions (max 3, numbered), (4) wait. After approval record data + STATE.md + commit + push + send files.

Versioning: never overwrite an approved file; make `_v2`, `_v3`. Keep the script that made each output next to it (`py/name_vN.py`).
Decisions are recorded with date and the builder's words (translated) in STATE.md.
