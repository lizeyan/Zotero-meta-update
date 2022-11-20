import json
from datetime import datetime
from functools import lru_cache

__all__ = ['download_items']

from pathlib import Path

from typing import Dict

import requests
from loguru import logger


@lru_cache(maxsize=None)
def zotero_headers() -> dict:
    with open("ZOTERO_API_KEY", 'r') as f:
        return {
            "Zotero-API-Key": f.read(),
            "Zotero-API-Version": "3",
            "Content-Type": "application/json",
        }


@lru_cache(maxsize=None)
def zotero_user_id() -> str:
    with open("ZOTERO_USER_ID", 'r') as f:
        return f.read()


def download_items(output_dir: Path = Path("./output")) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    assert output_dir.is_dir(), f"{output_dir} is not a directory"
    count = 0
    while True:
        items = requests.get(
            f"https://api.zotero.org/users/{zotero_user_id()}/items",
            headers=zotero_headers(),
            params={
                "format": "json",
                "start": f"{count}",
            }
        ).json()
        if len(items) == 0:
            break
        count += len(items)
        for item in items:
            item_output_dir = output_dir / item["key"]
            item_output_dir.mkdir(parents=True, exist_ok=True)
            with open(item_output_dir / "original.json", 'w') as f:
                json.dump(item, f, indent=2)
            with open(item_output_dir / f"original-{datetime.now().isoformat()}.json", 'w+') as f:
                json.dump(item, f, indent=2)
    return count


def write_metadata_to_zotero(key: str, meta_data: Dict):
    logger.info(f"write metadata to {key} {zotero_user_id()=}")
    rsp = requests.put(
        f"https://api.zotero.org/users/{zotero_user_id()}/items/{key}",
        headers=zotero_headers(),
        params={
            "format": "json",
        },
        data=json.dumps(meta_data),
    )
    logger.info(f"Response: {rsp.status_code} {rsp.text}")
    return rsp.status_code
