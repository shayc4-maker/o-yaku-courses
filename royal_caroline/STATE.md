# Royal Caroline 1:48 — project state (handover for a new session)

## Who / what
- The builder works in Hebrew, uses **Rhino 8 on a Mac**, and checks everything visually against the plans.
- Goal: a POF (plank-on-frame) model at 1:48. Deliverables are a Rhino 8 `.3dm`, DXF cut files and QA overlays (plan + lines).
- Thickness comes from the plans; the builder chooses stock later.
- **Working style the builder wants:**
  - Lines only until final approval.
  - Minimal tokens and few interim reports.
  - Send whole results, plus a short list of open questions.

## Coordinates (model mm, 1:48)
- **Axes:**
  - X is forward of station 18, which is the heel of the sternpost.
  - Z is up from the baseline.
  - The keel bottom is at Z = -9.37.
- **plan_5 (A3/3 inboard profile)** to model, in `py/p5map.py`:
  - K = 1000/244.8/48, R5 = 1.00146
  - X = ((4197.6+(px-1280)*R5)-4194.98)*K
  - Z = (2045-py)*K*R5-9.37
  - `model_to_p5` is the inverse.
- **plan_1a profile:**
  - X = (px-4194.98)*K
  - Z = (2104.73-py)*8.689/102.1

## Files in this folder
- **`plans/`:** aligned scans `plan_1a_aligned.png`, `plan_1b_aligned.png` and `plan_5_aligned.png`.
  - Other plans (`plan_2a`, `2b`, `4a`, `4b`, `6`–`13` `.tif`) and the reference pack are **not** included.
  - Ask the builder to re-upload them if needed. They are on the builder's Mac under `~/Documents/ship models/royalcaroline`.
- **`data/`:**
  - `frames_X.json`: 45 frame X positions. Frame 25 at 303.76 was added; it is the midship frame and is not drawn in plan_5.
  - `parts_v10.json` and `frame_pieces_v10.json`: the full previous hull. It has 1,074 parts, collision-free, but many parts were judged inaccurate.
  - `backbone_contour_v5.json`: the outer backbone contour, with `seats` = per-frame block X-ranges [a, b, z].
  - `backbone_split_v5.json`
  - `seats_auto.json`, `fwd_steps_plan5.json`
- **`scan/`:** the builder's dot-marking pass.
  - `backbone_trace_sheets.pdf/.json`: 5 printed A4 sheets at 2:1, strips A–F with corner marks.
  - `dots_scan_5pages.pdf`: the builder's scan. Green dots are straight-line vertices; blue dots are spline points.
  - `dots_merged.json`: 319 dots already registered into model coordinates (id, X, Z, c = G/B).
  - `lines_v1.json`: the lines built from them (current, v2).
- **`rhino/`:**
  - `RoyalCaroline_backbone_lines_v2.3dm`: current lines, dots and the v5 contour.
  - `RoyalCaroline_backbone_contour_v5.3dm/.dxf`
  - `RoyalCaroline_hull_1to48_v9.3dm`: the old whole hull.
  - `README_HE.md`
- **`py/`:** all scripts. The key ones:
  - `p5map.py`
  - `bbv5.py`: v5 contour.
  - `dots.py`: scan registration via corner marks.
  - `buildlines.py`: dot chains to lines, with frame snapping.
  - `vlines.py`: overlay QA.
  - `ids.py`: numbered-dot render.
  - Scripts expect a scratch layout (`a/`, `out/`, `scan2/`), so adjust paths.

## Rules the builder set (keep!)
1. **Faithful to plan_5**, with smooth lines.
   - Green dot to green dot = **straight line**.
   - Blue dots between greens = **spline** through them.
2. **Anything that touches the frames aligns to the frames, not to the dots.** Dots are reference only there.
   - Frame block X edges come from `backbone_contour_v5.json` seats.
   - Each frame gets a small **horizontal** seat step for easy building.
3. **Keelson is a separate part with its own contour.**
   - It is notched over the frames, about 1 mm deep. The frames rise into keelson notches.
4. **The stern knee is included** (upper and lower edges marked). The **post top is raised to Z 90.5**, per dots 244/245; the v5 contour still stops at 83.8 and must be updated.
5. When the builder sends a red sketch, it is **shape/topology reference only, not precise**. Use the dots for positions.

## Current status (approved vs open)
- **Done:** lines v2 (`qa/lines_*.png`), after the builder's red-sketch corrections:
  - **Stern:** the post fore face is one stepped line with transom notches: 247-246-250-251-254-253-256-257-259-260-261-262.
  - **Inner post:** a straight line 262→282.
  - **Knee lower edge:** ends 269-270-275; the upper edge ends at 271, and 271-275 closes the knee toe.
  - **Bow:** two continuous stem splines:
    - 1-4-5-11-22-32-40, ending at hook 40/41.
    - 0-3-18-20-25-28-34-38, ending at hook 38/39.
  - **Head:** the V 12-26-24.
  - **Keelson underside:** built from the frame blocks.
- **Builder's last feedback:** none yet on v2 (the session ended here).
- **Next steps:**
  1. Builder approves the v2 lines, or sends topology fixes as chains of dot ids or a red sketch.
  2. Extend the contour (post top at 90.5) and build closed parts from the lines: keel, false keel, hog, post, inner post, deadwood pieces, knee, keelson, stem/apron/gripe/head pieces. Output `.3dm` (layers per part) plus DXF.
  3. Then: complete the forward cant frames to the correct height; refit the frames to the new seats; continue fixing parts one by one (the builder judged the earlier full model "good from afar, full of mismatches").
- **Lesson learned:** guessing dot connectivity from the hatched plan is unreliable. Ask the builder for chains or sketches instead, then build the geometry.
