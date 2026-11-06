# Royal Caroline 1:48 — project state (handover for a new session)

Working rules are in `royal_caroline/CLAUDE.md`; read them first.

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

## Parts v1 (2026-10-15)
- Builder approved lines v2 and said go ahead. Built 19 closed profile parts from `data/backbone_split_v5.json` (all valid polygons), sternpost top raised to dots 244/245 (Z 90.5). Script `py/build_parts_v1.py`; outputs `data/backbone_parts_v1.json`, `rhino/RoyalCaroline_backbone_parts_v1.3dm` (layer per part, closed polyline in XZ, Y=0), `rhino/RoyalCaroline_backbone_parts_v1.dxf`, QA `qa/parts_v1.png`.
- Open: `DEADWOOD_RISING` is still one part that includes the keelson with its frame seat steps; per rule 3 the keelson should be a separate notched part. Parts are 2D profiles (no thickness yet; builder picks stock).

## Final division DXF from the builder (2026-10-15)
- Builder supplied `rhino/ref_final_from_builder.dxf` (layers 01_BODY_OUTER, 02_KEELSON, 03_STERN_KNEE (= keelson underside), 04_AFT_DIVISIONS, 05_KEEL_HOG_FALSEKEEL, 06_STEM_APRON, 07_HEAD_GRIPE, 98_JOINED_REVIEW_CURVES; plan_5 image reference). Same model coordinates as parts v1 (X forward, Z up, in XZ at Y=0). It supersedes `backbone_split_v5` for the division.
- Builder's instruction: make sure the 45 frame seats are in place and the seat verticals meet the keelson boundary at the top and the keel boundary at the bottom; excess goes. Examples are at the start (frames 0-1) and end (frame 44).
- `py/fix_seats.py` -> `rhino/ref_final_seats_v1.dxf`: per frame (seats from `backbone_contour_v5.json`, identical X/Z to the DXF) two full verticals plus floor and notch-top horizontals on new layer `10_FRAME_SEATS`; 176 old vertical stubs removed; keelson-underside curve (03) trimmed inside each pocket. Notch tops for frames 0, 1, 44 come from layer 98 (36.9, 32.49, 33.03). Original file untouched. QA: `qa/seats_v1_*.png`. Pending builder confirmation of this reading.

## Solids v1 (2026-10-15)
- Builder: "close the shapes and make solids, I'll fix from there". The builder's DXF curves do not form closed loops (gaps, open ends), so polygonize/raster fill leaked; instead `py/build_solids_v1.py` takes the 19 closed v5 parts (post top 90.5) and adds two new closed parts built from the builder's DXF curves: KEELSON (red top curve, blue underside with the 45 frame pockets, ends X 41.2 / 526.6) and STERN_KNEE (upper/lower 03 chains to the post fore face). KEELSON/STERN_KNEE take priority: DEADWOOD_RISING was cut where it overlapped them (slivers <7 mm2 dropped).
- Outputs: `rhino/RoyalCaroline_backbone_solids_v1.3dm` (layer per part: closed profile curve at Y=0 + solid 5.3 mm sided, centered on Y=0, all validated IsSolid/IsValid), `data/backbone_parts_v2.json`, `qa/solids_v1_profiles.png`.
- Not verified against the builder's final division: v5 split is still the basis for keel/false keel/hog/deadwood/post/stem/apron/gripe/head; the builder's 04-07 layers were not used to redefine them. 5.3 mm sided is the body-plan backbone width from README_HE; builder can change.

## Builder's corrected solids: `rhino/backbone_builder_44.STEP` (SolidWorks 2024, 2026-10-15)
- 18 valid solids, all 4.0 mm sided (Y 0 to 4), profiles in XZ, same model coordinates. Read with `py/read_step.py` (OCP via `pip install cadquery-ocp`) and `py/step_profiles.py`; profiles in `data/step44_profiles.json`, QA `qa/step44_profiles.png`. This supersedes solids v1 (5.3 mm).
- Differences from solids v1: false keel is one piece; hog, rising deadwood, stem and apron are merged into one body (Boss-Extrude2[2], X -0.9..568, Z up to 116.6); keelson (Boss-Extrude4[4]) runs X 41.2..542.6 up the bow; stern knee Boss-Extrude3[3]; sternpost Boss-Extrude5[3] to Z 90.5; three extra aft bodies at X -30..0 (Split1[1], Split1[2], Boss-Extrude4[2], Z up to 134) that were not in my parts; knee of head/gripe pieces re-cut (Boss-Extrude5[1], [2], [5], 6, 2[1]).
- Builder's .x_t (Parasolid) could not be read here; the STEP replaced it.

## Reference: 45 frames on the builder's backbone (2026-10-15)
- Builder: backbone thickness must come from the plan scale, not 4.0 mm; 5.3 mm (254 mm real, body-plan backbone width, `README_HE.md`) is used and centered on Y=0. Builder wants a reference file with all 45 frames on the new keel, then to continue fixing the forward part from the new photos.
- `py/frames_on_keel.py` -> `rhino/RoyalCaroline_frames45_on_new_keel_REF.3dm`: layer `BACKBONE_builder` (18 solids rebuilt from `data/step44_profiles.json`, 5.3 mm; Boss-Extrude5[2] has an inner void that was not cut) + 45 layers `FRAME_nn` (533 v10 frame timbers, 4 mm each, layers A and F, solids). QA `qa/frames45_on_new_keel.png`, table `data/frames_vs_seats_v1.json`.
- Finding: frame X vs seat centre agree within 0.64 mm; floor bottom vs seat floor differs by +4.7 mm (floating) aft to -3.9 mm (cutting in) forward, so frames need refitting to the new seats (the v10 frames are not refitted yet).

## Forward frame: hawse timbers HT1-HT10 (2026-10-15)
- Builder: the forward frame is 10 vertical planks HT1..HT10 (5 per side, parallel to the centre plane), as in the SOS hawse-timber drawing (reference only); Frame 1 of that drawing = our frame 45 (X 528.03); strip width: (hull half-breadth at frame 45 - backbone half-thickness) / 5 = 8.97 mm; hawse holes only in HT2 and HT9, position approximate (builder: unknown).
- `py/bow_ht.py` -> `rhino/RoyalCaroline_bow_HT_v1.3dm`: layers HT1..HT10 (valid solids, S side = HT1-5 with HT5 next to the stem, P side = HT6-10), `HAWSE_HOLE_approx` (two 4 mm cylinders along X at Z 100, Y +-34, not cut), context layers BACKBONE_builder, FRAME_44, FRAME_45. Hull surface from `BOW_SURFACE_faired_sections` of `RoyalCaroline_hull_1to48_v9.3dm`; head extension above Z 88 and top Z 119.6 as in the old cant build. Each HT is the profile at the plank's inner face extruded 8.97 mm, so it carries a bevel allowance to be faired to the hull. Filling pieces and deck clamps of the drawing are not modelled. Old cants (`CANT_*`, `HAWSE_*` in `parts_v10.json`) are superseded.
- QA: `qa/bow_HT_v1.png`, profiles `data/bow_ht_profiles.pkl`.

## Sanding marks and stern check (2026-10-15)
- Builder: every part needs correct sanding marks; next the wing transom and aft part.
- `rhino/RoyalCaroline_bow_HT_v2.3dm` adds to the HT planks: `HT_SAND_LINE` (final hull line on the outer face of each plank, red), `HT_SAND_CONTOURS` (depth contours at 25/50/75 % across the plank width) and `HT_SAND_NOTES` (text dots with max in-plane allowance). Inner face edge = stock edge, no sanding along it. HT1 is too thin at its outer face for a line. Same kind of marks still needed on the other parts (frames, cants replaced).
- Stern: old stern parts (`parts_v10.json` groups stern/rudder: wing transom, transoms 2/3, 6 counter timbers, half frames H1/H2, fashion pieces; all flat, not canted) checked against the builder's backbone with OCP (`py/stern_clash.py`): the only clash is WING_TRANSOM with the raised sternpost (Boss-Extrude5[3], 51.7 mm3). Reference file `rhino/RoyalCaroline_stern_REF_v1.3dm` (new backbone, frames 1-6, old stern parts, wing transom on its own layer). The three loose bodies left of the post in the builder's STEP are the rudder (Z up to 134).

## Stern v2 (2026-10-15)
- Builder has no counter-timber angle image: use the angle of the stern windows in plan_5. Measured by Hough lines on the window frames in `plan_5_aligned.png`: 12.2-12.6 deg from vertical, top aft (median 12.2, longest lines 12.5).
- Photo 22 (`research/sos_full/22.jpg`, aft view into the stern) shows 6 counter timbers: an inner pair either side of the post top, then two pairs further out, standing on a laminated stepped block. Reference only.
- `py/stern_v2.py` -> `rhino/RoyalCaroline_stern_v2.3dm`: 6 counter timbers (4 mm, moulded 5 mm, standing on the wing transom at Z 78 up to 147.9, canted 12.5 deg, Y +-5.9/19.6/35.8 = 0.12/0.40/0.73 of the wing transom half width 49, proportions from the photo, not plan dimensions), wing transom + transoms 2/3 as in v10, sternpost notched where the wing transom crosses it (clash fixed), builder backbone (5.3 mm) and rudder (his three bodies). QA `qa/stern_v2.png`, params `data/stern_v2_params.json`.
- Not done: round-aft / round-up arch of the transom and counter tops (no source yet), half frames H1/H2 and fashion pieces not refitted to the new post, no sanding marks on stern parts, counter timber lower knee not modelled.

## Stern v3 (2026-10-15): positions, splay and arch from plan_7 and plan_4a
- Builder gave `plan_7.tif` (aft elevation of the stern and bow structure, 1/48) and `plan_4a.tif` (quarterdeck plan). Stored crops: `research/plan7_stern_crop.png`, `research/plan4a_stern_crop.png`. Plans are orientation/measuring aids at true 1:48 (0.0847 mm per 300 dpi pixel; checked against the beam and the metre bar).
- plan_7 text: the stern is based on six counter timbers tenoned into the wing transom, which sits between the two lower wales above the stern ports. The six timbers show as pairs of dashed edge lines. Measured on the lower band (clean, 6 pairs): centres at +-7.8, +-26.4, +-44.1 mm from the centre line; each leans INWARD at the top (converging towards the centre line) by 1.8, 5.5, 8.9 deg. (First version had the direction reversed; fixed after the builder's red-line overlay.) Tops follow the arch: drop 0.3 / 3.7 / 10.4 mm from the centre.
- plan_4a: aft edge arc of the stern in plan, sag 7.6 mm at half-width 38 mm (about R 95 mm, sag = y^2 / 2R); the same value reproduces the elevation arch drops (0.3, 3.7, 10.2), so both views agree. Used for the wing transom arc and the timber feet (forward shift = sag).
- `py/stern_v3.py` -> `rhino/RoyalCaroline_stern_v3.3dm` (supersedes v2): wing transom as an arc, six counter timbers raked 12.5 deg (side view, plan_5 windows), splayed inward at the top, tops on the arch, sternpost notched, builder backbone 5.3 mm and rudder. No clashes (OCP check). QA `qa/stern_v3_aft.png`, params `data/stern_v3_params.json`.
- Assumptions: foot Z 78, top Z at the centre 147.9 (old), the Y positions of the lower band apply at the foot; outer timber top ends at Y about 35 because of the inward lean. Not done: lower knee of the timbers, transoms 2/3 and half frames/fashion pieces not re-arched, sanding marks.

## Stern v4 and assembly v1 (2026-10-15)
- Builder: add the knee and the wing transom, all 45 frames, more 3D detail to review in Rhino; "you are making a mistake there, use the photos" (the mistake was not named; the hooked foot placed on top of the wing transom was being replaced).
- Reading of photos 11 and 22: the stack on the wall is a template/jig (stepped, traces the arch); the timbers lean aft at the top (rake) and converge inward at the top; the lower end bends forward (toward the frames) and flares outward at the bottom; the wide curved board at the bottom of photo 22 is the wing transom (arched in plan, ends forward of the centre).
- `py/stern_v4.py` -> `rhino/RoyalCaroline_stern_v4.3dm`: counter timbers keep rake 12.5 deg (plan_5 windows), inward splay 1.8/5.5/8.9 deg (plan_7), tops on the arch; NEW knee: straight rake down to Z 98, then a Bezier bend turning forward-down (55 deg below horizontal, 11 mm forward) landing on the wing transom top (Z 78). Knee proportions are placeholders read off the photos. Plan footprints of the six timbers marked on the wing transom (`WING_TRANSOM_MARKS`). No clashes (OCP). Overlay on plan_5: `qa/stern_knee_check.png`.
- `py/assembly_v1.py` -> `rhino/RoyalCaroline_assembly_v1.3dm`: builder backbone (5.3 mm), all 45 frames (v10 timbers, 533 solids, layers FRAME_01..45, NOT refitted to the new seats: floors float +4.7 mm aft to -3.9 mm forward), bow HT1-10 with sanding marks and hawse markers, stern v4 parts, rudder.

## Counter timbers from the builder's marks (2026-10-15)
- Builder scanned the marking sheets (`print_sheets_stern.pdf`) and said: in the top-view plan (plan_4a) use the black cubes inside his purple frames to measure the timbers. Six cubes at the aft edge, symmetric about the centre line (y_px 1098): y offsets 7.5 / 23.2 / 40.2 mm (inner/mid/outer), aft-face offsets 0 / +1.5 / +4.7 mm (aft line R about 170-190 mm), cube about 3.0 mm in Y by 3.5 mm in X. Agrees with plan_7 (7.8 / 26.4 / 44.1 at the foot, minus the inward lean up to the deck level). Data `data/stern_cubes_plan4a.json`, 2D for approval `qa/stern_cubes_plan.png`. Sheets A (plan_5) and B (plan_7) came back with almost no marks. Nothing rebuilt yet: waiting for approval of the 2D points.
- Deck level for the plan_4a cubes (builder: take it from the plans): the aft deck in plan_4a is the poop deck; poop beam tops (parts_v10, beam 02, X=35) Z 120.0 / 119.7 / 118.6 at Y 7.5 / 23.2 / 40.2 (QD roof beams are at X>=129, Z 128-131). Thickness: from the cubes at plan scale, 3.0 mm sided. Sheets A+B reissued at 75 % white blend, plan_5 up to its top edge (Z 165): `qa/print_sheets_stern_v2.pdf`.

## Builder's marks on sheets A/B (2026-10-15, scan `Document_2026-10-15_231149.pdf`)
- Registered with `py/scan_marks2.py` (corner crosses) -> `data/scan_marks_stern_2.json`. Yellow = curved lines; dots = points.
- Side view (plan_5): the counter timber is the far-left diagonal strip with four black cubes (cuts) at Z about 146.4 / 129.8 / 100.7 / 92.7: lean 19.8 deg from vertical (top aft), perpendicular width 2.5 mm (not the 12.5 deg of the windows, not 5 mm). Its lower end is a curved knee (yellow): two splines of 4 points each ending at the wing transom (marks at Z 71.9-75.8, so wing transom about 3.9 mm thick, not 6). Points `data/stern_side_points_v1.json`.
- Aft view (plan_7): yellow top arch is a clean parabola (max deviation 0.45 mm, vertex x 1410 px, centre line 1420 px, R about 85 mm: drop 9.4 mm at Y 40.6). The lower yellow curve (tuck near the rudder) is not used yet.
- 2D for approval: `qa/stern_points_2d_v1.png`. Waiting for approval before rebuilding the six timbers.
- Builder: straight lines are also given by dots on the page (not only yellow = curve). The 13 dots near the wing transom / stern knee band (`data/stern_lower_points.json`, ids 1-13 in `qa/stern_lower_points.png`) are corners of straight edges (blocks at Z about 75.8, 65.5/61.6, 57.5 and the diagonal band); connectivity to be given by the builder as id chains.
- Knee edges made parallel (builder): blue upper curve = offset of the green lower spline by 2.5 mm (the strip width): `data/stern_side_points_v2.json`, `qa/stern_knee_parallel.png`.
- Builder chains (images `research/builder_chains_transoms.webp`, `research/builder_note_strip_knee.webp`): transoms 1-3 are the closed blocks 1-2-C-4 (C at -3.4, 71.8), 7-8-10-9, 12-11-(11.0,53.3)-(-2.45,53.4); other dots (3, 5, 6, 13) belong to the keelson, ignore for now. Strip edges K1-K3 are straight lines through the cube corners (fit dev 0.44 mm, lean 20.4 / 19.0 deg); a small spline between K3 and the knee, parallel inner/outer, via the K4 corners. 2D for approval: `qa/stern_side_v3.png`, points `data/stern_side_points_v3.json`.
- Counter timber side profile as ONE closed outline (builder: all must join into a continuous closed shape, trimmed at intersections, closed at one point): start/end R0; segments: straight R0-R1, transition spline R1-JR, blue knee JR-EB, cap EB-EG on the wing transom top (Z 75.75), green knee EG-JL, transition spline JL-L1, straight L1-L0, top L0-R0. Joints are intersections (curves extended along end tangents where needed). `data/stern_timber_profile_closed_v1.json`, `qa/stern_timber_closed_v1.png`. Note: the fitted edges are 20.4 and 19.0 deg so the top is narrower (1.6 mm) than at K3 (2.8 mm); builder to say whether the strip should be parallel-sided.

## Stern v5 (2026-10-15): six counter timbers from the approved profile
- Builder: the timber really tapers, also in the aft view. `py/stern_v5.py` (OCP): profile = one closed outline of straight lines and 4-5 point interpolated splines (from `data/stern_side_points_v3.json`, joints at intersections); prism through the profile, cut by a wedge for the sided thickness t(z) = 3.0 - 0.0155 (z - 119) (3.0 mm at the poop deck from the plan_4a cubes; taper rate estimated from the plan_7 dashed pairs, 2.8-2.9 low band to 2.0-2.3 high band: ASSUMPTION), centred on y(z) = Y_cube + tan(splay)(Zdeck - z) (Y_cube 7.5/23.2/40.2 at poop deck Z 120.0/119.7/118.6; inward lean 1.8/5.5/8.9 deg), forward shift dx = kp (Y^2 - 7.5^2) from the plan_4a aft line, top cut by the arch (drop 5.85e-3 Y^2). Transoms 2 and 3 from the builder's chains (Y extents of v10: 37.8 and 12.7, no arch yet), wing transom block 1 as an arc in plan (Z 71.85-75.75, avg of the slanted ends). 9 valid solids, no clashes among them.
- Outputs: `rhino/RoyalCaroline_stern_v5.step` (true solids, no part names), `rhino/RoyalCaroline_stern_v5_meshes.3dm` (meshes, layer per part, for viewing), QA `qa/stern_v5_views.png`. Not done: stern knee/post/backbone clash check against these parts, no sanding marks, transoms 2/3 straight.

## Assembly v2 (2026-10-15)
- Builder: stern v5 looks good; apply it to the full file, fit the transoms next. `py/assembly_v2.py` -> `rhino/RoyalCaroline_assembly_v2.zip` (the 51 MB .3dm inside is git-ignored, regenerate with the script): frames 1-45 (v10, not yet refitted to the new seats), bow HT1-10 with sanding marks, builder backbone 5.3 mm notched by transoms 1-3 (post and stern knee, 1.1 mm2 each), rudder, stern v5 parts as meshes (six tapered counter timbers, transoms 1-3). Old stern parts removed. Next: fit the transoms (arch for 2 and 3, Y extents, mortises for the timbers), then frames refit to the new seats.

## Transoms from the builder's flat-back note (2026-10-15)
- Builder: no more views. In plan_7 the yellow lower curve is the last profile line of the stern; everything inside that frame is totally flat, including the backs of the transoms; check if this suffices to stand 3 parts; also consider the seats on the keel.
- Side view: the aft edges of T1-T3 (builder chains) are collinear: flat back plane leaning 16.8 deg (top aft), max deviation 0.09 mm. Aft view: the yellow bowl curve gives the half-width trimming each transom (T1 about 47, T2 38-42, T3 14 tapering to 2.4 at the post). Z for the curve from two anchors: widest point = wing transom mid Z 73.8, curve meeting the post = T3 bottom Z 53.35 (0.0688 mm per px vertical; the drawing is in perspective). Transom = side profile extruded in Y, trimmed by the outline prism along X. Previous wing-transom plan arc (R about 85-170) is dropped: the back is flat. 2D for approval: `qa/stern_transoms_2d_v1.png`, `data/stern_transom_outline_v1.json`.
- Transoms normalized (builder): uniform thickness 3.9 mm, horizontal top and bottom, both sides parallel to the flat back plane (lean 16.8 deg); depths (horizontal) 4.4 / 7.2 / 11.9 mm for T1/T2/T3, mid Z 73.8 / 63.5 / 55.4. `data/stern_transom_outline_v2.json`, `qa/stern_transoms_2d_v2.png`. Waiting for approval before building.
- Builder (photo 26 = same as 7): the transoms all meet a vertical frame; build it, cut the transoms to it; add 3 adjacent double frames at a single gap from 45 (his numbering: 45 = aftmost standard frame = our frame 1, X 35-43; bow = 1). 2D check `qa/stern_vertical_frames_2d_v1.png`, `data/stern_vertical_frames_v1.json`: gap 3 mm from our frame 1 aft face (X 35), three doubles of 8 mm: X 24-32 (46), 16-24 (47), 8-16 (48). Aft face of the aftmost at X 8.0: T3 forward end (8.3-9.5) fits within 0.3-1.5 mm; T1 (-4.7) and T2 (1.2-2.4) would be extended to X 8.0. Frame outlines not built yet (plan: interpolate outer curves between the v10 half frames H2 X 10, H1 X 22 and frame 1).
- Builder: the example model has gaps between the frames: use the same layout as the rest (double 8 mm, gap 3 mm, pitch 11) to see whether it is 2 or 3 added frames after 45. 2D `qa/stern_vertical_frames_2d_v2.png`, `data/stern_vertical_frames_v2.json`: F46 X 24-32, F47 13-21, F48 2-10 (F49 -9..-1 optional). Current transom forward ends: T1 -4.7/-3.5, T2 1.2/2.4 (meets the aft face of F48 at X=2.0 within 0.2 mm), T3 8.3/9.5 (inside F48). Three frames fit T2 exactly; two frames would leave T2 11 mm short.

## Stern frames 46-48 v1 (py/stern_frames_v1.py)
- Double frames W=8 gap 3: F46 X24-32, F47 13-21, F48 2-10 (A=aft layer, F=fwd layer, 4 mm each, S/P). Templates H1/H2; outer Y and Z range interpolated quadratically in X through H2(12), H1(24), frame1(39).
- Transoms 2,3,wing cut to F48 aft face X=2.0; tenons (rib-shaped, 2.2 deep, 0.6 inset) fused to transoms, pockets (+0.1) cut in FRAME48_A. No clashes among new parts. Not checked: backbone clash, frames 1-45 refit, T1, opened in Rhino.
- Files: rhino/RoyalCaroline_stern_frames_v1.step, _meshes.3dm, qa/stern_frames_v1.png
- v1b: F48 outer clamped to stern outline (bowl knots + 48.8 above wing, 50% on F47); T2/T3 rebuilt as smooth lofts with the wing's plan arch dx=kp*(y^2-Yc0^2); no clashes.
- v2 (`py/stern_frames_v2.py`, replaces v1 frame outlines): frames 46-48 rebuilt from the hull lines, not from template scaling: per layer centre X the outer curve is a cubic interpolated spline (OCP) through ~8 points: rabbet foot (from WL I-V end points), Y at WL crossings (WL curves of `RoyalCaroline_hull_1to48_v9.3dm`, saved in `data/hull_lines_stern.npz`), Y at Z 58..121 from stations ST18/17/16 (X 0/14.6/36.8, quadratic in X), top from the station tops. Inner edge = offset 4.7 (template band width), clipped at Y 2.65 (backbone). My earlier clamp to 49 removed (frames now follow the stations: F48 outer reaches 51.5 at Z~80). Transoms as in v1b. Files `rhino/RoyalCaroline_stern_frames_v2*`, `qa/stern_frames_v2.png`. No clashes; not opened in Rhino.
- v3 (`py/stern_frames_v3.py`): F46 anchored to the builder-accepted F46 (v1) by a Z-dependent bias (`data/f46_anchor_bias.json`, <=1 mm above Z 56, faded out below 52) carried along the line-derived flow to F47 and F48. No clashes.
- v4 (`py/stern_frames_v4.py`): foot of the outer curve continues the slope of the next segment (concave end, no hook), stops at the backbone face Y 2.65 (F48 foot Z about 51, as station 18 starts at 49.6). No clashes.
- Reference file for the builder: `rhino/RoyalCaroline_bodyplan_with_frames46_48_REF.3dm` + `rhino/bodyplan_A1-2_aft.png` (keep side by side): body plan picture on the YZ plane at X=-1 (scale 0.0833 mm/px from WL I-VI), v4 frame outer/inner curves (S and P), their points, stations 16-18. Script `py/bodyplan_ref_3dm.py`. Not opened in Rhino.
- v5 (`py/stern_frames_v5.py`): frames 46-48 now follow the builder's curves from `01e6a4d8-55.dxf` (`data/builder_frame_curves_v1.json`: three outer splines F46/F47/F48 by foot height 24.9/35.5/43.9, plus closed station-16-like and station-18-like outlines and the backbone line Y 3.2, all in the YZ plane). Each layer = builder curve (10 arc-length nodes, cubic spline) + hull-flow offset between the layer X and the frame centre X (28/17/6). Mean offset from his curve 0.8-1.4 mm per layer (the 2 mm layer shift). Inner edge offset 4.7. No clashes. Note: his curves sit 1-2.6 mm inside the v4 curves at Z 50-60.
- Stern assembly v3 (`py/stern_assembly_v3.py`): backbone aft part X<=80 (builder profiles, 5.3 mm sided; cut where transoms/wing overlap the post, <=5.7 mm3 each), rudder, 6 counter timbers, transoms 2/3 + wing (arched, cut to F48 face X=2, tenons), frames 46-48 v5. 32 valid solids, no clashes. Files `rhino/RoyalCaroline_stern_assembly_v3.3dm/.step`, `qa/stern_assembly_v3.png`. Transom 1 not built; frames 1-45 and sanding marks not included. Not opened in Rhino.
- v6 frames + assembly v4 (`py/stern_frames_v6.py`, `py/stern_assembly_v4.py`): frame feet were in the air; the builder says each frame is one part entering the gap between the keel/deadwood (lower mass) and the keelson (upper strip) and overlapping the lower mass. Now, when the foot is above the deadwood top at its X (F46, F47), the outer curve continues down along its own tangent to 1 mm below the deadwood top (reaches Y 0..1), the half frames meet at Y=0 through the gap (clipped under the keelson bottom - 0.3), and the backbone is cut (mortise) by the frames (1-4 mm3 per layer). F48 stays beside the post (foot Z 44 is inside the post mass at X 4-8). Gap = backbone profile of `data/step44_profiles.json` (deadwood top/keelson bottom per X). No clashes. `qa/frames_feet_vs_backbone_v6.png`.
- v7 frames + assembly v5: F46/F47 now have a floor like frames 1-45 (`py/stern_frames_v7.py`): flat 5.4 mm base seated 1.76 mm (seat depth) into the keel/deadwood top, flat top across the centre under the keelson (capped at keelson bottom -0.3), thickness profile of frame 1's floor carried along the hull flow (blend over Y 2.7-9 into the hull curve), fused with the rib band; backbone mortised by the floors. F48 sits against the post (post mass reaches Z 53 at X 4), no floor. `qa/frames_floor_sections_v7.png`, `py/frames_sections_qa.py`. Open: the "ח" saddle shape (floor straddling the keel) is my reading of frames 1-45; F48 treatment to confirm.
- v8 frames + assembly v6 (`py/stern_frames_v8.py`): the lower end of the hull curve of F46/F47 now runs tangent into the keel wall (Y 2.65, vertical tangent, continuous line) down to 1.76 mm below the deadwood top; flat floor base inside the keel seat; upper floor surface capped under the keelson with a smooth 1.5 slope (no step). 32 valid solids, no clashes. `qa/frames_floor_sections_v8.png`.
- v10 frames + assembly v8 (`py/stern_frames_v10.py`, `py/stern_assembly_v8.py`, 2D logic in `py/connection_reading.py`, `py/connection_chain.py`): built from the approved 2D: outer hull curve tangent into the keel/post wall (vertical, F48 down to Z 37), concave top lines (slope never decreases, F46 top from the keelson at 45.5, F47 52.7, F48 61.5; each a copy of F46's thickness profile scaled to its keelson, fading into the rib offset at Y~45), keelson notch (frame passes under the keelson at its bottom level), seat 1.76 into the keel/deadwood top (OVER). Both layers of a frame share the centre profile. One solid per layer per side, no unions. F48 has an "ear" near Y 40-45 (top climbs into the rib offset). `qa/frames_sections_v10.png`.

## סיכום סשן 16.10.2026
ראה `docs/SESSION_2026-10-16_stern_frames.md` (מה נבנה, לקחים, בעיות פתוחות) ו-`docs/NEXT_PROMPT.md` (פרומפט המשך).
- v11 frames + assembly v9 (`py/stern_frames_v11.py`, `py/stern_assembly_v9.py`, QA `py/layers_envelope_qa.py`): each layer is now a block between its two exact faces (X=x0 and x0+4): outer = outermost of the two hull-flow outer lines, inner/top = the more inboard of the two; shift of each face vs the frame centre = smoothed hull-flow delta along Z (gaussian 8 mm), tapered to 0 at the keel wall. Sanding allowance = the wood between the block and each exact face line: max on the outer line F46 3.2/3.0, F47 5.0/3.6, F48 3.7/4.0 mm (aft/fwd layer). The "exact inner line" is an interpolation (offset 4.7 / chained top lines), not a plan line. No reference hull surface exists yet (only 3 stations aft: X 0, 14.6, 36.8). `qa/frames_layers_envelope_v11.png`. F48 "ear" at Y 35-42 still there.
- 2D cutting plan for builder frames 1-5 (our 45..41): `py/cutting_plan.py` -> `qa/cutting_plan_frames_b1-5.png`, `rhino/cutting_plan_frames_b1-5.dxf` (layers F<b>_A / F<b>_F). Method: faces X-4/X/X+4 per frame; outer line of a face = interpolation (equal Z) between the neighbouring frames' plan outlines; inner = parallel at the true in-plane offset (normal thickness 3.2); layer block = union of its two face bands; pieces cut at the old joints (perpendicular cuts): layer A floor 1 (V across the keel) / fut2 2,7 / top 3,6; layer F fut1 8,13 / fut3 9,12 / top 10,11 (like the frame-21 sheet). Not included: deck clamps, scarf/lap details, topU pieces, nesting optimisation. Extend to all 45 by changing `frames=` in the script.
- Builder frame 5 (our 41) precise 2D (`py/frame5_precise.py` -> `qa/frame5_precise_2d.png`): outer line of each face from the hull lines (foot where the hull reaches the keel wall, WL I-V crossings, stations 3/2 interpolated in X for Z 56-104, old plan outline above, spline through 15 points), tangent merge into the keel wall (leg bottom = keel top - 2.5), inner line = true-offset parallel (3.2 normal), inverted-U lap at the keelson (keelson bottom + 2.5, shoulders concave into the inner line), double sanding lines (faces X-4,X for layer A, X,X+4 for F), keel/keelson from the builder profiles at the layer centre (keel top 7.16, keelson 15.88). Hull data saved: `data/hull_stations_all.npz`, `data/hull_waterlines_all.npz`. Not yet: piece joints in this sheet, frames 1-45.
- Frames on keel and keelson, 2D, builder frames 1-10 (our 45..36): `py/frames_on_keel_2d.py` -> `qa/frames_on_keel_2d_b1-10.png` (same method as frame 5 precise; generalised: keel top / keelson bottom from the builder profiles at each layer's centre X, legs bottom = keel top - 2.5, keelson legs top = keelson bottom + 2.5, true-offset inner line 3.2, double face lines, stations extrapolated beyond the last one). Frames 3-10 look consistent. Frames 1-2 (bow): layers A and F are displaced ~5 mm outward/inward from each other (the face lines use different point sets near the bow where the WLs change fast): needs a bow treatment. Frame 10 keel top 2.55 / keelson 8.5 (gap 6). Note `outer_line` in `cutting_plan.py` now merges multipolygons.

## 2026-10-17 views reference
- `py/build_views_3dm.py` -> `rhino/RoyalCaroline_views_ref.zip` (3dm + 4 PNG textures, keep beside): body plan (X=-80, aft A1/2 + fwd A1/3), elevation (Y=0, plan_1a: X=0.08511px-357.14, Z=(2110-row)*0.085), half-breadth plan (Z=0, plan_1b: X=0.08499px-361.43, Y=(1238-row)*0.0833). Check: `qa/views_ref_check.png`. Finding: WL data in lines.dxf deviate from the A1/4 drawing near the bow (up to ~25 mm in X, stations 1-4); Y scale of plan view fitted only to ~±1.5 mm.

- 2026-11-06 `py/bodyplan_st01_points.py`: ST01 on A1/3, points every 20 mm of arc on the ink centre (7 points) -> `qa/bodyplan_st01_points.png`, `data/st01_points_20mm.csv`. Awaiting builder approval.

- 2026-11-06 `py/bodyplan_points_all.py`: points on all 18 body-plan stations (10 mm arc, ink centre, straight top corner on ST01-03, ST06 kept inside ST07) -> `data/bodyplan_points_v1.json`, `qa/bodyplan_points_fwd.png`, `qa/bodyplan_points_aft.png`. Awaiting approval.

- 2026-11-06 `py/bodyplan_points_v2.py`: keel-contact points ST13-17, coloured splines through points (ST07-09 held back for a separate round) -> `data/bodyplan_points_v2.json`, `qa/bodyplan_lines_fwd.png`, `qa/bodyplan_lines_aft.png`. Problem stations: 10,11,12,14,15 upper part (mis-snapped to neighbours).

- 2026-11-06 approved by builder: ST01-06, 13, 16-18 -> `data/bodyplan_points_approved.json` (ST01 csv, ST02 json, rest from v2). Pending: 10,11,12,14,15 (upper part mis-snapped), 7-9 separate round.

- 2026-11-06 aft upper part ST10-15: `py/bodyplan_aft_upper*.py` (stations identified by order counted from the right, clean rows only; validated vs approved ST16-18: mean 0.05 mm) -> `data/bodyplan_aft_upper_v1.json`, `qa/bodyplan_aft_10-15_points.png`. Awaiting approval. Root cause of earlier failures: builder splines sit ~2 mm outside the ink at Z 55-100, lines only 1-2 mm apart => nearest-ink snapping picks the neighbour.

- 2026-11-06 aft right side restarted by builder: approved ST13 (v4), ST14 (v2), ST15 (v2) -> `data/bodyplan_points_approved.json`; ST16-18 earlier ones need re-approval; next ST12, 11, 10, then 7-9.

- 2026-11-06 approved ST12 (v2) -> approved json; ST11 points sent for approval (`data/st11_points.json`).

- 2026-11-06 approved ST11 (v2); ST10 points sent for approval (`data/st10_points.json`); next ST7-9 round.

- 2026-11-06 approved ST10 (v3 + convergence point F=(1.0,-0.3)); ST09 points sent (`data/st09_points_v2.json`), top ends at row 891 (above it only the handwritten 9 arrow).

- 2026-11-06 approved ST09 (v2); ST08 points sent (`data/st08_points.json`): builder spline for ST08 sits ~2 mm inside the ink, points taken as the ink line just outside ST09.

- 2026-11-06 approved ST08; ST07 points sent (`data/st07_points.json`) from the forward plan: clean rows = 2nd line from the right; merged band 7+8 = left part; foot points = builder spline.

- 2026-11-06 approved ST06 (v2) and ST07 (v2) -> approved json; ST16 points sent (`data/st16_points.json`); next ST17, 18 then global check.

- 2026-11-06 approved ST16 (v2, top moved up 0.4 mm); ST17 points sent (`data/st17_points.json`).

- 2026-11-06 approved ST17 (v2); ST18 points sent (`data/st18_points_v2.json`). After ST18: re-check 1-5 foot points, add F to stations ending at the foot, then spline-through-points for all and compare with builder splines.

- 2026-11-06 approved ST18; all 18 stations approved. Convergence points: F_aft (1.0,-0.3), F_fwd (3.27,-0.43) in `data/bodyplan_F_points.json` (proposed: append to stations 8-12 aft / 4-8 fwd).

- 2026-11-06 all 18 stations approved; F points approved (F_aft, F_fwd, shared 2nd point G of 6/7/8). `py/bodyplan_splines_final.py` -> `data/bodyplan_splines_v1.json`, `qa/bodyplan_final_{clean,fwd,aft}.png`. IMPORTANT calibration finding: aft plan (A1/2) Y scale was 3.1 % too small (stations 8-18 sat 2.3 mm inside the builder splines and inside forward stations 1-7); Y of stations 8-18 multiplied by 1.0325 (pixel positions unchanged). After: aft mean distance to builder splines 0.15-0.3 mm.

- 2026-11-06 stations 8-12 now all end at F_aft (old foot points Y~2.7 dropped, ST8 start = F_aft); foot smooth. Awaiting final approval of the body plan splines.

- 2026-11-06 station 8 redone on the forward plan as the outermost stroke (`data/st08_points_fwd.json`, band right edge - 2 px); previous 8 (from aft plan) sat inside 7 by up to 2 mm at Z<35. 8 starts at F_aft per builder (8-12 share the point).

- 2026-11-06 waterlines phase started: top view WL I traced (`py/line_follow.py`), 27 points every 20 mm -> `data/wl1_top_points.json`, `qa/wl1_top_*.png`. Y scale of plan A1/4 NOT yet calibrated (tentative 0.0833; body plan vs plan inconsistent by 1-3 mm); side-view line pending builder choice.

- 2026-11-06 WL I (top) approved. Side view line D = the long strip (rectangle) above the hull in A1/1; points on its top and bottom edges every 20 mm incl. corners -> `data/sideD_points.json`, `qa/sideD_points.png` (for approval).

- 2026-11-06 side line D approved. WL II-VII top view traced (`py/wl_top_all.py`): Y scale of plan A1/4 calibrated on 87 crossings with the approved body plan: Y=(1227.4-row)*0.08186 (resid std 1.0 mm); WL I re-expressed with it (midship Y 52.2->50.5). Points every 20 mm -> `data/wl_top_points_all.json`, image `qa/wl_top_all_points.png` (awaiting approval).

- 2026-11-06 WL I-VII top approved. Side-view hull lines: tracer found C/A (continuous port line) and the E bundle (4 lines, called E1-E4 top to bottom); points every 20 mm -> `data/side_lines_points_v1.json`, `qa/side_lines_*.png` (ends need confirmation). Other side lines not done yet: upper rail lines, dashed lines, B, F.

- 2026-11-06 `rhino/RoyalCaroline_lines_v2.3dm` (py/lines_v2_3dm.py, check: py/lines_v2_check.py, qa/lines_v2_check.png): GRID+LABELS of the original lines file, NEW approved stations (+Y, mirror, flat at X=-80), NEW waterlines I-VII (+Y, mirror), approved points layers (hidden), backbone solids for reference. No old body plan / waterline lines used. WL VI fixed near the stern (labels broke the column method: bump at X~72). WL vs station crossing mismatch: std 1.5 mm, 54% within 1 mm, max 4.6 mm (plan A1/4 vs body plan inconsistency).

- 2026-11-06 builder rule: the body plan decides; plan/WL mismatches are closed by ADDING a waterline, never by changing body plan lines. Central frame (builder 23 = our 23, X=284.46) planned on the NEW lofted body plan with keel/keelson laps: `py/hull_new_sections.py`, `py/frame_central_2d.py`, `qa/frame23_central_2d.png`. Keel top Z=2.38, keelson bottom 7.25 / top 12.25 at that X (step44_profiles).

- 2026-11-06 plan_6 B3 (central hull section) read: keelson bottom row 2287, top 2212 (5.9 mm), keel top row 2325 -> gap 3.0 mm (scale 0.0791 mm/px from keel width 5.3 mm). Inner/outer edge of frame band: `py/b3_inner_line.py`, `data/b3_inner_line.json`, `qa/b3_inner_line.png` (for approval). Our frame 23 at X=284 used gap 4.9 / keelson 5.0 from step44 profile.

- 2026-11-06 B3 is at X~270.9 (line 9). Frame our 22 (builder 24, X=273.9) redone with B3 gap 3.0 / keelson 5.9: `python3 py/frame_central_2d.py 22 3.0 5.9` -> `qa/frame24_central_2d_B3.png`. Floor top of my frame (~7.9) is ~2 mm above the B3 inner line (~5.9).

- 2026-11-06 frame 24 (our 22) corrected per B3: `PEN_UP=0.6 python3 py/frame_central_2d.py 22 3.0 5.9` (leg tops = keelson bottom+0.6, floor top Z 6.0 at the keel). Matches B3 inner line within 0.1-0.5 mm to Y=10, 0.9 at Y=18, 1.4-1.8 at Y 26-34 (my hull outer sits ~1.5 mm above the B3 drawing there).

- 2026-11-06 frames in batches of 5 (2D, for approval): `python3 py/frames_batch_2d.py 1 2 3 4 5` (builder numbering) -> `qa/frames5_b1-5.png`, `data/frames5_b1-5.json`. Rules: new body plan loft, step44 keel/keelson levels, leg tops keelson bottom+0.6 (B3). Frames 1-2: layers A/F displaced (X beyond station 1 at 527.8 clamped; steep bow). Next: builder 6-10.

- 2026-11-06 builder: each face plane must take keel/keelson levels at its OWN X (they rise to the bow). `py/frame_one_faces.py 1` -> `qa/frame1_faces_2d.png`. Frame 1 (X=524): face X-4 keelson bottom 29.60, face X 33.03 (step in the keelson profile), face X+4=528.03 lies in the stem where keel+keelson are one solid (stem starts X=526.6) -> asked builder how frame 1 ends there. frames_batch_2d.py now uses per-face levels too.

- 2026-11-06 frame 1 side view (X-Z) with the keel/keelson channel: `py/frame1_side.py` -> `qa/frame1_side_view.png`. The channel between keel and keelson is stepped (steps at X~511, 516, 521.5, 524) and closes into the stem at 526.6.

- 2026-11-06 channel views `py/channel_views.py` -> `qa/channel_views.png`: keel-top/keelson-bottom steps at X=443,455,465.5,477.5,488.5,499.5,510.5,521.5 (pitch ~11 mm) vs frame bands (builder N: 1=520-528, 2=509.5-517.5, 3=498.2-506.2, 4=487.3-495.3, 5=476.3-484.3): steps lie 1-1.5 mm inside the bands, plateaus 11 mm vs band 8 mm. Proposal (not done, backbone is approved): set each opening exactly X-4..X+4. Waiting for builder answer.

- 2026-11-06 builder approved adapting keel/keelson openings to frames (outer lines untouched). `py/channel_adapt.py` -> `data/channel_seats_v1.json` (45 seats: X-4..X+4, keel top / keelson bottom at the frame centre level; between frames previous level, step exactly at X-4 of the next), `qa/channel_adapt.png`. Backbone 3dm solids NOT yet modified (waiting for approval of the picture).

- 2026-11-06 builder: wants a FULL pocket for every frame (keelson inner line walls on both sides). `python3 py/channel_adapt_v2.py 1.5` -> `data/channel_seats_v2.json`, `qa/channel_adapt_v2.png`: in the gaps between frames the keelson inner line sits W=1.5 mm below the seat ceiling. 3dm not modified yet.

- 2026-11-06 keelson inner line as a spline between pockets: `py/keelson_spline.py 1.5` -> `data/keelson_inner_spline_v1.json`, `qa/keelson_spline.png`. Original shape lowered by a smooth d(x) (3.1 mm at frame 2, ~1 mm at midships), wall >= 1.5 mm at the bow side of every pocket; clearance to keel top >= 1.3 mm. Pocket ceiling = old level at frame centre. 3dm not modified.

- 2026-11-06 builder: wall 1 mm is enough. `py/keel_keelson_final_2d.py 1.0` -> `data/keel_keelson_final_v1.json`, `qa/keel_keelson_final_2d.png` (2D for approval before 3D): keelson inner line lowered 0.1-2.6 mm, keel top raised 0.6-1.8 mm (splines), full pockets both sides at all 45 frames; min clearance keel-keelson outside pockets 0.92 mm at frame 2, others >= 2.1 mm.

- 2026-11-06 keelson from the builder STEP (solid 15, 269-vertex outline): top line smooth spline, bottom = smooth ramp spline (120 vertices, residual 0.06 mm) + 43 plateau pockets ~5 mm wide centred on the frames; `py/keelson_from_step.py 1.0 1.0` -> `data/keelson_from_step_v1.json`, `qa/keelson_from_step.png`. New line = ramp spline 1.0 mm lower; pockets keep his plateaus, raised <=0.63 mm in 3 frames for 1 mm walls.

- 2026-11-06 clean 2D keel+keelson from the STEP: `py/keel_keelson_clean_2d.py 1.0 1.0` (py/step_chain.py reads the STEP solids 15=keelson, 16=deadwood rising) -> `data/keel_keelson_clean_v1.json`, `qa/keel_keelson_clean_2d.png`. Reference splines = ramp vertices, keelson line 1.0 mm lower, keel line 0.88 mm higher (constant), 8 mm pockets centred on frames, walls >= 1 mm both sides, pocket height 4.4-9.3. Line gap outside pockets >= 0.9 mm (frames 15-28), frame 1: lines cross (stem merge at 526.6). Waiting for approval before 3D.

- 2026-11-06 bow junction fixed: keel and keelson lines meet at the stem start (X=526.6), gap tapers to 0 over 12 mm, never negative (`py/keel_keelson_clean_2d.py`). Frames 1-5 in 2D on the new pockets: `python3 py/frames_on_pockets_2d.py 1 2 3 4 5` -> `qa/frames_pockets_b1-5.png`, `data/frames_pockets_b1-5.json`. Pocket floor/ceiling identical for layers A and F. Next: builder 6-10 after approval.

- 2026-11-06 3D build+render (bow, frames 1-12 + keel/keelson with the new pockets): py/build3d_parts.py, py/build3d_hull.py, py/render3d.py (three.js in headless chromium, node script in /tmp), renders qa/render3d/v1-v4, mesh file rhino/RoyalCaroline_bow_frames1-12_keel_keelson_v1.3dm (meshes, not solids; not opened in Rhino). Frame 1 pocket (520-528) extends past the stem start 526.6 -> open window at the right end of the keel.

- 2026-11-06 builder: keelson = one smooth spline, no pockets; keel has 2 mm pockets with two parallel splines; frame is CUT with allowance = difference between the spline levels at the layer faces (innermost min .. outermost max) and sanded to the final surface (laser mark = final line). `py/frame_allowance_2d.py 5 23` -> `qa/frame_allowance_5_23.png`: frame 5 allowance ~0.9-1.05 mm per layer, frame 23 ~0 (flat midships). 2D only, for approval.

- 2026-11-06 NEW KEEL/KEELSON 2D (builder rules): keelson = smooth STEP spline, no pockets, frame top has no step/pocket (NOSTEP=1 option in frames_batch_2d.py); keel = surface spline + 2 mm pockets normal to the spline, floor spline parallel; 43 pockets 8 mm. `py/keel_keelson_v2_2d.py` -> `data/keel_keelson_v2.json`, `qa/keel_keelson_v2_2d.png`. Gap keelson-keel surface 2.8 mm midships. Next: frames 1-5 on it, 5 per round.

- 2026-11-06 pocket depth set to 1.0 mm (measured in the STEP: keelson steps mean 0.91, deadwood 1.11, backbone.py NOTCH=1.0; ~2 mm only at the bow). `py/keel_keelson_v2_2d.py` DEPTH=1.0 -> qa/keel_keelson_v2_2d.png.

- 2026-11-06 frames 1-5 on the new keel/keelson (NOSTEP=1, pocket 1 mm): `NOSTEP=1 python3 py/frame_allowance_2d.py 1 2 3 4 5` -> `qa/frame_allowance_1_2_3_4_5.png`. Allowance per layer: keelson seat 0.9-2.4 mm, keel pocket floor 0.9-3.2 mm (largest at frame 1). Levels for faces beyond X=526 read at 526. Next: 6-10.

- 2026-11-06 ALL 45 frames 2D on the new keel/keelson (NOSTEP, pocket 1 mm, inner line smoothed): py/frames_all_2d.py -> qa/frame_allowance_*.png (9 sheets). 3D: py/build3d_v2.py (frames 1-45 + keel + keelson meshes) -> rhino/RoyalCaroline_frames1-45_keel_keelson_v2.3dm, renders qa/render3d/n1-n5. Allowance max 2.35 mm keelson / 3.23 keel (frame 1), 37 of 90 layers < 0.1 mm both. Frames 44-45 and the stern end: keel/keelson built from X=45.

- 2026-11-06 builder wants frames BEFORE sanding: flat-cut blanks (straight 4 mm prisms covering both faces, one horizontal floor / seat line at the keel and keelson, extra wood both sides) with red laser lines = the final face outlines. `py/build3d_blanks.py 1 2 3 4 5`, `py/render3d_blanks.py` -> qa/render3d/b1-b4. Builder frames 1-5 only (5 per round).

- 2026-11-06 blanks v2: A and F share ONE common cut outline (envelope of the faces X-4, X, X+4: inner minimum .. outer maximum, one horizontal tab floor), glued first, sanded after; laser marks on the back (X-4), middle (X) and front (X+4) final outlines. py/build3d_blanks.py 1 2 3 4 5. Excess area vs final face 55-100 percent at the bow because the hull flares across the 8 mm.

- 2026-11-06 frame 5 blank: across the backbone width (+-2.65) two straight horizontal lines: floor on the keel (pocket floor = keel surface - 1 mm) and seat under the keelson (keelson spline level); no legs/steps (NOSTEP branch in frames_batch_2d.py, flat tab in build3d_blanks.py). qa/render3d/d1-d3. Other frames still to be regenerated with this rule.

- 2026-11-06 frames 1-5 blanks with the straight horizontal floor/seat rule: py/build3d_blanks.py 1 2 3 4 5 (+ py/render3d_blanks.py) -> qa/render3d/e1-e4. Blank excess vs final face: frame 1 x2.5, 2 x2.1, 3 x1.8, 4 x1.7, 5 x1.6 (hull flare over 8 mm).

- 2026-11-06 sharp connections (no radii, non-tangent): face_poly_sharp in frames_batch_2d.py (SHARP=1 with NOSTEP): floor horizontal +-KB -> straight to the exact hull line start; seat horizontal -> straight out to where it meets the inner line. Frames 1-5 blanks regenerated, qa/render3d/e1-e4.

- 2026-11-06 builder: do not invent lines; body plan lines are exact. Frame 5 in 2D with only: exact hull line, inner offset, horizontal floor/seat lines extended until they meet the exact lines (no chords, no radii): py/frame_one_2d.py 5 -> qa/frame5_one_2d.png. Waiting for approval.

- 2026-11-06 builder answers: outer (iron) hull line stops at the keel wall (vertical wall); only ONE horizontal line = keel pocket floor, backbone width; inner line deviates slightly inward and meets its end. Frame 5 2D: `python3 py/frame_one_2d.py 5` -> qa/frame5_one_2d.png. Not yet propagated to frames_batch_2d.py / 3D blanks.

- 2026-11-06 side view of keel with pockets and the frame-5 arm end face: py/keel_side_frame.py 5 -> qa/keel_side_frame5.png (pocket 1.0 mm; arm end face 3.2-3.7 mm below the floor, covers the keel side wall). py/frame_arm.py = arm function.

- 2026-11-06 builder: raise the inner horizontal line by 2 mm (no thin neck at the keel wall) and let the inner line leave the 3.2 offset to meet it. frame_arm.py RAISE=2.0. Frame 5: inner horizontal 8.79/9.70/10.75, wall 5.2-5.7 mm, inner line moves 2.5-3.1 mm. qa/frame5_one_2d.png, qa/keel_side_frame5.png.

- 2026-11-06 builder: the gap between keel and keelson must be FILLED at the frame centre; upper line meets the keelson bottom line. frame_arm.py now builds floor+seat+wall; connection of the seat end to the natural inner line unresolved: variants A/B/C in qa/frame5_variants.png (py/frame_variants.py). Waiting.

- 2026-11-06 inner line continuation per builder sketch: Hermite spline from the seat-line end (KB, seat) to the exact offset line, tangent to it at the join (G1), corner at the horizontal line. frame_arm.py. Frame 5: qa/frame5_one_2d.png. Waiting for approval before 1-5.

- 2026-11-06 join point of the inner-line spline moved outward (JOIN=18 mm from the wall) for a longer, more continuous transition. frame_arm.py, qa/frame5_one_2d.png.

- 2026-11-06 frames 1-5 in 2D by the final arm rule: py/frames_arm_batch_2d.py 1 2 3 4 5 -> qa/frames_arm_1_2_3_4_5.png, data/frames_arm_1_2_3_4_5.json. Wall 3.2-6.1 mm, gap filled 3.0-7.6 mm. Frame 1 face X+4 levels read at X=526.

- 2026-11-06 frames 6-10 in 2D (arm rule): qa/frames_arm_6_7_8_9_10.png. Wall 3.0-3.6, gap filled 4.9-7.6. Next 11-15.

- 2026-11-06 builder (plan_6 B2): inner line must be one continuous flowing curve departing GRADUALLY from the iron outer line, no break. frame_arm.py: cubic Hermite in y from the seat corner (slope capped) to the exact offset line, tangent join at JOIN=50 mm; also fixed: do not sort the hull line by Z (broke flat midship frames). qa/frames_arm_5_10_23.png. Frames 1-10 need re-run with this.

- 2026-11-06 builder: inner line must never be convex, keep concavity; right-hand (X+4) join point farther out. frame_arm.py: monotone non-decreasing cubic (Fritsch-Carlson, never below the seat) from the seat corner to a tangent join on the exact offset line, join moved out in 10 mm steps until concave; z_nat from the lower branch only. qa/frames_arm_5_23_30.png. Midship frames get a flat shelf (inner line = seat level out to y~40) because the offset line there dips below the seat; needs builder judgement.

- 2026-11-06 measurement check vs plan_6 B3 (central section, station 9, X=270.9): outer hull surface relative to keel top is 0.4-0.7 mm HIGHER in the drawing than in our model (keel top row 2321-2325, n=25, std 0.45; B3 scale 0.0791 mm/px). Matches the builder impression (raise frames 0.5-0.75 vs keel). Not yet applied; since hull lines are iron, applying = lowering keel and keelson splines by ~0.6 mm (or shifting floor/seat up). Waiting for his decision.

- 2026-11-06 builder: take the whole backbone as is and lower it 0.6 mm vs the body plan. qa/backbone_shift_view.png: lower line of the backbone before/after over the original sheer plan + body plan at the keel. Finding: the drawing keel bottom line is at Z~-9.08 (std 0.17, -9.4 at the stern to -8.8 at the bow); backbone before -9.37; after the shift -9.97, i.e. 0.9 mm below the drawing line. Not applied to the data files yet.

- 2026-11-06 side view: whole existing backbone (not moved) over the original sheer plan + lower end of all 45 frames (outer line at the keel wall .. pocket floor) at X-4,X,X+4: py/frames_bottom_side.py -> qa/frames_bottom_side.png, data/frames_bottom_side.json. Lowest frame point Z=-0.93 (frame 10); midships ~-0.3, frame 5 4.28, frame 1 22.71. The frame bottoms follow the baseline Z~0 drawing line (the hull line at the keel), i.e. they sit ~2.4 mm above the keel top... keel top midships 3.4.

- 2026-11-06 builder: frames are too low vs the keel -> raise all by 0.6 (SHIFT=0.6 in frame_arm.py; backbone drawn 0.6 lower). qa/frames_bottom_side_shift.png. docs/NEXT_PROMPT.md rewritten for a new conversation.

- 2026-11-06 frames 1-5 re-run by the final arm rule with SHIFT=0.6 (frames raised vs keel): `python3 py/frames_arm_batch_2d.py 1 2 3 4 5` (needs shapely, scipy, cadquery-ocp; mkdir -p /tmp/claude-0/x for the loft cache) -> qa/frames_arm_1_2_3_4_5.png, data/frames_arm_1_2_3_4_5.json. Wall 2.6-5.5, gap filled 3.0-7.6. Frame 1 face X+4 (red) is distorted on the right (beyond stem start 526.6). Awaiting builder check of the middle (seat/inner line by the keelson).

- 2026-11-06 builder: frames overshoot the RABBET line (upper of the double black line on the sheer plan) in side view. `py/rabbet_points.py` -> 15 reference points (point 15 fixed to 28.8 at X=528) + spline (`data/rabbet_points_v1.json`, `qa/rabbet_points_v1.png`, for approval), residual vs ink <=0.1 mm (0.36 at X=525). Overshoot of frame bottoms (unshifted, outer line at keel wall) below the rabbet: midships 0.5-0.9 mm, frames 10-11 1.3-1.4, frames 1-2 2.4-2.6. Frames 36-45 (stern) lie above it. Frames NOT yet trimmed; waiting for approval of the points.

- 2026-11-06 body plan of the front frames 1-5 with the exact outer line ending at the rabbet spline at each face X: `python3 py/frames_rabbet_bodyplan_2d.py 1 2 3 4 5` -> qa/frames_rabbet_bodyplan_1_2_3_4_5.png, data/frames_rabbet_bodyplan_1_2_3_4_5.json (unshifted; cut Y 3.6-5.4, cut-off length vs wall 0.6-2.9 mm). Waiting for approval; stern frames skipped by the builder.

- 2026-11-06 builder clarified: body plan OF THE PLANS (approved station lines, forward stations 1-8), not the frames. `py/bodyplan_rabbet_2d.py` -> qa/bodyplan_rabbet_1_8.png: station line ends vs rabbet Z at station X: 1 -1.25, 2 -0.24, 3 -0.02, 4 -1.00, 5 -0.34, 6 -0.75, 7 -0.74, 8 -0.56 (mm, negative = line ends below the rabbet). Not changed, waiting.

- 2026-11-06 builder: end point of the station line moved HORIZONTALLY to the keel half-width (Y=2.65) at the rabbet Z, spline refit, original forward body plan (plan_1b) as background: `py/bodyplan_rabbet_v1.py` -> data/bodyplan_rabbet_v1.json, qa/bodyplan_rabbet_v1_full.png, qa/bodyplan_rabbet_v1_zoom.png (dashed = old, solid = new, green = new end). Finding: stations 1,2,4 leave the plan ink by ~1 mm near the end; curvature sign changes rose for 2, 5, 8 (1->3? 2:1->3, 5:2->3, 8:2->3). Not approved.

- 2026-11-06 builder: the rabbet-ended body plan experiment is dropped (approved data/bodyplan_splines_v1.json was never changed; bodyplan_rabbet_v1 outputs removed). Rule back to iron: body plan lines untouched. Check rabbet vs waterlines: rabbet spline reaches WL Z (8.7/17.4/26.1) at X 494.1/513.0/524.9 vs top-view WL bow ends 497.1/513.2/525.2 (diff 3.0/0.2/0.3 mm); on the sheer-plan ink the line III is at Z~26.9 (0.8 above the body-plan WL III 26.1).

- 2026-11-06 side view with backbone + rabbet + WL I-VII in colours (model Z from the body plan, bow end X from the top view) over the sheer plan: `py/side_backbone_wl.py` -> qa/side_backbone_wl.png. The WL Z (8.7/17.4/26.1/34.8/43.4) sit 0.4-0.9 mm below the sheer-plan ink lines (9.2/17.8/26.9/35.5/44.3).

- 2026-11-06 sheer plan (plan_1a) waterlines sampled every 3 mm (`py/sheer_wl_measure.py` -> data/sheer_wl_measure.json, qa/sheer_wl_measure.png): plan ink = body plan WL Z + 0.202 mm + 0.00135*(X-270) (tilt 0.68 mm over 500 mm), residuals I-V <=0.13 mm, VI -0.27, VII -0.14. So the plan image is slightly rotated; the rabbet spline (read on the same image) carries the same tilt: correct Z_model = Z_ink - 0.202 - 0.00135*(X-270) (-0.55 mm at the bow). Not applied to data yet.

- 2026-11-06 recalibration (builder: recalibrate the views, do not touch the planned data): sheer plan plan_1a affine X,Z from 213 station-vertical samples (resid 0.05 mm) and WL I-VII (resid <=0.2) -> data/plan_calibration_v2.json; `py/side_calibrated.py` warps the plan into model coords -> qa/side_calibrated.png; rabbet re-expressed -> data/rabbet_points_v2_calibrated.json (v1 untouched). Rabbet crosses WL I/II/III at X 495.8/514.0/525.6 vs top-view ends 497.1/513.2/525.2. Body plan fwd (plan_1b) horizontals: Z scale off by about -1.2% (resid 0.37), aft +0.05+0.0026*Y (resid 0.25): only measured, not applied. Top view not yet recalibrated.

- 2026-11-06 top view (plan_1b) X check: station verticals scatter -0.83..+0.87 mm vs frames_X list (stations 1,2 -0.45/-0.47; 7 +0.87; 9 -0.83; 15 -0.78), measured only, not applied. Side view with calibrated sheer plan + frame silhouettes before (red) / raised 0.6 (blue): `py/side_calibrated_frames.py` -> qa/side_calibrated_frames.png. Note: in data/frames_bottom_side_shift.json the SHIFT moves only floor/seat (+0.6); the outer line end at the keel wall (hk) is unchanged, so the frame lower end is NOT raised. WL I bow end (497.1, 8.7) lies 0.5 mm below the calibrated upper rabbet line (Z 9.19 at X 497.1; v1 9.75).

- 2026-11-06 why the frame silhouettes protrude below the calibrated upper rabbet: (1) the lower end hk in frame_arm/frames_bottom_side is the loft hull line EXTRAPOLATED (cubic, last 10 mm) from its own start (Y 3.2-4.6) to the keel wall Y=2.65: -0.5..-1.4 mm of invented length; (2) frames 1-2: the loft line itself starts 0.1-1.5 mm below the rabbet (frame 1 -1.0..-1.5, frame 2 -0.1..-1.2), frames 3-5 start 0.3-1.0 ABOVE it. Body plan station ends vs calibrated rabbet: -0.65,+0.32,+0.52,-0.49,+0.12,-0.34,-0.37,-0.24 (st 1-8). Also SHIFT=0.6 in frame_arm.py LOWERS the pocket floor/seat (backbone lowered) and leaves hk unchanged: the builder wants the FRAMES raised, not the keel lowered. Nothing changed yet.

- 2026-11-06 builder confirmed: remove the extrapolation to the keel wall (frame ends at its loft line own end) and raise the WHOLE frame 0.6 (keel not moved). Side view silhouettes of frames 1-8 only (py/side_frames_v2.py -> qa/side_frames_v2.png), frame_arm.py NOT yet changed. Lower end minus calibrated rabbet (faces X-4,X,X+4): f1 -0.8/-0.9/-0.4, f2 +0.5/-0.05/-0.6, f3 1.6/1.3/0.9, f4 1.7/1.8/1.7, f5 1.3/1.5/1.6, f6 0.8/1.0/1.1, f7 0.4/0.6/0.7, f8 0.2/0.2/0.3 (positive = above the rabbet). Without the 0.6: f3-f5 are 0.3-1.1 above.

- 2026-11-06 builder: line III ends exactly at the end of station 1 in the original body plan. Zoom of plan_1b (py/bodyplan_end_zoom.py -> qa/bodyplan_end_zoom.png): the ink of stations 1 and 2 continues ~1.4 mm past the approved FIRST points (st1 4.00/27.38, st2 3.83/13.22) in a short steeper hook to the keel wall (Y~2.65); st1 hook ends at the WL III row (nominal Z 26.1), st2 hook ends ~1 mm below its first point (Z~12.2), NOT on WL II. The approved point sets stop before this hook. Rough automatic follow (py/bodyplan_end_points.py -> data/bodyplan_ends_v1.json, qa/bodyplan_ends_v1.png) gives Z 25.2/11.6/2.3 for st 1-3 (corner overshoot, not reliable to 1 mm; st 8 wrong). Loft/frames end below the WL III dot because they use an extrapolated end, not this hook. Proposal: add a measured end point per station (1-3 especially) for approval.

- 2026-11-06 proposed END points of stations 1-8 (hook tips at the keel wall) read from gridded zooms of plan_1b: py/bodyplan_ends_propose.py -> data/bodyplan_ends_proposed_v1.json, qa/bodyplan_ends_proposed_v1.png: 1 (2.85,26.05) 2 (2.95,12.10) 3 (2.85,2.80) 4-8 (3.30,-0.55). For approval; body plan data untouched.

- 2026-11-06 builder approved the end points (station 2 raised 0.25 -> (2.95,12.35)). py/side_frames_v3.py: data/bodyplan_splines_v2_ends.json = old curves with the end point prepended (nothing else changed), loft rebuilt, frames 1-8 ends -> data/frames_ends_v3.json, qa/side_frames_v3.png (py/side_frames_v3_draw.py). Lower end minus calibrated upper rabbet, NOT raised: f3 -0.06/-0.28/-0.58, f4 +0.15/+0.14/+0.05, f5 +0.02/+0.06/+0.12, f6 -0.09/-0.05/-0.02, f7 -0.23/-0.17/-0.12, f8 -0.47/-0.38/-0.29 (so no 0.6 raise is needed for 3-8); f2 -0.87/-1.26/-1.68, f1 -1.93/-2.21/-2.29 (the loft between stations 1,2,3 does not follow the convex rabbet).

- 2026-11-06 why frame 1 ends below the green dot: the dot is the top-view WL III end at X=525.2; on the body plan/loft the station 1 end (527.8, Z 26.05) is ON line III, and frame 1 face X+4=528 ends at Z 25.95. WL II (Z 17.4) is reached by the loft ends at X~516.3 vs top-view dot 513.2. So the top-view WL ends sit 2.6-3.1 mm earlier in X than the body plan implies at the bow (III, II). Not changed.

- 2026-11-06 builder asked to try moving the WL bow ends (division runs away along X): py/side_wl_ends_moved.py -> qa/side_wl_ends_moved.png: I 497.1->495.6, II 513.2->516.3, III 525.2->527.8 (body plan loft ends), IV-VII not movable (above the loft ends). X spacing top view I..VII 16.1/12.0/9.3/6.7/6.2/7.6; moved I-II-III 20.7/11.5; calibrated rabbet crossings 495.8/514.0/525.6 (18.2/11.6). Not applied to data.

- 2026-11-06 builder: frames 1-4 must end on the UPPER rabbet. py/frames_on_rabbet_2d.py 1 2 3 4 -> qa/frames_on_rabbet_1_2_3_4.png, data/frames_on_rabbet_1_2_3_4.json (2D, for approval): exact loft hull line (stations with approved end points) trimmed at Z=calibrated rabbet(X) (frame 1 trims 1.9-2.3, frame 2 0.9-1.7, frame 3 0.06-0.6), frame 4 is 0.05-0.15 above and drops vertically; then a horizontal piece to Y=2.65 (frame 1: 2.3-3.1 mm, frame 2: 1.5-2.8, frame 3: 0-1.0). Frame 1-2 hull line meets the rabbet at Y 4.2-5.7, i.e. the end is farther from the keel (the earlier complaint).

- 2026-11-06 builder: frames-on-rabbet 2D (qa/frames_on_rabbet_1_2_3_4.png) rejected. Built rhino/RoyalCaroline_all_approved_lines_v1.3dm (py/lines_all_3dm.py, rhino3dm, 4.3 MB, not opened in Rhino): stations 1-18 +Y/-Y at their X (+ straight tops), approved end hooks 1-8 (data/bodyplan_ends_proposed_v1.json), WL I-VII +Y/-Y at Z, rabbet upper line calibrated (Y=0, data/rabbet_points_v2_calibrated.json), side line D (calibrated, Y=0), backbone solids (gray), approved points on hidden layers. Frames and solids built from lines are not included.

- 2026-11-06 builder: body plan file with the new lines + image of the plan. py/bodyplan_new_3dm.py -> rhino/RoyalCaroline_bodyplan_new_v1.3dm (2D at X=-80: aft 9-18 +Y, forward 1-8 -Y, approved splines unchanged + approved end hooks 1-8 as green lines, WL I-VII, centreline, keel half-width; not opened in Rhino), qa/bodyplan_new_fwd.png and qa/bodyplan_new_aft.png (lines over the original plans, end hooks in green).

- 2026-11-06 builder: keel half-width stays 2.65 (the "2 mm" assumed a 4 mm keel); try UPDATING THE RABBET LINE. py/rabbet_update.py -> data/rabbet_points_v3_ends.json: ink-based calibrated rabbet (v2) lowered by a smooth deficit (0 up to station 3, -0.55 at st 2, -1.98 at st 1) so it passes exactly through the approved station ends (st1 26.05, st2 12.35, st3 2.80); side view qa/side_rabbet_updated.png (py/side_rabbet_updated.py). Frame loft ends minus the updated rabbet: f1 -0.59/-0.54/-0.29, f2 -0.19/-0.37/-0.52, f3 +0.29/+0.16/-0.02, f4 +0.29/+0.35/+0.34. At the bow the updated rabbet lies ~2 mm below the sheer-plan upper ink line at station 1 (X 527.8). Not applied to frames or backbone.

- 2026-11-06 builder: 2D file before solids. py/keel_2d_new_rabbet.py -> rhino/RoyalCaroline_keel_side_2D_new_rabbet_v1.3dm (plane Y=0, X-Z; 85 objects: backbone profiles, NEW rabbet v3, rabbet v2 hidden, station ends 1-8, frames 1-8 outlines from loft ends to floor, 45 frame position ticks, WL I-VII hidden; not opened in Rhino) and qa/keel_side_2D_new_rabbet.png. Rabbet defined only X 30..527.8 (stern post and stem above Z 28 not traced); station ends 4-8 (-0.55) lie ~0.4-0.5 below the rabbet there.

- 2026-11-06 builder: trim frames to the NEW rabbet, then 3D for frames 1-8. py/frame_arm_v2.py (loft with approved station ends, lower end ON py rabbet v3, SHIFT=0, no raise; end inside keel width is cut at the wall) -> py/frames_arm_batch_2d_v2.py 1..8 -> qa/frames_arm_v2_1_2_3_4_5_6_7_8.png, data/frames_arm_v2_*.json (frames 7-8 inner line near the middle needs review: flat shelf / crosses between faces). 3D: py/build3d_frames_v3.py -> rhino/RoyalCaroline_frames1-8_blanks_v1.3dm (16 extrusions A/F 4 mm, laser lines on X-4/X/X+4, backbone reference, rabbet new) + .step; one common blank outline per frame (union of 3 faces, slivers filled: frame 1 blank 2846 mm2 vs faces 716-869, strong flare). Checks: prisms valid, volume = area*4, no frame-frame overlap; overlap with backbone STEP 24-86 mm3 per layer (STEP still has the old steps/pockets, new pockets not applied to the backbone). Preview qa/frames1-8_preview.png (wire, not a render). Not opened in Rhino.

- 2026-11-06 builder: frame 1 red lines ran away; inner lines should be CONCAVE only (except frame 2 which was fine). Causes/fixes: (1) frame 1 face X+4=528 lies beyond the stem start 526.6 (keel+keelson one solid): the loft collapses in its last 0.8 mm (Y@Z70 41.3 -> 29.4) and keelson/seat stay at 33.3 while the hull end is at 26.2, so the inner line crossed the outer. Now frame 1 ends at the stem start: face X+4 -> 526.6 (F layer 2.6 mm), faces >=527.0 would use the approved station 1 line. (2) frame_arm_v2.py inner line near the seat: cubic Hermite with guaranteed convexity (z-double-prime >= 0 at both ends: max(0,3m-2*s1) <= s0 <= (3m-s1)/2, needs m <= s1 <= 3m), smallest join distance; convex runs below the widest point: none left for frames 1-8. Remaining convex runs only in the upper S flare of the iron hull of frames 1-2 (Y 42-50, Z 86-106). Vector PDF: qa/frames_arm_v2_1-8.pdf (one page per frame). 3D rebuilt: rhino/RoyalCaroline_frames1-8_blanks_v1.3dm + _step.zip; frame 1 blank 1719 mm2, backbone overlap 24-82 mm3 per layer.

- 2026-11-06 builder: frames 2-8 APPROVED. Frame 1: back part fine, front part messed up; split into 4+4 and show separately before union. py/frame1_split_2d.py -> qa/frame1_part_A.png (faces 520/524, blank 1406 mm2), qa/frame1_part_F.png (524/528, front face = band butting the stem, blank 1398 mm2), qa/frame1_part_F2.png (524/526.6, front face keeps floor/seat, blank 1100 mm2), qa/frame1_parts_AF.pdf (vector, 3 pages). Reason: the bow flares so strongly that the hull line moves inward 4-6 mm (Y@Z50 31.8 at 524 vs 25.5 at station 1 527.8) over the 4 mm of X, i.e. the layer would need a ~55 deg bevel; at X>526.6 there is no gap/seat (stem). Waiting for the builder choice before union/3D.
