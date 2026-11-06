# Continuation prompt (paste into a new conversation)

Read in this order: `CLAUDE.md`, `.claude/skills/ship-plans-to-model/SKILL.md`, `STATE.md` (end of file = latest decisions). Hebrew, minimum tokens, one item per round, 2D first, 5 frames per round, never invent lines, ask one precise question when unsure.

## State on 2026-11-06
- Body plan (18 stations), waterlines I-VII (top view), line D (side) approved; lines file `rhino/RoyalCaroline_lines_v2.3dm`. Hull loft = `py/hull_new_sections.py` (exact hull line at any X).
- Backbone from the builder STEP (smooth keelson spline, keel surface spline, 1 mm pockets 8 mm wide, `data/keel_keelson_v2.json`). Builder decision: backbone is taken as is and lowered 0.6 mm vs the body plan (= frames raised 0.6 vs the keel; confirmed by the B3 / plan_6 check). Implemented as `SHIFT=0.6` in `py/frame_arm.py`; the backbone data files are NOT yet rewritten.
- Frame rule (final, builder): exact outer (iron) line ends at the keel wall (Y=2.65, vertical wall); ONE horizontal at the backbone width on the keel (pocket floor) and ONE under the keelson (keelson spline) - the frame fills the gap; the inner line is one concave, never-dipping curve (monotone cubic from the seat corner, tangent join to the exact 3.2 mm offset line, join moved out until concave). Blank = one common cut outline for A and F (envelope of the 3 faces), glued then sanded; laser lines = final faces.
- Open: builder said left and right arms are fixed, the MIDDLE (centre, seat/inner line near the keelson) still does not work for him; check after the 0.6 raise. Frame 1 face X+4 lies beyond the stem start (526.6). Stern frames 46-48 not rebuilt on the new backbone. Frames 6-45 not re-run with the final rule (use `py/frames_arm_batch_2d.py`), 3D blanks (`py/build3d_blanks.py`) not updated to the final arm rule.
- Files for the next step: `qa/frames_bottom_side_shift.png`, `py/frames_arm_batch_2d.py`, `py/frame_arm.py`.
