import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import pytest

from update_zotero_meta import update_zotero_meta_for_item


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
    new_meta = update_zotero_meta_for_item(original_meta)
    if updated_meta is not None:
        assert new_meta is not None and new_meta == updated_meta
    else:
        assert new_meta is None

