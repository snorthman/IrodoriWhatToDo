import os
import urllib.request
from importlib.resources import files
from pathlib import Path
from urllib.parse import urlparse


def _cache_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local")
    else:
        base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
    cache = Path(base) / "irodori_whattodo"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


class Resource:
    def __init__(self, uri: str) -> None:
        self.uri = uri

    @property
    def is_url(self) -> bool:
        return urlparse(self.uri).scheme in ("http", "https")

    @property
    def filename(self) -> str:
        ref = urlparse(self.uri).path if self.is_url else self.uri
        return Path(ref).name

    def _download(self) -> Path:
        dest = _cache_dir() / self.filename
        if not dest.exists():
            with urllib.request.urlopen(self.uri) as response:
                dest.write_bytes(response.read())
        return dest

    def _bundled(self) -> Path:
        path = Path(files(__package__).joinpath(self.uri))
        if not path.exists():
            raise FileNotFoundError(f"No bundled resource named {self.uri!r} in package {__package__!r}")
        return path

    @property
    def path(self) -> Path:
        return self._download() if self.is_url else self._bundled()


sentence_pattern_list = Resource("https://www.irodori.jpf.go.jp/assets/data/sentence_patterns_list.xlsx")
irodori_can_do = Resource("https://www.irodori.jpf.go.jp/assets/data/irodori_can-do-jf_can-do_for_life_in_japan.xlsx")
output_claude = Resource("claude_output.json")
