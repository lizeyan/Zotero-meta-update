import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import pytest

from zotero.metadata import get_updated_zotero_meta_for_item


def load_cases() -> List[Tuple[Dict, Optional[Dict]]]:
    root = Path(__file__).parent / "cases"
    rets = []
    for case_path in root.glob("*"):
        with open(case_path / "original.json") as f:
            a = json.load(f)
        try:
            with open(case_path / "updated_meta.json") as f:
                b = json.load(f)
        except FileNotFoundError:
            b = None
        rets.append((a, b))
    return rets


@pytest.mark.parametrize(
    "original_meta,updated_meta", load_cases()
)
def test_update_zotero_meta(original_meta, updated_meta):
    print(original_meta["key"])
    new_meta = get_updated_zotero_meta_for_item(original_meta)
    if "dateModified" in new_meta:
        del new_meta["dateModified"]
    if "dateModified" in updated_meta:
        del updated_meta["dateModified"]
    if "extra" in new_meta:
        del new_meta["extra"]
    if "extra" in updated_meta:
        del updated_meta["extra"]
    if updated_meta is not None:
        assert new_meta is not None and new_meta == updated_meta
    else:
        assert new_meta is None


def test_update_zotero_meta_debug():
    with open("cases/N38EVV4Q/original.json", 'r') as f:
        original_meta = json.load(f)
    with open("cases/N38EVV4Q/updated_meta.json", 'r') as f:
        updated_meta = json.load(f)
    print(original_meta["key"])
    new_meta = get_updated_zotero_meta_for_item(original_meta)
    if "dateModified" in new_meta:
        del new_meta["dateModified"]
    if "dateModified" in updated_meta:
        del updated_meta["dateModified"]
    if "extra" in new_meta:
        del new_meta["extra"]
    if "extra" in updated_meta:
        del updated_meta["extra"]
    if updated_meta is not None:
        assert new_meta is not None and new_meta == updated_meta
    else:
        assert new_meta is None
