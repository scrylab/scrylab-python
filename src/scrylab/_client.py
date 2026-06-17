import io
import json
from typing import Optional

import requests


_MIN_APP_VERSION = "0.1.10"


def _parse_version(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0,)


class ScryLabError(Exception):
    pass


class _Client:
    def __init__(self, host: str = "127.0.0.1", port: int = 5678, timeout: float = 30):
        self._base = f"http://{host}:{port}"
        self._timeout = timeout
        self._session = requests.Session()
        self._version_checked = False

    def _url(self, path):
        return f"{self._base}{path}"

    def _request(self, method, path, **kwargs):
        try:
            return self._check(self._session.request(method, self._url(path), timeout=self._timeout, **kwargs))
        except ScryLabError:
            raise
        except Exception:
            raise ScryLabError("ScryLab desktop app is not running or unreachable – download it at https://scrylab.de/download.") from None

    def _get(self, path):
        return self._request("GET", path)

    def _post(self, path, body=None, *, files=None, data=None):
        return self._request("POST", path, json=body, files=files, data=data)

    @staticmethod
    def _check(resp):
        try:
            data = resp.json()
        except ValueError:
            resp.raise_for_status()
            return {}
        if resp.status_code == 404:
            raise ScryLabError(f"Feature not available – please update ScryLab to v{_MIN_APP_VERSION} or later")
        if resp.status_code >= 400:
            raise ScryLabError(f"ScryLab error ({resp.status_code}): {data.get('error', resp.text)}")
        if data.get("status") == "error":
            raise ScryLabError(data.get("error", "Unknown error"))
        return data

    def _ensure_version(self):
        if self._version_checked:
            return
        data = self._get("/api/status")
        app_ver = data.get("version", "")
        if _parse_version(app_ver) < _parse_version(_MIN_APP_VERSION):
            raise ScryLabError(
                f"ScryLab v{app_ver} is too old – please update to v{_MIN_APP_VERSION} or later"
            )
        self._version_checked = True

    def _resolve_source(self, name: str) -> str:
        self._ensure_version()
        data = self._get("/api/sources")
        for s in (data.get("result") or []):
            if s.get("name") == name:
                return s["source_id"]
        created = self._post("/api/sources", {"name": name})
        return (created.get("result") or {})["source_id"]

    def send(self, ys: list, names: list, source_id: str, xs: list, zs: list,
             y_units, x_units, z_units,
             overwrite: bool = False) -> list[dict]:
        import numpy as np

        n = len(ys)
        def _norm(u):
            if u is None or isinstance(u, str):
                return [u] * n
            lst = list(u)
            return lst * n if len(lst) == 1 else lst

        y_units, x_units, z_units = _norm(y_units), _norm(x_units), _norm(z_units)
        files, metas = [], []
        for yi, ni, xi, zi, yu, xu, zu in zip(ys, names, xs, zs, y_units, x_units, z_units):
            buf = io.BytesIO()
            arrays = {"y": np.asarray(yi)}
            if xi is not None: arrays["x"] = np.asarray(xi)
            if zi is not None: arrays["z"] = np.asarray(zi)
            np.savez(buf, **arrays)
            buf.seek(0)
            files.append(("file", (f"{ni}.npz", buf.read(), "application/octet-stream")))
            m = {"name": ni, "target_source_id": source_id}
            if yu is not None: m["y_unit"] = yu
            if xu is not None: m["x_unit"] = xu
            if zu is not None: m["z_unit"] = zu
            if overwrite: m["overwrite"] = True
            metas.append(m)

        data   = self._post("/api/signals/upload_batch", files=files, data={"meta": json.dumps(metas)})
        result = data.get("result") or {}
        errors = result.get("errors", [])
        if errors:
            details = "; ".join(f"#{e['index']}: {e['error']}" for e in errors)
            raise ScryLabError(f"{len(errors)} signal(s) failed: {details}")
        return result.get("signals", [])

    def send_one(self, y, name: str, source_id: str, x, z,
                 y_unit, x_unit, z_unit, overwrite: bool = False) -> list[dict]:
        return self.send([y], [name], source_id, [x], [z],
                         y_unit, x_unit, z_unit, overwrite=overwrite)

    def plot(self, signal_id: str):
        self._post("/api/plot", {"signal_id": signal_id})


_default_client = _Client()
