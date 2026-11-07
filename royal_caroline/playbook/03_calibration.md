# 03 Calibration of plans into model millimetres

## Method
- Fit pixel -> mm per axis (affine, least squares) on known features: station verticals, waterline rows, keel width, grid. Report rms and max residual. Typical: 0.04-0.2 mm. Scales differ per axis and per plan (aft body plan Y 3.1 % small; half-breadth plan 0.0819 vs 0.085 mm/px).
- Cross-check plans against each other at crossings (station x waterline). Report std/max. Do NOT fix the body plan; add a waterline if needed.
- Centre alignment: fit ONE centre line per view on the drawn dash-dot centre lines (fwd/aft body plan, top view); mast discs give the centre line on the deck plans. Align everything through that centre.
- Keel/neck dimensions come from the plan (keel half-width 2.65 -> 5.3 mm sided; neck half-width 1.8; backbone 5.3 mm centred on Y=0). Planking thickness: 4b 1.6 mm, 4a about 0.8 mm; deck-plan outlines include the plank, approved frames are width BEFORE planking and govern (offset the outline inward by the plank).

## Registering a re-sent scan (the builder re-sends plans at another pixel size)
- Do not recalibrate. Register the new image onto the existing aligned image: grid of template matches (normalised cross-correlation, `cv2.matchTemplate`, tiles ~380x520 px on `255-image` blurred), sub-pixel parabola refine, least-squares affine new->aligned with outlier rejection. Expect rms ~0.4 px (0.04 mm). Script: `scripts/register_plan1a_new.py` (and `register_plan5_new.py`). Then reuse the existing calibration. CAUTION: the script writes its JSON to a fixed filename; change the output name or you overwrite the other plan's registration (this happened once; git restored it).
- A coloured-pixel mark file (PDF) holds the image at full resolution: extract with `pdfimages -all`, find components with saturation > 60 (`cv2.connectedComponentsWithStats`), take centroids, apply the registration affine and the inverse of the sheet calibration (iterate 5x because the calibration is not exactly invertible in closed form). Script: `scripts/p1a_marks.py`. Colours encode groups (red, purple, yellow, green); the front green pixel was the rabbet end.
- Screenshots of the builder's red line: read the pixel axes from the plot ticks (e.g. 17.19 px/mm) and convert; state in the report that the precision is limited (about 0.3 mm).

## Known sheets (Royal Caroline)
- Sheer plan plan_1a: X = 0.08511*px - 357.14, Z = (2110 - row)*0.0850 plus per-view corrections in `data/plan_calibration_v2.json` (tilt 0.68 mm over 500 mm). Side view of the bow also exists in plan_5 (`p5map.py`), BUT plan_5 and plan_1a disagree about the position of the forecastle step by about 8-9 mm (plan_1a 529.3, plan_5 537.5). The builder decided that FRAME 1 (X=528.03) is the correct step; plan_5 / plan_4a registration of the bow top view is therefore only a reference (see 06).
- Deck plans 4a, 4b, 2b: 8507x2456 px, 300 dpi, 11.75 px/mm; centre line through the mast discs (main disc x 3860, fore disc about 6605-6612); X registered by C = stem aft face (555.0 at Z 86-88 from the STEP). Rough: ask before relying on it.
