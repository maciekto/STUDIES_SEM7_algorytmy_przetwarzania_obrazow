import numpy as np
from app.model import histogram


def test_compute_lut_sum_and_stats():
    img = np.array([[0, 1, 1], [2, 2, 2]], dtype=np.uint8)
    h = histogram.compute_lut(img, levels=256)
    assert h.sum() == img.size

    mean, median, std, count = histogram.stats_from_hist(h)
    # manual mean: (0 + 1 +1 +2+2+2)/6 = 8/6 = 1.333...
    assert abs(mean - (8.0 / 6.0)) < 1e-6
    # median: sorted values [0,1,1,2,2,2] median is 1 (lower middle)
    assert median == 1
    assert count == img.size
