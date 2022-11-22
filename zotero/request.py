import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache

__all__ = ['download_items', 'write_metadata_to_zotero']

from pathlib import Path

from typing import Dict, List

import requests
from loguru import logger
from requests.adapters import HTTPAdapter, Retry, Response

_session = requests.Session()
_adapter = HTTPAdapter(
    max_retries=Retry(
        total=10, backoff_factor=1, allowed_methods=None, status_forcelist=[429, 500, 502, 503, 504]
    )
)
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)


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


def download_items(output_dir: Path = Path("./output"), *, limit: int = 100, n_workers: int = 16) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    assert output_dir.is_dir(), f"{output_dir} is not a directory"
    count = 0
    dt = datetime.now()

    def query(start: int) -> Response:
        return _session.get(
            f"https://api.zotero.org/users/{zotero_user_id()}/items",
            headers=zotero_headers(),
            params={
                "format": "json",
                "start": f"{start}",
                "limit": f"{limit}",
            }
        )

    def process_items(items: List[Dict]):
        nonlocal count
        count += len(items)
        logger.info(f"{count}/{total_counts}={count / total_counts * 100:.2f}% fetched")
        for item in items:
            if item["data"]["itemType"] == "attachment":
                continue
            item_output_dir = output_dir / item["key"]
            item_output_dir.mkdir(parents=True, exist_ok=True)
            with open(item_output_dir / "original.json", 'w') as f:
                json.dump(item, f, indent=2)
            with open(item_output_dir / f"original-{dt.isoformat()}.json", 'w+') as f:
                json.dump(item, f, indent=2)

    first_response: Response = query(start=0)
    total_counts: int = int(first_response.headers.get("Total-Results"))
    logger.info(f"The total number of items: {total_counts}")

    process_items(first_response.json())

    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        executor.map(lambda _start: process_items(query(_start).json()), range(count, total_counts, limit))

    assert count == total_counts, f"{count=} {total_counts=}"
    return count


def write_metadata_to_zotero(key: str, meta_data: Dict):
    logger.info(f"write metadata to {key} {zotero_user_id()=}")
    rsp = _session.put(
        f"https://api.zotero.org/users/{zotero_user_id()}/items/{key}",
        headers=zotero_headers(),
        params={
            "format": "json",
        },
        data=json.dumps(meta_data),
    )
    logger.info(f"Response: {rsp.status_code} {rsp.text}")
    return rsp.status_code
