# 07 Rhino / 3dm / STEP delivery and library pitfalls

## Files
- Rhino 8 `.3dm` (layer per part), under 30 MB (split by 15 frames, ~12 MB each). STEP only when booleans are needed; it is huge (a 5-frame STEP was 28 MB) -> not in git, offer on request.
- Say plainly: "not opened in Rhino". Check solids (OCP `BRepCheck_Analyzer`, volume) and state it.
- Half ship only (+Y) when the builder will edit lines (mirror is derived). Frames in `v2..v5` are +Y master, -Y mirror.

## Picture planes (plan image under the lines so the builder can arrange curves)
- Warp the plan into model coordinates (`scripts/p1a_strip.py: warped`), save PNG, make a `Mesh` quad with plane texture mapping (`TextureMapping.CreatePlaneMapping`), material with `SetBitmapTexture('file.png')` (relative name).
- The PNG must be in the SAME FOLDER as the 3dm (not in a sub-folder) -> zip with both at the root; tell him to open in Rendered/Textured display mode (Wireframe/Shaded shows nothing). This failed once ("I can't see the picture").
- Side view plane at Y=-0.05; top view plane at Z = deck level.

## rhino3dm pitfalls
- No `Brep.CreateFromCornerPoints`: use Mesh planes.
- `NurbsCurvePointList` has no `Count`; use `len`/`PointCount`.
- NURBS from scipy: `splprep` gives (t, c, k); build `NurbsCurve(3, False, k+1, n)`, set points (Point4d weight 1) and knots `t[1:-1]`; or `NurbsCurve.Create(False, k, points)` and set knots. After reading a file back, curves come back as `PolylineCurve`/`LineCurve`/`NurbsCurve`: `ClosestPoint` is not available on NurbsCurve; verify by sampling `PointAt`.
- Name checks like `'line' in name` match `'spline'`: use explicit kind flags (this produced straight lines instead of splines once).
- File reading of big 3dm: use rhino3dm, not the Read tool. Compare an edited file to the original by sampling every object (name+type+60 samples) to find what the builder changed (new unnamed curves = his drawings; changed curves list max deviation).
- A `.rhl` file is only a Rhino lock file (user/computer/time), not data; ask for the 3dm.

## OCP / environment pitfalls
- `STEPControl_Reader.ReadFile` on a missing upload path SEGFAULTS (exit 139, no message). Upload folders disappear between sessions: check the path first; fall back to `data/step44_profiles.json` (profiles of the STEP solids: keelson = Boss-Extrude4[4], keel/deadwood+stem = Boss-Extrude2[2]).
- `TopoDS.Face_s` may not exist: use `TopoDS.Face`.
- Piping a script into `head`/`tail` can kill it before the outputs are saved (happened more than once): redirect to a log file, then read it.
- Long jobs (3 x 15 frames) exceed the 120 s tool limit: run in background and use the Monitor tool; commit scripts while waiting.
- Matplotlib 3D is not usable offscreen; 3D renders were done with three.js in headless chromium (`render3d_blanks.py`), or give the builder the 3dm and a Y=0 section picture.

## Sending
- SendUserFile with a one-line caption; images readable on a phone (dpi 55-70, zoom panels). Give the exact folder instruction for zips.
