# Rhino 8 (Python 3): places the 4 calibrated picture planes. Run with _RunPythonScript; it asks for the folder holding the PNG files.
import os
import Rhino, scriptcontext as sc, rhinoscriptsyntax as rs
from Rhino.Geometry import Plane, Point3d, Vector3d, PlaneSurface, Interval
from Rhino.DocObjects import ObjectAttributes, ObjectMaterialSource, Material

# name, file, origin (bottom-left of the picture), u axis (picture right), v axis (picture up), width, height
VIEWS = [
    ("bodyplan_aft", "bodyplan_aft.png", (-80.05, 94.55, -15.21), (0, -1, 0), (0, 0, 1), 94.97, 156.61),
    ("bodyplan_fwd", "bodyplan_fwd.png", (-80.05, 0.0, -11.98), (0, -1, 0), (0, 0, 1), 106.09, 138.16),
    ("elevation", "elevation.png", (-76.28, -0.05, -31.11), (1, 0, 0), (0, 0, 1), 687.01, 210.46),
    ("halfbreadth_plan", "halfbreadth_plan.png", (-51.22, -103.88, -0.05), (1, 0, 0), (0, 1, 0), 652.30, 207.01),
]

folder = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else None
if not folder or not os.path.exists(os.path.join(folder, VIEWS[0][1])):
    folder = rs.BrowseForFolder(message="Folder with the PNG files from the zip")
if not folder:
    raise SystemExit

for name, fn, o, u, v, w, h in VIEWS:
    path = os.path.join(folder, fn)
    if not os.path.exists(path):
        print("missing", path); continue
    lname = "VIEW_" + name
    if not rs.IsLayer(lname):
        rs.AddLayer(lname)
    pl = Plane(Point3d(*o), Vector3d(*u), Vector3d(*v))
    srf = PlaneSurface(pl, Interval(0, w), Interval(0, h))
    mat = Material()
    mat.Name = name
    mat.SetBitmapTexture(path)
    mi = sc.doc.Materials.Add(mat)
    at = ObjectAttributes()
    at.LayerIndex = sc.doc.Layers.FindByFullPath(lname, -1)
    at.MaterialIndex = mi
    at.MaterialSource = ObjectMaterialSource.MaterialFromObject
    at.Name = name
    sc.doc.Objects.AddSurface(srf, at)
sc.doc.Views.Redraw()
print("done - switch the viewport to Rendered (or Texture/Arctic) to see the pictures")
