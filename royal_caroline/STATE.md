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
5. **SOS images and the reference plans are for orientation only.** Never take dimensions or geometry directly from them; measurements come from the builder's plans (plan_5, plan_1a/1b) and dots.
6. When the builder sends a red sketch, it is **shape/topology reference only, not precise**. Use the dots for positions.

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

## Research (Ships of Scale), added 2026-10-15
- **`research/RoyalCaroline_SOS_references.html`:** an index of 184 plan and structure images from 13 SOS threads. Each entry has a thumbnail, a "full" link (needs login) and a "post" link.
- **Most relevant: Jeronimo (Karl), 1:48 POF from the same Bellabarba 1:48 plans.**
  - Thread: https://shipsofscale.com/sosforums/threads/royal-caroline-1749-m-1-48-by-jeronimo-completed-build.3178/
  - #1: disposition of frames.
  - #6, #7, #35, #36: per-frame timber drawings (made by "Mike").
  - #3, #4, #33, #34: the backbone, with a **horizontal seat notch per frame** (same as the builder's rule).
  - #39, #41: hawse timbers.
  - #58–#74: keelson and riders.
  - #70–#77: stern framing.
  - **Lesson from his build:** leave bevel allowance on the frames; his first frame set ended up too thin.
- **Original NMM draughts (1749, 1:48):** photos are #26–#29, #847–#850, #1172 and #1173.
- **Planned:**
  - The builder will download the full-size images manually and upload them.
  - **Optional, not set up yet:** an SOS login cookie as a Network secret, so sessions can fetch full-size images. Use header `Cookie`, host `shipsofscale.com`, value `xf_user=...`.

## Session 2026-10-15 (cont.)
- Builder approved lines v2; uploaded 5 full-size SOS images to `research/sos_full/` (1: hawse timbers/filling pieces, 2: frame 5 sections, 3-4: frame 21 sections with chocks, 5: disposition of frames, 610.5 mm between frames 1-18 and 627.0 overall).
- `py/faces.py` (shapely polygonize) on `scan/lines_v1.json` closes only 5 regions: keel in 3 scarfed pieces (split at X=168.3 and 333.6), a deadwood wedge (X 10-60, Z 1-11) and a stern-post piece (X 5-16, Z 10-31). QA: `qa/faces_v2.png`.
- The rest (stem, apron, gripe, head, post, knee, keelson) is open chains and needs the builder to name the part boundaries (chains of dot ids or a red sketch) before closed parts are built.
- Batch 2 of SOS images saved in `research/sos_full/` (6-10): 6 hawse timbers end view (HT1-10, deck clamps), 7 photo of the stepped inner face of the frames/clamps, 8 photo of the bow hawse timbers with numbered pairs, 9 photo of a hawse-timber template with the first frame's timbers, 10 hawse timbers sheet (plan, side view, end view with dimensions).
- Batch 3 of SOS images saved in `research/sos_full/` (11-15): 11 stern frames 40-47 with the transom/counter framing and a laminated stern block; 12 close-up of the laminated transom-seat steps; 13 bow-on view of the frame set with cross-beams and the keel/stem; 14 aft end showing the notched (joggled) keelson/deadwood seat; 15 full frame set from the side with the continuous top rail.
- Image 16 saved in `research/sos_full/`: stern frames 38-45 beside the transom frame, side view of the aft end.
