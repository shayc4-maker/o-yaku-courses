# 01 Rules (learned the hard way)

Language: reply to the builder in his language (Hebrew), minimum tokens, one precise question when unsure, files first, no narration.

## The ten rules
1. **No line tracing, ever.** No automatic outline following, no hundreds of pixels, no "fit a curve to the ink". Lines are made of a MINIMUM number of reference POINTS (every 10–20 mm of arc, plus a corner point where a straight begins) joined by a spline (or a straight where the builder says straight). Pixels are only used to centre one chosen point on the ink (column/row snap within about +-1.5 mm) and then the point is shown for approval.
2. **Points first, in 2D, with ids and coordinates, then splines, then 3D.** Never skip a gate. The builder approves per item; only then record in `data/*approved*.json`.
3. **Iron lines do not move.** Approved body-plan lines and the approved outer lines of the frames are iron. Mismatches between plans are closed by adding a helper line (a waterline, a point set), never by moving an iron line. Anything that touches iron needs explicit approval.
4. **The builder's marks beat your reading.** If he draws a line, sends coloured pixels, a screenshot with a red line, or an edited 3dm, THAT is the data. Read it exactly (see 04), do not "improve" it. If his mark is not exactly on a hard fact (e.g. the rabbet end), say the offset in mm and ask; the original plan wins unless he says otherwise.
5. **Calibrate every plan before using it** and show the residuals. Scales differ per axis and per plan. A re-sent scan must be registered to the already calibrated image, not re-calibrated from scratch.
6. **One item per round.** A station, a line, a frame, then (once the method is approved) rounds of 5 frames. Show one clear image per ask: he reads on a phone, zoom crops where lines are dense.
7. **Say what was not checked** (not opened in Rhino, no clash test, rough registration...). Never write "done and verified" for something you did not verify.
8. **Dimensions come from the builder's plans and dots**, each computed from its source, never chained from an earlier cut feature. Thickness from the plan scale. Images such as SOS pictures are orientation only.
9. **Report numbers, not adjectives**: deviation in mm, curvature sign changes, min radius, areas, validity of solids.
10. **Commit and push after every deliverable**, append a few lines to STATE.md (what, files, caveats), send files with SendUserFile. Never commit files > 30 MB (STEP of 28 MB stays out of git).

## Vocabulary used by the builder
- "iron line" = fixed reference. "double frame" = layers A (X-4..X) and F (X..X+4), 8 mm total, planks 4 mm. "blank" = flat-cut piece before sanding. "laser marks" = final (sanded) face outlines marked on the blank for hand sanding.
- "waterline" (WL) = horizontal section at constant Z; the builder also uses it for any Z-constant line (deck level).
- "plan" in Hebrew speech may mean a top-view image (not only "a plan").
- "spline" = interpolating cubic through approved points; yellow on his marks = spline, anything else straight.
