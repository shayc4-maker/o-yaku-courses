# -*- coding: utf-8 -*-
"""
Royal Caroline 1:48 - Rhino 8 setup script (v1)
Run in Rhino 8: Tools > Script > Run (or ScriptEditor), with
RoyalCaroline_lines_1to48_v1.3dm open.

1. Places the 4 calibrated plan images as locked picture frames.
2. Lofts the 18 body-plan stations into a first half-hull surface.
3. Cuts that surface at waterlines I..VII so you can compare with
   the waterlines traced from the half-breadth plan (A1/4).

Units: mm, model scale 1:48. X forward from station 18, Y = half-breadth,
Z up from the baseline.
"""
import os, json
import rhinoscriptsyntax as rs
import scriptcontext as sc

WLZ = {"I": 8.689, "II": 17.378, "III": 26.068, "IV": 34.757,
       "V": 43.446, "VI": 52.135, "VII": 69.513}


def here():
    try:
        d = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(d, "images", "frames.json")):
            return d
    except Exception:
        pass
    d = rs.WorkingFolder()
    if d and os.path.exists(os.path.join(d, "images", "frames.json")):
        return d
    return rs.BrowseForFolder(message="Select the RoyalCaroline_Rhino folder")


def ensure_layer(name, color=None, parent=None):
    full = name if parent is None else parent + "::" + name
    if not rs.IsLayer(full):
        rs.AddLayer(name, color, parent=parent)
    return full


def place_images(folder):
    frames = json.load(open(os.path.join(folder, "images", "frames.json")))
    parent = ensure_layer("BACKGROUND_IMAGES", (180, 180, 180))
    for f in frames:
        lay = ensure_layer(f["file"].replace(".png", ""), (180, 180, 180), parent)
        existing = rs.ObjectsByLayer(lay)
        if existing:
            continue
        plane = rs.PlaneFromFrame(f["origin"], f["xaxis"], f["yaxis"])
        path = os.path.join(folder, "images", f["file"])
        pid = rs.AddPictureFrame(plane, path, f["w"], f["h"], True, False, False, False)
        if pid:
            rs.ObjectLayer(pid, lay)
    rs.LayerLocked(parent, True)


def loft_hull():
    src = "STATIONS_LOFT_uniform14"
    if not rs.IsLayer(src):
        print("Layer %s not found - open RoyalCaroline_lines_1to48_v1.3dm first" % src)
        return None
    crvs = [c for c in rs.ObjectsByLayer(src) if rs.IsCurve(c)]
    crvs.sort(key=lambda c: rs.CurveStartPoint(c)[0])
    lay = ensure_layer("HULL_LOFT_v1", (90, 160, 90))
    old = rs.ObjectsByLayer(lay)
    if old:
        rs.DeleteObjects(old)
    srf = rs.AddLoftSrf(crvs, loft_type=0)   # 0 = Normal
    if not srf:
        print("Loft failed")
        return None
    rs.ObjectLayer(srf, lay)
    return srf[0]


def contour(srf):
    lay = ensure_layer("LOFT_WATERLINES_v1", (230, 120, 0))
    old = rs.ObjectsByLayer(lay)
    if old:
        rs.DeleteObjects(old)
    for name, z in sorted(WLZ.items(), key=lambda t: t[1]):
        plane = rs.PlaneFromNormal((0, 0, z), (0, 0, 1))
        cs = rs.AddSrfContourCrvs(srf, plane)
        for c in cs or []:
            rs.ObjectLayer(c, lay)
            rs.ObjectName(c, "loftWL_" + name)


def main():
    folder = here()
    if not folder:
        return
    rs.EnableRedraw(False)
    place_images(folder)
    srf = loft_hull()
    if srf:
        contour(srf)
    rs.EnableRedraw(True)
    rs.ZoomExtents(all=True)
    print("Done. Compare layer LOFT_WATERLINES_v1 (orange) with "
          "WATERLINES_from_A1-4_plan (red). Use CurvatureGraph / Zebra on HULL_LOFT_v1.")


main()
