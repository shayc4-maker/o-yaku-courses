# 08 Problems met so far and how not to repeat them

| # | Symptom | Cause | Prevention / fix |
|---|---------|-------|------------------|
| 1 | Builder angry: "why again trace lines?!" | automatic outline tracing/fitting of deck plans | chosen-column points shown for approval; never auto-trace |
| 2 | Deck points slid inward / sat on the wrong line | snap to nearest ink; outline includes planking, frame line is inside | identify line by order from a reference side; apply plank offset (4b 1.6, 4a 0.8) INWARD to get the frame line |
| 3 | Points on the cathead diagonal bar | picked a similar dark line | validate against known geometry; builder re-marks |
| 4 | Belly (double curve) at the keel junction, frames 14-27 | spline allowed to dip below the junction | floor points from stations + clamped tangent at the keel; lowest point = junction |
| 5 | Frame 1 front face broke at X=528 (loft collapse) | station 1 not lofted beyond | use station 1 directly |
| 6 | Frames overshoot the rabbet / end below the green point | several plans disagree (0.25-2 mm) and frame lift | calibrate all views, lift only control point 0 to the plan rabbet, builder repairs in Rhino, approved v2 |
| 7 | "2 mm from the centre" misread | meant for a 4 mm keel; plan keel is 5.2-5.3, neck 3 | take keel/neck from the plan |
| 8 | Inner line convex at frame ends (frame 1) | tangent blend wrong for V sections | concave-only inner rule, JOIN/JMAX rules (05) |
| 9 | "Round line at the top though the body plan is straight" | spline between straight stations | explain method in words; waterlines drive the interpolation |
| 10 | Deck-edge curve distorted in 3D | X from 5 rough deck-plan points, Z mixed | build the line from the plan outline/builder's line and frame crossings; show top and side together |
| 11 | Gap/discontinuity between the top line and frame 1 | his line ended at Y 38.2 while frame 1 front at Z=101 is at Y 44.3 | one waterline through ALL frames to the rabbet at constant Z |
| 12 | Plane splines straight / wavy above WL VII | 2 points only | add estimated mid point (say so) or ask for a mark |
| 13 | Overwrote another plan's registration file | script wrote fixed output name | rename output; `git checkout` file; check `git status` after sed-copies |
| 14 | Texture not visible in Rhino | PNG in subfolder; wrong display mode | PNG beside 3dm; Rendered mode |
| 15 | Straight lines instead of splines in 3dm | `'line' in 'spline'` | explicit flags |
| 16 | STEP load segfault | upload path gone | check path, use data/step44_profiles.json |
| 17 | Frame areas wrong (190, 1963, 244 vs 800) in bow frames | offset self-intersection, wedge inner line, join too long | offset_curve, JOIN=min(34,8D), JMAX=40; always print the area table |
| 18 | Blank floor hangs above the sloped keel pocket (up to 6.5 mm) | flat prism over 8 mm on a slope | accepted by the builder (laser marks + hand sanding), but report the numbers and make sure enough material |
| 19 | Beam rectangles were gun ports | assumed meaning | ask what an object is; builder: "find the lower line of the bulwark" |
| 20 | Dropping builder's marks M34-M36 to straighten a bump | tried to be helpful | never drop marks; give points+curves and let him arrange |
| 21 | Frame tops looked 12 mm too low | plotted only the curve, not the straight `top` segment | plot curve + top; extend tops to the line, never trim |
| 22 | Plan registration of top view conflicts with the side view (9.7 mm at the bar) | different drawings, different step positions | treat as open; ask one precise question with a picture; builder decides which plan wins |
| 23 | Processes killed by `| head` | pipe closes early | log to a file |
| 24 | Reading the whole 3dm into context | too large | use rhino3dm, print summaries |
| 25 | Ran long jobs in the foreground (timeout) | 120 s limit | background + Monitor |

General: when the builder says "does not look right", measure first (areas, distances, curvature), show the numbers, then fix; when he gives a rule, write it in STATE.md and in this playbook the same day.
