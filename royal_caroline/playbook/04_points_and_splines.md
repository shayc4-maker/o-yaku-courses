# 04 Points and splines (no tracing)

## Getting points
- Choose columns/rows yourself (arc spacing 10-20 mm, corners), snap each to the ink centre inside a small window (+-1.5 mm) and show the result. If two parallel lines are 1-2 mm apart ("nearest ink" mis-snaps), identify the line by its ORDER counted from a reference side and validate against approved neighbours (a new line must lie outside/inside the approved one).
- Ink thickness matters: take the centre of the run; for a band (several lines merged) take the band centre and SAY so. Hatched or thick regions: do not snap, ask.
- Straight segments (vertical tops, flats, steps) get corner points and are straight lines; curved parts get a spline. Do not join a straight and a curve tangentially unless he asks.
- Dark rectangles on the sheer plan can be gun ports, not beams: ask what an object is before using its edge. (Cost one round: "the squares are the gun ports".)
- Take the builder's own picks over automatic detection. Offer candidates as numbered ids on an image and let him choose.

## Splines
- Interpolating cubic: `scipy.interpolate.splprep(Q.T, k=3, s=0)`; for 2-3 points use k=len-1. Sort points along the line; drop duplicates.
- Always report: curvature sign changes (threshold |k|>1e-3), min radius, max deviation, monotonicity in X.
- Smoothing only when the builder says "smooth": weighted smoothing spline (`w`, `s`) with end points weight 50; pick the smallest s that gives 0 sign changes; report max deviation from the points (we used s=0.4 -> 0.21-0.34 mm). Never smooth iron.
- A line through frame crossings inherits their noise (about 0.1-0.3 mm): that was the source of "15 curvature sign changes" on the deck waterline.
- Tangent to another line: include the points of that line in the fit (the join becomes tangent automatically) instead of forcing a derivative.
- Many frames: spline per segment, not one spline over steps and bumps. Segments: splines through chosen points, straights for steps. The builder arranges the final curves himself in Rhino; give him the points + segment curves on the plan picture (see 07).
- Rounded vs straight: a line with only 2 points is a straight line; if the builder wants it curved, add a middle point whose bulge follows the trend of its neighbours (sagitta/chord 0.09, 0.06, 0.038 -> 0.025) and say it is an estimate.

## Waterline-progression method (frames from the body plan)
Y(face) = Y_stA(Z_k) + u_k(X) * (Y_stB(Z_k) - Y_stA(Z_k)), where A, B are the neighbouring body-plan stations, u_k from the original waterline k. Body plan leads, waterlines are reference; they need not overlap fully. Floor points near the keel from the stations (interpolate in Z at fixed Y); clamped end tangent at the keel junction (a double belly at the keel is forbidden: the lowest point of the spline is the junction with the keel).
