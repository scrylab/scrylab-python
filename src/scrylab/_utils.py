from typing import Optional
import numpy as np


def _broadcast(val, n):
    return list(val) if isinstance(val, (list, tuple)) else [val] * n


def normalize_one(y, name: Optional[str], x, z):
    try:
        import pandas as pd
        if isinstance(y, pd.Series):
            name = name or y.name
            x    = x if x is not None else y.index.to_numpy()
            y    = y.to_numpy()
        if isinstance(z, pd.DataFrame):
            x = x if x is not None else z.columns.to_numpy()
            z = z.to_numpy()
        elif isinstance(z, pd.Series):
            z = z.to_numpy()
    except ImportError:
        pass
    if x is not None:
        x = np.asarray(x)
    if z is not None:
        z = np.asarray(z)
    return np.asarray(y), name or "Unnamed Signal 1", x, z


def normalize_many(y, names, x, z):
    try:
        import pandas as pd
    except ImportError:
        pd = None

    if pd is not None and isinstance(y, pd.DataFrame):
        cols  = list(y.columns)
        ys    = [y[col].to_numpy() for col in cols]
        names = names if names is not None else cols
        x_eff = y.index.to_numpy() if x is None else x
        xs    = [np.asarray(xi) if xi is not None else None for xi in _broadcast(x_eff, len(ys))]
        zs    = [np.asarray(zi) if zi is not None else None for zi in _broadcast(z, len(ys))]
        return ys, names, xs, zs

    y_items = list(y)
    n       = len(y_items)
    ys, auto_names, xs, zs = [], [], [], []
    for yi, xi, zi in zip(y_items, _broadcast(x, n), _broadcast(z, n)):
        if pd is not None and isinstance(yi, pd.Series):
            auto_names.append(yi.name)
            xs.append(np.asarray(xi) if xi is not None else yi.index.to_numpy())
            ys.append(yi.to_numpy())
        else:
            auto_names.append(None)
            xs.append(np.asarray(xi) if xi is not None else None)
            ys.append(np.asarray(yi))
        zs.append(np.asarray(zi) if zi is not None else None)
    if names is None:
        names = [an or f"Unnamed Signal {i + 1}" for i, an in enumerate(auto_names)]
    else:
        names = list(names)
    return ys, names, xs, zs
