"""
scrylab – Python client for ScryLab.
"""

from ._client import ScryLabError, _default_client
from ._utils import normalize_one, normalize_many
from typing import Optional, Union

ScryLabError.__module__ = "scrylab"

__all__ = ["send", "send_many", "plot", "ScryLabError"]
__version__ = "0.1.0"


def send(
    y,
    name: Optional[str] = None,
    source: str = "Sent from API",
    x=None,
    z=None,
    y_unit: Optional[str] = None,
    x_unit: Optional[str] = None,
    z_unit: Optional[str] = None,
    overwrite: bool = False,
) -> None:
    """Send a single signal to ScryLab without plotting.

    y accepts a numpy array, a plain list, or a pandas Series.
    For a Series, x defaults to the index and name to the series name.
    x accepts a numpy array, list, or pandas Series/Index.
    z is optional – pass a 1D array/list/Series for a color axis or a 2D array/DataFrame for a spectrogram.
    source is created automatically if it doesn't exist yet.
    Raises ScryLabError on failure or if the name already exists (overwrite=False).
    """
    try:
        yi, ni, xi, zi = normalize_one(y, name, x, z)
        client    = _default_client
        source_id = client._resolve_source(source)
        client.send_one(yi, ni, source_id, xi, zi, y_unit, x_unit, z_unit, overwrite=overwrite)
    except ScryLabError as e:
        raise ScryLabError(str(e)) from None
    except Exception as e:
        raise ScryLabError(str(e)) from None


def send_many(
    y,
    names=None,
    source: str = "Sent from API",
    x=None,
    z=None,
    y_unit: Union[str, list, None] = None,
    x_unit: Union[str, list, None] = None,
    z_unit: Union[str, list, None] = None,
    overwrite: bool = False,
) -> None:
    """Send multiple signals to ScryLab without plotting.

    y accepts:
      - a list of arrays, lists, or pandas Series: each element is one signal
      - a pandas DataFrame: each column is one signal, index as x

    x and z can each be a list (one entry per signal) or a single value broadcast to all.
    z accepts a 1D array (color axis) or 2D matrix (spectrogram) per signal.
    y_unit, x_unit, z_unit each accept a single string (applied to all signals) or a list
    (one unit per signal).
    Raises ScryLabError on failure.
    """
    try:
        ys, ns, xs, zs = normalize_many(y, names, x, z)
        client    = _default_client
        source_id = client._resolve_source(source)
        client.send(ys, ns, source_id, xs, zs, y_unit, x_unit, z_unit, overwrite=overwrite)
    except ScryLabError as e:
        raise ScryLabError(str(e)) from None
    except Exception as e:
        raise ScryLabError(str(e)) from None


def plot(
    y,
    name: Optional[str] = None,
    x=None,
    z=None,
    y_unit: Optional[str] = None,
    x_unit: Optional[str] = None,
    z_unit: Optional[str] = None,
    overwrite: bool = False,
) -> None:
    """Send a single signal to ScryLab and plot a signal-instance.

    Accepts the same y, x, z types as send(). Always lands in data source "Sent from API".
    A new plot is created if none exists.
    """
    try:
        yi, ni, xi, zi = normalize_one(y, name, x, z)
        client    = _default_client
        source_id = client._resolve_source("Sent from API")
        results   = client.send_one(yi, ni, source_id, xi, zi, y_unit, x_unit, z_unit, overwrite=overwrite)
        for r in results:
            client.plot(r["signal_id"])
    except ScryLabError as e:
        raise ScryLabError(str(e)) from None
    except Exception as e:
        raise ScryLabError(str(e)) from None
