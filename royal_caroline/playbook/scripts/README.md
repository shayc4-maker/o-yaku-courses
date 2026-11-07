# Scripts (copy to `py/`, run from the project root `royal_caroline/`)
Paths inside point to `data/`, `plans/`, `qa/`, `rhino/` of the Royal Caroline project; upload paths (`/root/.claude/uploads/...`) are session specific — replace. Run frame batches with `JMAX=40`.
- Calibration/registration: p1a_strip.py (warp plan_1a to model mm), p5map.py (plan_5), register_plan1a_new.py / register_plan5_new.py (template-match registration), p1a_marks.py (builder's coloured pixels -> mm), p5_strip.py.
- Lines: bulwark_line_spline.py, bulwark_marks_3dm.py (points + curves on the picture for the builder), bow_deck_waterline_v3.py, rabbet_iron_and_planes_v4.py, deck_plan_on_planes_3dm.py, lift_bottoms_half.py, ingest_half_lifted.py.
- Frames: frame_arm.py (the rule), frames_batch_2d.py (older helper F), frame_blank_v6.py, frames_blank_batch.py (2D + npy), frames_blank_3d_batch.py (3dm), frames_tops_v5.py, frames_on_keel_3d_v2.py, frames_on_keel_side_check.py.
- STEP helpers: step_chain.py, hull_new_sections.py.
