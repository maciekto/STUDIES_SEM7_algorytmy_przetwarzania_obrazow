import numpy as np
from app.model import point_ops, mapping


def test_negation_idempotent():
    arr = np.arange(256, dtype=np.uint8).reshape(16, 16)
    lut = point_ops.negation_lut()
    out = mapping.apply_lut(arr, lut)
    out2 = mapping.apply_lut(out, lut)
    assert np.array_equal(arr, out2)


def test_requantization_levels():
    arr = np.tile(np.arange(256, dtype=np.uint8), (2, 1))
    lut = point_ops.requantization_lut(256, 4)
    out = mapping.apply_lut(arr, lut)
    unique = np.unique(out)
    assert unique.size <= 4


def test_thresholds():
    arr = np.array([[0, 100, 200, 255]], dtype=np.uint8)
    lut = point_ops.threshold_binary_lut(150)
    out = mapping.apply_lut(arr, lut)
    assert set(np.unique(out)).issubset({0, 255})
    lut2 = point_ops.threshold_keep_levels_lut(150, 10, 240)
    out2 = mapping.apply_lut(arr, lut2)
    assert set(np.unique(out2)).issubset({10, 240})
