# Open Bicycle Clearance Specification

**Version:** 0.1.0 draft  
**Status:** community proposal; not affiliated with ETRTO or ISO  
**Language:** The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**,
**SHOULD NOT**, and **MAY** are to be interpreted as described in RFC 2119.

## 1. Scope and terms

OBCS describes how a bicycle frame or fork reports tyre, fender, and chainring
clearance. It does not certify structural strength, handling, wheel compatibility,
or safe operation. A publication MUST identify the tested frame size and the
conditions under which its measurements were made.

The terms *tyre* and *fender* are used throughout. Rim sizes are exact ETRTO /
ISO 5775 bead-seat diameters (BSD) in millimetres. Tyre sizes are written as
measured width-BSD, for example `50-622`. BSD values MUST NOT be rounded or
inferred from a nominal inch name: 571/584/590 and 622/630/635 are distinct
diameters. The BSD of 686 mm is included as a core row but MUST be marked
“BSD to be verified against ETRTO” until confirmed.

## 2. Coordinate system and clearance profile

Tyres, fenders, and chainrings are rotationally symmetric. Therefore, spinning
frame/fork material around the wheel axle reduces its relevant geometry exactly
to a two-dimensional radial/lateral profile. This reduction is exact for an
axisymmetric component: no angular samples are needed.

The wheel axle is the origin. `r` is radial distance from the axle in mm; `z` is
lateral distance from the wheel centre plane in mm. At each radius, record the
smallest absolute lateral distance to frame material on each side as
`z_free_left(r)` and `z_free_right(r)`. Each is the nearest available surface
from the centre plane; the two sides can differ.

```text
                z (lateral)
                   →
     left space  | wheel plane |  right space
       z_free_L  |     z=0     |  z_free_R
                 |     ● axle  |
                 |      ↑ r    |
                 |      │      |
                tyre rotates about axle
```

`max_radius` is the radial distance to the closest frame material directly in
the tyre path (for example seat tube, bridge, or fork crown). Rear clearance
MUST use the worst case over the full permitted axle/sliding positions.
Suspension clearance MUST use the worst case over the full travel. Published
profiles MUST give units, sorted radii, and enough coverage for every claimed
fit.

For chainrings, use the bottom-bracket (BB) axis. `z_frame_max_drive(r)` is the
outermost drive-side frame material at radius `r`; ignore the BB shell/spindle
zone. The ring sits outboard of this profile.

## 3. Reference shapes

### 3.1 Reference tyre

For BSD `B` and measured width `W` (mm), the reference cross-section is a circle
of diameter `W`, centred at `r_c = B/2 + 0.45W`. Its specified height is
`H = 0.95W` and outer radius is `B/2 + 0.95W`. For
`B/2 <= r <= B/2 + 0.95W`, its half-width is:

`sqrt((W/2)^2 - (r - r_c)^2)`

Real measured width depends on rim internal width (approximately +0.4–0.5 mm
per +1 mm rim width); tyres commonly stretch 1–2 mm over time. Publications
MUST identify the rim/measurement basis when known.

Approximate display-only outer diameter is `OD = B + 2 * 0.95 * W`.

### 3.2 Reference fender

The reference fender is a 2 mm shell, 12 mm radial gap above the tyre, width
`W + 10 mm`, wrapping 15 mm down each side. The reference implementation uses
this envelope for conservative fit prediction. Real fender cross-sections and
mount hardware MUST be measured separately for a definitive claim.

### 3.3 Chainring

For `N` teeth, pitch diameter is `Dp = 12.7 / sin(180°/N)` mm. Envelope radius
is `Dp/2 + 4 mm`; reference ring width is 6 mm centred on its chainline, and
margin is 3 mm. A ring fits only if
`z_frame_max_drive(r) <= chainline - 3 - margin` for all
`r <= envelope_radius + margin`. Ignore the BB shell/spindle zone.

Reference pitch diameters (mm): 34T 137.6, 40T 161.9, 46T 186.1,
50T 202.3, 53T 214.4.

## 4. Level A — fit matrix (REQUIRED)

Every conforming publication MUST provide two matrices: without a fender and
with a fender. Rows are exact BSD values; columns are measured tyre widths.

Core BSD rows: 406, 559, 584, 622, and 686 mm. Extended optional rows: 203,
254, 305, 349, 355, 451, 507, 520, 540, 571, 590, 597, 630, 635, and 787 mm.
A sheet for nominal BSD `X` MUST also include the next size up and down in the
combined core and extended list, when present.

Core widths are 20–75 mm in 5 mm steps. Optional widths are 28, 32, 38, and
42 mm, plus 80–125 mm for fat bikes. Cells are integer minimum measured gap in
mm, `x` when it does not fit, or `null` when not tested. Optional detail MAY
include `{lateral, radial, binding_point}`. Matrix width is measured tyre width,
not the nominal label.

The fender mount checklist MUST support: `dropout_f`, `dropout_r`, `crown_hole`,
`mid_fork`, `ss_bridge`, `cs_bridge`, and `other`.

A chainring section MAY declare 1x maximum teeth per chainline in
43.5, 45, 47.5, 50, 52, and 55 mm; 2x supported combinations; front derailleur
mount (`braze-on`, band clamp diameter, or `none`), `fd_ring_range` [min, max],
and `max_tyre_with_fd`.

## 5. Margins and Level B — clearance profile (OPTIONAL)

Fit margin classes are road 4 mm, all-road 6 mm (default), and mud 10 mm. A
tyre fits a class when its minimum clearance gap is greater than or equal to
that class margin. A publication MUST state the selected margin for generated
claims.

Level B MAY provide left/right `z_free(r)` polylines, `max_radius`, and
`bb_profile_drive`. A profile MUST NOT be extrapolated beyond its measured
coverage. If coverage does not include all required radii, the result is
“insufficient data,” not fit or no-fit.

An SVG drawing SHOULD show both sides at 1:1 scale with `r` vertical, `z`
horizontal, and the machine-readable polylines embedded. DXF export is optional.

## 6. Generated label and consistency

A generated label MUST report maximum passing tyre size per BSD, with and
without fenders, at the selected margin, using ETRTO notation and a common name
in parentheses. It MUST include chainring limits, fender mounts, reference
conditions, and data provenance.

When both Level A and Level B are published, software MUST predict Level A gaps
from the profile and flag cells whose measured and predicted gaps differ by
more than 2 mm. Untested cells remain untested.

## 7. Provenance and confidence

Each measurement SHOULD record source, method, instruments, resolution, date,
contributor, repeats, and uncertainty. Confidence is one of `declared`,
`measured`, `verified`, or `manufacturer-confirmed`. “Verified” means repeated
or independently checked measurements; “manufacturer-confirmed” identifies
confirmation by the frame maker, not endorsement of OBCS.

## 8. Versioning and conformance

Data MUST declare `obcs_version`. Patch releases correct editorial or
implementation defects without changing interpretation; minor releases add
compatible optional fields; a major release may change normative meaning.
Modified versions MUST NOT use the OBCS name or claim conformance unless they
pass the reference test suite. This document and all associated repository
materials are CC0 1.0 Universal.
