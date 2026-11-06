---
name: ship-plans-to-model
description: Workflow for turning a ship model's 2D plans (body plan, half-breadth/waterline plan, sheer plan, midship sections) into approved reference points, splines, frames and a 3D build with a human builder approving every step. Use for any POF/frame-by-frame wooden ship model (Royal Caroline 1:48 is the worked example in royal_caroline/).
---
# Ship plans -> approved points -> splines -> frames -> 3D

Reply in the builder's language (Hebrew for Royal Caroline), minimum tokens. Read `royal_caroline/CLAUDE.md` and `STATE.md` first. The builder is an expert; he is exhausted by guessing. **If you do not understand a line or a rule, ask one precise question with numbers or a picture. Never invent a line, a chord, a radius or a smoothing.**

## 0. Ground rules that were learned the hard way
1. The **body plan lines are iron**: they decide. Mismatches with other plans are closed by adding a waterline, never by moving a body plan line.
2. Never trace pixels in bulk. Work with a **minimum number of reference points** (every ~10-20 mm of arc, plus a corner point where a straight begins) and let a spline join them. Pixels are used only to centre a point on the ink.
3. **One item per round, show, wait for approval** (a station, a line, a frame). Frames/stations in rounds of 5 once the method is approved. The builder says "approved" per item; only then record it in `data/*approved*.json`.
4. Always show the **2D drawing with ids and coordinates first**; build 3D only after approval. Say plainly what was not checked.
5. Drawings: point = circle, label with number and Y,Z; zoom crops where lines are dense; the builder reads them on a phone, so one clear image per ask.
6. Commit and push after every deliverable, update `STATE.md` (few lines), send files with SendUserFile.

## 1. Calibrate every plan before using it
- Fit pixel->mm per axis on known features (station verticals, waterline rows, keel width). **Scales differ per axis and per plan** (e.g. aft body plan Y was 3.1 % small; half-breadth plan Y 0.0819 mm/px vs X 0.085). Check by overlaying known lines (builder splines, grid) on the image and report residuals.
- Cross-check plans against each other at crossings (station x waterline). Report std/max; do not "fix" the body plan.
- Typical image files live in `royal_caroline/plans/`; the DXF/3dm of lines is the builder's reference.

## 2. Reading lines with points (what works)
- Identify a line by **order counted from a reference side at the same row** (lines 1-2 mm apart are mis-snapped by "nearest ink"). Validate against already approved neighbours (a new line must be outside/inside the approved one).
- Track a line with a small ink follower along its tangent (`py/line_follow.py`); reject wide runs (crossings, labels). Hand-written labels and arrows are not lines.
- Where lines merge into a band, take the band centre, and say so; where they converge on a point (keel), define one shared convergence point (F) for all stations that end there.
- Straight segments (vertical tops, flat floors) get a **corner point** and a separate straight line.
- Splines: interpolating cubic through the approved points; check curvature sign changes; never smooth the iron lines.

## 3. Order of work (worked example)
1. Body plan stations (all), then waterlines in the half-breadth plan, then sheer-plan lines. Put them in one 3D lines file (grid/labels of the builder's original layout + approved lines only; old lines not reused).
2. Backbone: read keel/keelson from the builder's STEP (`py/step_chain.py`): the smooth ramp vertices are the spline; steps are notches. Do not use the stepped profile as a spline.
3. Hull = loft through the approved station splines (`py/hull_new_sections.py`); the section at any X is the exact hull line for a frame.
4. Frames: see section 4. 2D first, 5 frames per round, then 3D renders.

## 4. Double frames (Royal Caroline rules)
- Frame centre X from `data/frames_X.json`; layers A (X-4..X) and F (X..X+4), 8 mm total, 4 mm planks. Radial thickness 3.2 mm measured **in the section plane** (true offset), inner line = offset of the exact outer line (normalise the inner line with a smoothing spline, never the outer).
- **Cut blank (before sanding)**: A and F share ONE common outline = envelope of the three faces (inner minimum, outer maximum); glued first, sanded after gluing. Laser marks = the final (exact) face outlines at X-4, X, X+4. No step between layers.
- Keelson inner line = one smooth spline, no pockets. Keel top = surface spline with **1 mm** pockets (measured in the STEP; backbone.py NOTCH=1.0), pocket width = frame width 8 mm, floor spline parallel.
- At the backbone width (+-2.65 mm) only ONE horizontal straight line: the keel pocket floor. The exact (iron) outer line stops at the keel wall (vertical wall up to the floor); the inner line deviates slightly inward with its own spline and meets the end of the floor line with a sharp corner. No radii, no tangent joins, no seat line, no legs.
- Bow: keel and keelson meet at the stem start (X=526.6, gap tapers to 0, never negative).
- Allowance = difference of the spline levels at the layer faces (not a constant).

## 5. Tools (royal_caroline/py)
`line_follow.py`, `bodyplan_points_all.py`, `bodyplan_aft_st_fix.py`, `bodyplan_splines_final.py`, `wl_top_all.py`, `step_chain.py`, `hull_new_sections.py`, `keel_keelson_v2_2d.py`, `frame_one_2d.py` (current frame rule), `build3d_blanks.py` + `render3d_blanks.py` (3D blanks with laser lines; renders with three.js in headless chromium: `npm i three playwright-core`, `--use-gl=swiftshader`). VTK/Matplotlib 3D are not usable offscreen here.

## 6. Failure patterns to avoid
- Inventing connecting lines or smoothing iron lines (cost many rounds).
- Showing renders where the detail the builder asked about is invisible (use a zoom).
- Answering a reference question from memory instead of reading the file; check what a file contains before saying it lacks something.
- Changing the approved backbone without asking. Build commits: never commit wheels/large files (100 MB GitHub limit).
