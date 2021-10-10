from pathlib import Path
import json
import os
from typing import Union, Dict, List


class Cache:
    PATH = Path(__file__).resolve().parent.parent / "cache"

    @classmethod
    def exists(cls, cache_name: str):
        return (cls.PATH / f"{cache_name}.json").exists()

    @classmethod
    def store(cls, cache_name: str, data: Union[Dict, List]):
        filename = cls.PATH / f"{cache_name}.json"
        print("cache storing", filename)
        os.makedirs(filename.parent, exist_ok=True)
        filename.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, cache_name: str):
        filename = cls.PATH / f"{cache_name}.json"
        return json.loads(filename.read_text())
