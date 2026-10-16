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
