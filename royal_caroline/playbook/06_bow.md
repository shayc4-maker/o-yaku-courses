# 06 Bow: rabbet, stem, plank planes, deck waterline, bulwark line

## Facts fixed by the builder
- The approved frames are width BEFORE planking and govern. Deck plans include the plank.
- Rabbet = iron line at the junction with the hull and the most significant side-view reference. One continuous rabbet spline through: lower ends of the approved face lines (frames 8..1 mid faces, frame 1 front), the continuation points R1-R7, R10, E and the plan's rabbet end M48 (560.74, 103.62) (E2 dropped: the original plan wins). Checks: other face ends <= 0.08 mm from the rabbet, X monotone, 3 curvature sign changes (one S at the top).
- Frame 1 front face (X=528.03) IS the step (forecastle step). The vertical frames/planks are built from it. It runs Z 28.2 (lifted lower end) to 118.66 (top on the bulwark line).
- Lifting the lower ends of frames 1-5 to the plan rabbet: only control point 0 of each lifted face is moved to the rabbet R2, capped below control point 1 (script lift_bottoms_half.py); the builder fixed distortions in Rhino and returned the file, which became approved v2.
- Planes parallel to the keel, perpendicular to the transverse frames: Y = 2.65 + 8.97 j (j=0..4; j=0 is the rabbet). Points on each plane: the frame-1 front-face crossing at X=528.03, waterline crossings WL IV-VII (Z 34.8, 43.4, 52.1, 69.5) forward of station 1, and the top on the deck waterline. Planes 4/5 have only 3/2 points (no data between WL VII 69.5 and the deck): plane 5 got an estimated middle point.
- Deck waterline: horizontal plane Z=101 (builder confirmed). ONE line through the frame-face crossings at Z=101 (frames 8..1), the builder's drawn top line as a general reference, ending on the rabbet at Z=101 (X=560.14, Y=1.8); smoothing s=0.4; then rounded further by his red sketch and tangent to the frame part. The tops of planes 2-5 sit on it (X 557.5, 553.1, 546.7, 537.3 at Z=101). Z=101 is a choice; the bulwark lower line rises 100.2 -> 103.6 forward.
- Bulwark lower line (all ship): from the builder's coloured pixels M0-M48 on plan_1a; 10 segments: splines S1 (M0-M13), S3 (M16-M23), S6-S8 (M25..M42), straights S2, S4, S10, steps S5 (X 280) and S9 (bow step). History: he first said to straighten the cathead bump (v2), then complained that the line ignored his points in zone B; the final line is HIS arranged curves through ALL his marks (`data/bulwark_line_v3.json`, from his 3dm; only S4/S5 moved <= 0.26 mm). Rule: never drop a builder's mark to get a nicer curve; give him the points + curves on the plan and let him arrange.

## Plank top view (deck plan 4a) — pitfalls
- 4a registration by the stem aft face puts the cross bar (end of the frame band) at X 537.7, which equals the plan_5 step, but frame 1 front is at 528.03 and plan_1a puts the step at 529.3. Unresolved (see 09). Therefore: top-line X positions come from the builder's drawn line + the rabbet end + frame crossings, NOT from the 4a registration alone.
- Do not take points from the cluttered bow tip of 4a; take the outline from the keel/stem line and use a few points for FORM reference only.

## Method for the "top line the vertical splines reach"
1. Put the plan image as a texture plane at deck Z in Rhino beside the planes, rabbet and frame 1; the builder draws one line in Top view (Z=0 is fine: only X,Y are used).
2. Use his line as a general reference; force it through the hard facts (rabbet end, frame crossings) with a smoothly fading correction; show the picture; get approval.
3. Z of each plane top = value of the bulwark/deck line at that X (or 101 on the deck waterline).
