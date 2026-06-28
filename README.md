# scrylab-python

Python wrapper for the [ScryLab](https://scrylab.de) REST API. Lets you plot signals directly in a running ScryLab GUI from any Python environment – scripts, Jupyter notebooks or simulation pipelines – as a faster, more interactive alternative to matplotlib or plotly for exploratory signal analysis.

## What you can do

- Send 1D signals (time series, measurement channels, …) into ScryLab's data browser
- Send ~~colored lines (signal + scalar color axis)~~ (coming soon) or spectrograms (2D matrix)
- Convenience function: open signals directly in a plot from code

## Installation

1. Prerequisite: the ScryLab GUI (desktop app) needs to be running on the same machine. [Installation Guide](https://docs.scrylab.de/docs/getting-started/installation/) 
2. Install the wrapper: `pip install scrylab`

## Quick start

```python
import scrylab as scry
import numpy as np

t = np.linspace(0, 10, 1_000)
y = np.sin(2 * np.pi * 5 * t)

scry.plot(y, name="Example Signal", x=t, y_unit="V", x_unit="s") # Convenience function: send + plot in one step

# Or send without plotting – then you can drag the signal into plots manually from the data browser
scry.send(y, name="Example Signal via send", x=t, y_unit="V", x_unit="s")

# Update the "Example Signal"
y2 = np.sin(2 * np.pi * 10 * t)
scry.send(y2, name="Example Signal", x=t, y_unit="V", x_unit="s", overwrite=True) # overwrite=True replaces the existing signal with the same name
```

## Usage

### `scry.send(y, …)`

Sends a signal into a data source without automatic plotting.

```python
scry.send(y, name="Speed", source="Testrun 01", x=t, y_unit="km/h", x_unit="s")
```

| Parameter | Description |
|-----------|-------------|
| `y` | numpy array, list, or `pandas.Series`; for a Series, `name` and `x` default to the series' name and index |
| `name` | signal name (auto-generated if omitted) |
| `source` | [data source](https://docs.scrylab.de/docs/concepts/data-sources/) to send into, default `"Sent from API"`; created automatically if it doesn't exist yet |
| `x` | numpy array, list, or `pandas.Series`/`Index`; auto-generated if omitted |
| `z` | optional color axis – 1D array/list/`pandas.Series` (one value per sample, colors the trace) or 2D array/`pandas.DataFrame` (matrix → spectrogram; columns map to x-axis, index to y-axis) |
| `y_unit`, `x_unit`, `z_unit` | axis units, e.g. `"V"`, `"s"`, `"Hz"` |
| `overwrite` | replace an existing signal with the same name; raises `ScryLabError` if `False` (default) and a signal with that name already exists |

### `scry.send_many(y, …)`

Sends multiple signals at once. `y` can be a list of arrays or a `pandas.DataFrame` (each column becomes a signal).

```python
scry.send_many(
    y=[channel_1, channel_2, channel_3],
    names=["Speed", "RPM", "Torque"],
    y_unit=["km/h", "1/min", "Nm"],
    source="Testrun 02",
)
```

| Parameter | Description |
|-----------|-------------|
| `y` | list of numpy arrays/lists/`pandas.Series`, or `pandas.DataFrame` (each column becomes one signal); Series names and indices are used automatically |
| `names` | list of signal names; auto-generated if omitted |
| `source` | [data source](https://docs.scrylab.de/docs/concepts/data-sources/) to send into, default `"Sent from API"`; created automatically if it doesn't exist yet |
| `x` | a single numpy array/list broadcast to all signals, or a list of numpy arrays/lists (one per signal) |
| `z` | ~~1D array (colored trace)~~ (coming soon) or 2D array/`pandas.DataFrame` (spectrogram) – broadcast a single value to all signals, or pass a list (one per signal) |
| `y_unit`, `x_unit`, `z_unit` | a single string applied to all signals, or a list of strings (one per signal) |
| `overwrite` | replace existing signals with the same name; raises `ScryLabError` if `False` (default) and a signal with that name already exists |

### `scry.plot(y, …)`

Same as `send()` but also opens the signal in a plot. Always uses `"Sent from API"` as the data source – use `send()` if you need a specific source. A new plot is created if none exists yet.

```python
scry.plot(y, name="Accelerometer", y_unit="m/s²", x_unit="s")
```

## pandas integration

Pass a `pandas.Series` as `y` and `name` and `x` are derived automatically from the series:

```python
import pandas as pd
import scrylab as scry

voltage = pd.Series(
    data=[0.1, 0.4, 0.9, 0.7],
    index=[0.0, 0.1, 0.2, 0.3],
    name="Voltage",
)

scry.send(voltage, y_unit="V", x_unit="s")
# equivalent to: scry.send(voltage.to_numpy(), name="Voltage", x=voltage.index, y_unit="V", x_unit="s")
```

You can still override `name` or `x` explicitly – they take precedence over the series metadata.

`send_many()` works the same way for a list of Series. Pass a `pandas.DataFrame` and every column becomes a signal, with the index shared as x-axis:

```python
df = pd.DataFrame({"Speed": [...], "RPM": [...]}, index=t)
scry.send_many(df, source="Testrun 03", y_unit=["km/h", "1/min"], x_unit="s")
```

## Spectrograms

Pass a `pandas.DataFrame` as `z` to send a spectrogram – columns map to the x-axis (e.g. time), the index to the y-axis (e.g. frequency):

```python
import numpy as np
import pandas as pd
from scipy.signal import spectrogram

fs = 1000  # Hz
t = np.linspace(0, 4, fs * 4, endpoint=False)

# 20 Hz for the first 2 s, then 80 Hz
y = np.where(t < 2, np.sin(2 * np.pi * 20 * t), np.sin(2 * np.pi * 80 * t))

f, t_bins, Sxx = spectrogram(y, fs=fs, nperseg=256)
Sxx_db = 10 * np.log10(Sxx + 1e-12)

spec = pd.DataFrame(Sxx_db, index=f, columns=t_bins)
scry.send(y=f, z=spec, name="Spectrogram", y_unit="Hz", x_unit="s", z_unit="dB")
```

## Running tests

```bash
pip install -e ".[dev]"
pytest
```
