import numpy as np
import pandas as pd

from scrylab._utils import normalize_one, normalize_many

# --- normalize_one ---

def test_normalize_one_numpy_array():
    y = np.array([1.0, 2.0, 3.0])
    yi, name, xi, zi = normalize_one(y, None, None, None)
    assert isinstance(yi, np.ndarray)
    np.testing.assert_array_equal(yi, y)
    assert name == "Unnamed Signal 1"
    assert xi is None
    assert zi is None


def test_normalize_one_series_name_and_index():
    s = pd.Series([10.0, 20.0], index=[0.0, 0.5], name="Speed")
    yi, name, xi, zi = normalize_one(s, None, None, None)
    assert name == "Speed"
    np.testing.assert_array_equal(xi, [0.0, 0.5])
    np.testing.assert_array_equal(yi, [10.0, 20.0])


def test_normalize_one_series_x_override():
    s = pd.Series([10.0, 20.0], index=[0.0, 0.5], name="Speed")
    x = np.array([1.0, 2.0])
    _, _, xi, _ = normalize_one(s, None, x, None)
    np.testing.assert_array_equal(xi, x)


def test_normalize_one_z_dataframe():
    z_df = pd.DataFrame([[1, 2], [3, 4]], index=[10.0, 20.0], columns=[0.0, 1.0])
    _, _, xi, zi = normalize_one(np.array([10.0, 20.0]), None, None, z_df)
    np.testing.assert_array_equal(zi, z_df.to_numpy())
    np.testing.assert_array_equal(xi, z_df.columns.to_numpy())


def test_normalize_one_custom_name_overrides_series():
    s = pd.Series([1.0, 2.0], name="Original")
    _, name, _, _ = normalize_one(s, "Custom", None, None)
    assert name == "Custom"


# --- normalize_many ---

def test_normalize_many_list_of_arrays():
    a = np.array([1.0, 2.0])
    b = np.array([3.0, 4.0])
    ys, names, xs, zs = normalize_many([a, b], None, None, None)
    assert names == ["Unnamed Signal 1", "Unnamed Signal 2"]
    assert all(xi is None for xi in xs)
    assert all(zi is None for zi in zs)


def test_normalize_many_dataframe_input():
    df = pd.DataFrame({"Alpha": [1.0, 2.0], "Beta": [3.0, 4.0]}, index=[0.0, 1.0])
    _, names, xs, _ = normalize_many(df, None, None, None)
    assert names == ["Alpha", "Beta"]
    np.testing.assert_array_equal(xs[0], df.index.to_numpy())
    np.testing.assert_array_equal(xs[1], df.index.to_numpy())


def test_normalize_many_list_of_series():
    s1 = pd.Series([1.0, 2.0], index=[0.0, 0.5], name="Temp")
    s2 = pd.Series([3.0, 4.0], index=[0.0, 0.5], name="Pressure")
    _, names, xs, _ = normalize_many([s1, s2], None, None, None)
    assert names == ["Temp", "Pressure"]
    np.testing.assert_array_equal(xs[0], s1.index.to_numpy())
    np.testing.assert_array_equal(xs[1], s2.index.to_numpy())
