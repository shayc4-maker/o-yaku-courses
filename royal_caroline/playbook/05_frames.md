# 05 Frames (double frames, final builder rule)

Geometry: builder frame b has centre X = XF[45-b] (data/frames_X.json); layers A (X-4..X) and F (X..X+4); faces at X-4 (back), X (mid), X+4 (front). 45 frames; frames 46-48 (stern) are separate.

## Inputs
- Approved outer lines per face: `data/frames_outer_approved_vN.json` (+Y master, -Y mirror): `curve` (500 points Y,Z), `top` (straight top segment), `end` (lower end). These are iron. The tops were extended to the bulwark lower line in v5 (never trimmed, 1-4.7 mm).
- Backbone: `data/keel_keelson_v2.json` (keelson spline, keel surface spline, pocket depth 1.0). The backbone is lowered 0.6 mm against the body plan (= frames raised 0.6 vs the keel) -> SHIFT=0.6.

## Rule (builder, final)
1. Outer (iron) line runs to the keel wall (Y=2.65, vertical wall up to the pocket floor). The approved lines start at the neck (Y=1.8): cut them at Y>=3.2 and let the code extend to the wall with a cubic fit.
2. Across the backbone width (+-2.65) ONE horizontal at the pocket floor (floor = keel top - 1.0 - 0.6) and ONE under the keelson (seat = keelson spline - 0.6). The frame fills the gap between floor and seat; at the stern the gap grows (3.9 mm midship, 25 mm at frame 45) and the base grows with it.
3. Inner line = ONE concave curve that never dips: monotone cubic from the seat corner, tangent join to the exact 3.2 mm offset line; the join is moved outward until the line is concave.
4. Blank = ONE common cut outline for A and F: envelope of the three face outlines (inner minimum, outer maximum), flat prism (straight cut), glued, then sanded by hand. Laser marks = the exact final faces at X-4, X, X+4 (offset +-0.03 so they are visible). No bevel cut: the builder does NOT want sloped cuts, only laser marks for hand sanding; the blank must contain enough material (check it).
5. Top: cut straight along the bulwark lower line: horizontal per face at Z_line(X_face), sloped across each layer (A from Z(X-4) to Z(X); F from Z(X) to Z(X+4)). Implemented by boolean common with an XZ slab.
6. Radial thickness 3.2 mm is measured in the section plane (true offset of the exact outer line).

## Implementation notes (scripts/frame_arm.py, frames_blank_batch.py, frames_blank_3d_batch.py)
- Feed the approved curve through `F.hull_line = hull_approved` (monkey-patch) instead of the old lofted hull line; append 6 and 8 mm straight extension at the top and clip back to the line.
- Offset loops: where the outer line bends tighter than T=3.2 mm the raw normal offset self-intersects (MultiPolygon after buffer(0), areas wrong by 5-80 %). Use `shapely LineString.offset_curve` (cleaned) — fixed in frame_arm.py.
- JOIN is `max(8, min(34, 8*D))`, D = seat - natural offset at the wall: with a small D the long default join made the inner line cross the outer line (frame 1 front).
- JMAX env (default 120; use 40) limits how far out the join may move: without it V-shaped bow frames get a straight wedge (frame 2 front area 1963 instead of 800).
- Sanity table for every frame: face areas (should be within ~5 % of each other), valid polygons, min distance inner-outer (>= 2.3 mm for T=3.2), floor/seat per face. Look at the picture of 5 frames: whole frame, centre zoom, top zoom.
- Solids: OCP prism of the common blank, `BRepAlgoAPI_Common` with the slab, `BRepCheck_Analyzer`, volume; mesh with `BRepMesh_IncrementalMesh`. Export per 15 frames (about 12 MB each); a STEP of 5 frames is 28 MB (do not commit).
- 3D check on the keel: `frames_on_keel_side_check.py` (Y=0 section) shows the flat blank against the sloped pocket floor. Bow numbers: pocket slope 0.81 (frame 1) .. 0.25 (frame 5); flat blank hangs up to 6.5 mm above the pocket at X+4 and enters the keelson by the same amount at X-4. The builder accepted this (hand sanding) but the keel line "is not continuous enough" and must be worked again before closing.
- Cathead/step zones of the bulwark line (X 213-222, 251-262, 280) give steep top lines (frame 25: 105.6 -> 99.3 over 4 mm; frame 29: 118 -> 112.8). That is his line; flag, do not smooth.
