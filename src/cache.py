from pathlib import Path
import json
import os
from typing import Union, Dict, List


class Cache:
    PATH = Path(__file__).resolve().parent.parent / "cache"

    @classmethod
    def store(cls, cache_name: str, data: Union[Dict, List]):
        filename = cls.PATH / f"{cache_name}.json"
        os.makedirs(filename.parent, exist_ok=True)
        filename.write_text(json.dumps(data))

    @classmethod
    def load(cls, cache_name: str):
        filename = cls.PATH / f"{cache_name}.json"
        return json.loads(filename.read_text())
