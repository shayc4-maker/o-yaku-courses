---
name: ship-plans-to-model
description: Workflow for turning a ship model's 2D plans (body plan, half-breadth/waterline plan, sheer plan, deck plans, profile) into approved reference POINTS, splines, frames and a 3D build with a human builder approving every step; no line tracing. Use for any POF/frame-by-frame wooden ship model (Royal Caroline 1:48 is the worked example in royal_caroline/; full playbook in royal_caroline/playbook/ and royal_caroline/ship_plans_playbook.zip).
---
# Ship plans -> approved points -> splines -> frames -> 3D

Reply in the builder's language (Hebrew for Royal Caroline), minimum tokens. Read `royal_caroline/CLAUDE.md`, `STATE.md` (end = latest decisions) and the playbook (`royal_caroline/playbook/README.md`, esp. 01_rules, 08_problems_and_fixes). The builder is an expert and tired of guessing. **If you do not understand a line, an object or a rule, ask one precise question with numbers or a picture. Never invent a line, chord, radius or smoothing. Never trace lines.**

## 0. Ground rules
1. Body-plan lines and the approved outer frame lines are IRON. Mismatches are closed by adding a helper line (waterline/point set), never by moving iron.
2. NEVER trace pixels (no outline following, no bulk sampling, no fitting to ink). Minimum reference points (every 10-20 mm of arc, corners), chosen by you, snapped to the ink centre within +-1.5 mm, shown with ids/coordinates, approved, then a spline (interpolating cubic) or a straight where he says straight.
3. The builder's marks (drawn lines, coloured pixels, screenshots, edited 3dm) are DATA: read exactly, never drop a mark to get a nicer curve; if a mark disagrees with a hard fact, state the offset in mm and ask (original plan wins unless he says otherwise).
4. One item per round; 2D first; 3D only after approval; rounds of 5 frames once the method is approved. One clear image per ask (phone). Say what was not checked.
5. Report numbers (deviation mm, curvature sign changes, min radius, areas, solid validity). Commit+push after every deliverable, add a few lines to STATE.md, send files with SendUserFile. Files > 30 MB stay out of git.
6. Ask what an object is before using it (dark rectangles were gun ports; the "step" differs between plans).

## 1. Calibration
Per-axis affine on known features with residuals; one centre line per view; re-sent scans are REGISTERED to the aligned image by template matching (rms ~0.4 px), not recalibrated; coloured-pixel PDFs are extracted at full resolution (`pdfimages -all`) and converted through the registration + inverse calibration. Details: playbook/03.

## 2. Order of work
Body plan stations -> waterlines (top view) -> sheer-plan lines and backbone (keel/keelson from the STEP or `data/step44_profiles.json`) -> hull loft -> frame outer lines by waterline progression (approved = iron) -> bow (rabbet, planes, deck waterline Z=101, bulwark line, step = frame 1) -> 3D blanks -> keel context -> splitting/marks/numbering (builder's rules from sections b2/b3, only after he explains).

## 3. Frames (final rule, playbook/05)
Layers A (X-4..X), F (X..X+4); faces back/mid/front. Outer exact line to the keel wall (Y=2.65); ONE horizontal at the pocket floor and ONE under the keelson (the base grows toward the stern); inner line concave 3.2 mm offset (shapely offset_curve against loops; JOIN=min(34,8D); JMAX=40); common flat blank = envelope of the three faces, glued then hand-sanded to the LASER marks (no bevel cuts); top cut straight along the bulwark lower line. Always print the table of face areas/validity and look at a 5-frame sheet.

## 4. Splines
Interpolating cubic `splprep(s=0)`; report curvature sign changes (>1e-3), min radius, deviations. Smooth only on request (weighted, smallest s with 0 sign changes, report deviation). Tangent continuity by including the neighbour's points. Segment curves, not one spline over steps. Estimated points are labelled estimates.

## 5. Delivery (playbook/07)
3dm layers; picture planes with the PNG beside the 3dm (Rendered mode); NURBS from splprep knots; no `ClosestPoint` on NurbsCurve; OCP segfaults if a STEP path is missing; background + Monitor for long jobs; no `| head` on scripts that save outputs; compare edited 3dm to the original by sampling to find what he changed; `.rhl` is only a lock file.

## 6. Failure patterns (full list: playbook/08)
Tracing lines; moving iron; dropping his marks; plotting only part of a line (top segment missing); overwriting another plan's registration file; assuming an object's meaning; smoothing iron; showing renders where the detail he asked about is invisible; answering from memory instead of reading the file; changing the approved backbone without asking.
