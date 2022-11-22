from datetime import datetime
from typing import Dict, Optional, List

from loguru import logger
from pytz import timezone

from work import lookup


__all__ = ['get_updated_zotero_meta_for_item', "get_update_time", "set_update_time"]


def get_updated_zotero_meta_for_item(original_meta: Dict) -> Optional[Dict]:
    extra_info = {}
    if "creator" in original_meta and len(original_meta["creator"]) > 0:
        if 'name' in original_meta["creator"][0]:
            extra_info["first_author"] = original_meta["creator"][0]["name"]
        elif 'lastName' in original_meta["creator"][0]:
            extra_info["first_author"] = f"{original_meta['creator'][0]['lastName']}"
    work = lookup(
        title=original_meta.get('title', None),
        doi=original_meta.get("DOI", None),
        extra_info=extra_info,
    )
    if work is not None:
        new_meta = work.update_zotero_item_data(original_meta)
        set_update_time(new_meta)
        return new_meta
    else:
        logger.error(f"Cannot find {original_meta.get('title', None)=} {original_meta.get('DOI', None)=}")
        return None


def set_update_time(meta_data: Dict, dt: Optional[datetime] = None):
    if dt is None:
        dt = datetime.now(tz=timezone('Asia/Shanghai'))
    if dt.tzinfo is None:
        raise RuntimeError(f"{dt=} should be timezone-aware")
    extra = meta_data.get("extra", "").splitlines()
    ret_lines = []
    matched_existing_line = False
    for line in extra:
        if line.startswith("[ZMU-dateModified]"):
            matched_existing_line = True
            ret_lines.append(f"{EXTRA_MODIFIED_DATETIME}{dt.isoformat(timespec='seconds')}")
        else:
            ret_lines.append(line)
    if not matched_existing_line:
        ret_lines.append(f"{EXTRA_MODIFIED_DATETIME}{dt.isoformat(timespec='seconds')}")
    meta_data['extra'] = '\n'.join(ret_lines)
    meta_data['dateModified'] = dt.astimezone(timezone("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
    return meta_data


def get_update_time(meta_data: Dict) -> Optional[datetime]:
    extra: List[str] = meta_data.get("extra", "").splitlines()
    for line in extra:
        if line.startswith(EXTRA_MODIFIED_DATETIME):
            dt = datetime.fromisoformat(line.split(EXTRA_MODIFIED_DATETIME)[1])
            return dt
    return None


EXTRA_MODIFIED_DATETIME = "[ZMU-dateModified]"
