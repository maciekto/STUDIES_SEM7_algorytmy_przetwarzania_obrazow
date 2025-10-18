# How to install project

python3.12 -m venv .venv 

source .venv/bin/activate

pip install -r requirements.txt

Notes about LAB 1 compliance
--------------------------------
This repository was adapted to follow requirements for LAB 1 (histogram / LUT
and point operations). New modules implement manual histogram counting,
manual cumulative histogram, linear stretch (with optional clipping),
selective equalization, and point-wise operators via LUTs. A simple
histogram renderer (app/ui/hist_canvas.py) draws bar plots using OpenCV
drawing primitives — no automatic plotting libraries are used.

Key rules followed:
- No use of cv.calcHist, cv.equalizeHist, cv.normalize, cv.LUT or plotting libraries
  for histogram/mapping computations.
- OpenCV is used only for image I/O and presentation (drawing primitives).

See app/model for histogram/mapping/point_ops implementations and
app/controller for high-level helpers.
