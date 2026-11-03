# Roadmap

Each item below is a proposed, issue-sized follow-up; none is part of v0.1.0.

1. **Parametric fit-gauge hardware** (`hardware/fit-gauge`): OpenSCAD axle-pivot
   arm using aluminium flat bar and printed axle block; centring spacers for
   100/110/130/135/142/148 mm and 12 mm thru-axle / QR; BSD index marks for
   `r=200–420 mm`; generated 20–75 mm tyre-section and fender-envelope gauges.
2. **Contour-gauge hardware** (`hardware/contour-gauge`): 5 mm-pitch retracting
   pin blocks with ArUco markers, radial stop, and BB adapter.
3. **Gauge photo reader** (`obcs gauge-photo`): OpenCV photo interpretation and
   a measurement overlay for manual review.
4. **Interactive measurement wizard** (`obcs measure`): guided capture of
   reference conditions and Level A / Level B measurements.
5. **Community data store** (`data/frames/<brand>/<model>/<year>-<size>.yaml`):
   keep `.raw.yaml` and photos, aggregate conservatively by minimum and spread,
   check outliers, and strip EXIF GPS from photos.
6. **Exports**: printable PDF data sheets and DXF profile export.
