import numpy as np
from app.model import histogram, mapping


def test_stretch_no_clip_edges():
    # create histogram with signals at 10 and 200 only
    img = np.zeros((2, 3), dtype=np.uint8)
    img.flat[0] = 10
    img.flat[1:] = 200
    h = histogram.compute_lut(img, levels=256)
    lut = mapping.stretch_linear_from_hist(h, levels=256, clip_frac=None)
    # values <=10 should map to 0, >=200 to 255
    assert lut[0] == 0
    assert lut[10] == 0
    assert lut[200] == 255
    assert lut[255] == 255


def test_stretch_clip_fraction_respected():
    # create histogram with many low-end pixels and some high-end
    img = np.concatenate([np.zeros(90, dtype=np.uint8), np.full(10, 200, dtype=np.uint8)])
    h = histogram.compute_lut(img.reshape(1, -1), levels=256)
    # clip 10% total -> clip_total ~ 10 pixels
    clip_frac = 0.1
    lut = mapping.stretch_linear_from_hist(h, levels=256, clip_frac=clip_frac)
    # find zmin,zmax by lut boundaries
    zeros = np.where(lut == 0)[0]
    fulls = np.where(lut == 255)[0]
    zmin = int(zeros[-1]) if zeros.size else 0
    zmax = int(fulls[0]) if fulls.size else 255
    clip_total = int(h.sum() * clip_frac + 0.5)
    clipped = int(h[: zmin + 1].sum() + h[zmax:].sum())
    assert clipped <= clip_total
