import json
from datetime import datetime
from pathlib import Path

from pytz import timezone

from zotero.metadata import set_update_time, get_update_time


def test_date_modified():
    root = Path(__file__).parent / "cases"
    with open(root / "7V4PUQCN" / "original.json") as f:
        meta = json.load(f)
    modified_datetime = datetime.now(tz=timezone('Asia/Shanghai')).replace(microsecond=0)
    set_update_time(meta, modified_datetime)
    assert get_update_time(meta) == modified_datetime

    try:
        set_update_time(meta, datetime.now())
        assert False, "datetime without timezone is not checked"
    except RuntimeError:
        assert True
