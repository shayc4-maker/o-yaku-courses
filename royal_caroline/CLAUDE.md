# Royal Caroline 1:48 POF - working rules (read first, then STATE.md)

## Language and tokens
- Reply in Hebrew, minimum tokens: short results, no narration, no interim reports. Send whole results plus a short list of open questions.

## Geometry rules
- Never sample lines by pixel tracing or hundreds of points. Use the minimum number of reference points, with straight lines or splines between them (green dot = straight, blue dot = spline).
- If reference points cannot be read reliably from a plan, ask the builder (point ids, a chain, or a red sketch) instead of guessing.
- Always start with a 2D drawing showing the point positions (ids, coordinates). Build nothing further until the builder approves it.
- Images and plans are reference for form and direction only, not a source of dimensions, unless the builder says otherwise. Dimensions come from his plans and dots, each computed from the source, never chained from earlier cut features. Thickness comes from the plan scale (backbone 5.3 mm sided, centred on Y=0).
- Anything touching the frames aligns to the frames (seats from `data/backbone_contour_v5.json`), not to the dots.
- Mark sanding/bevel allowance on parts that need it.

- Choose control points that give clean smooth splines (drop points that cause waviness). Yellow on the builder's marks = curved line (spline), everything else straight. Do not make a joint between a straight line and a curve tangent unless needed (or approximately).

## Deliverables
- Rhino 8 `.3dm` (layer per part; closed curve plus solid), STEP when booleans are needed. Keep files under 30 MB (split or zip) so they can be sent to the builder.
- Check solids (valid, no clashes) before sending; say plainly what was not checked (for example not opened in Rhino).
- Commit and push to the session branch after each deliverable; update STATE.md with a few lines; send the file or image to the builder with SendUserFile.
- Printable marking sheets: lighten the plan to 50 % brightness so the builder's coloured pen marks show; corner crosses with source coordinates; the builder scans back (`py/scan_register.py` registers by the crosses; template match, scan is a different page size).
