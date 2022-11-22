import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from click import command, option
from loguru import logger
from pytz import timezone

from zotero import download_items
from zotero.metadata import get_updated_zotero_meta_for_item, get_update_time
from zotero.request import write_metadata_to_zotero


def check_difference(a, b, skip_confirmation: bool) -> bool:
    print(f"itemType: {a['itemType']=:15}, {b['itemType']=:15}")
    print(f"Missing keys:    {set(a.keys()) - set(b.keys())=}")
    print(f"Additional keys: {set(b.keys()) - set(a.keys())=}")
    print(f"Title: {b['title']}")
    nothing_changed = True
    for key in (set(a.keys()) | set(b.keys())) - {'extra', 'dateModified'}:
        if a.get(key, "NaN") != b.get(key, 'NaN'):
            nothing_changed = False
            print(f"{key:10} changed from {a.get(key, 'NaN')!r:10} to {b.get(key, 'NaN')!r:10}")
    if nothing_changed and get_update_time(a) is not None:
        """
        If get_update_time(a) is not None, the original metadata has no mark that it has been updated
        We want to mark it to skip online search in future runs
        """
        logger.info(f"Skip write because nothing changed")
        return False
    if skip_confirmation:
        return True
    choice = input("Skip (s, default) or write to server (w)")
    if choice.lower() == "write" or choice.lower() == "w":
        return True
    else:
        return False


@command("Zotero Metadata Update")
@option(
    "--output-dir", "-o", type=Path, default=Path("./output"),
    help="The downloaded original metadata files and the updated ones will be saved to this directory."
)
@option(
    "--min-update-interval-days", "-d", type=int, default=7,
    help="If an item has been updated in `min-update-interval-days` days, it will be skipped."
)
@option(
    "--skip-download", "-s", is_flag=True, default=False,
    help="If true, we skip download original metadata files from Zotero server."
)
@option(
    "--skip-online-update", is_flag=True, default=False,
    help="If true, we skip update online and just read the newest updated metadata."
)
@option(
    "--write", "-w", is_flag=True, default=False,
    help="If true, we write the updated metadata files to Zotero server."
)
@option(
    "--skip-confirmation", is_flag=True, default=False,
    help="If true, each item would be write to server (only when --write) without confirmation"
)
def main(
        output_dir: Path, min_update_interval_days: int, skip_download: bool, write: bool,
        skip_online_update: bool, skip_confirmation: bool,
):
    logger.add(output_dir / "log.txt", rotation="1 week", retention="1 month")
    logger.info(f"=========================START===============================")
    dt_threshold = datetime.now(timezone("Asia/Shanghai")) - timedelta(days=min_update_interval_days)
    logger.info(f"{dt_threshold=}")
    if not skip_download:
        logger.info("Downloading original metadata files from Zotero server...")
        download_items()
    else:
        logger.info("Skip download original metadata files from Zotero server.")

    paths = output_dir.glob("*")
    # paths = [output_dir / 'D2BLJAUK']  # DEBUG
    failed_items = []

    for item_path in paths:
        if not item_path.is_dir():
            continue
        handler_id = logger.add(item_path / "log.txt", rotation="1 MB", enqueue=True)
        try:
            logger.info(f"========================================================")
            logger.info(f"Processing {item_path}")
            try:
                with open(item_path / "original.json", "r", encoding="utf-8") as f:
                    original_meta = json.load(f)['data']
            except Exception as e:
                logger.error(f"Cannot load {item_path / 'original.json'}: {e}")
                continue
            date_modified: Optional[datetime] = get_update_time(original_meta)
            logger.info(f"item {original_meta['key']} is modified at {date_modified}")
            if date_modified is not None and date_modified > dt_threshold:
                logger.info(f"Skip {item_path.name} since it has been updated recently.")
                continue

            if 'lock' in original_meta.get("extra", ""):
                logger.info(f"Skip item {original_meta['key']} because it is locked: {original_meta['extra']=}")
                continue

            if original_meta["itemType"] == "attachment":
                logger.error(f"Skip {item_path.name} since it is an attachment.")
                continue
            if skip_online_update:
                try:
                    with open(item_path / "updated_meta.json", "r") as f:
                        new_meta = json.load(f)
                    logger.info(f"Read updated metadata from {item_path / 'updated_meta.json'}")
                except Exception as e:
                    logger.error(f"Cannot load {item_path / 'updated_meta.json'}: {e}")
                    new_meta = None
            else:
                logger.info(f"Updating metadata for {item_path.name}")
                new_meta = get_updated_zotero_meta_for_item(original_meta)
            if new_meta is not None:
                with open(item_path / "updated_meta.json", "w+") as f:
                    json.dump(new_meta, f, indent=2)
                with open(item_path / f"updated_meta-{datetime.now().isoformat()}.json", "w+") as f:
                    json.dump(new_meta, f, indent=2)
                confirmation = check_difference(original_meta, new_meta, skip_confirmation=skip_confirmation)
                if write and confirmation:
                    logger.info("Write to server")
                    write_metadata_to_zotero(original_meta['key'], new_meta)
                else:
                    logger.info("Skip writing to server")
            else:
                failed_items.append(item_path)
        except Exception as e:
            logger.exception(f"Exception encountered when processing {item_path=}", exception=e)
            failed_items.append(item_path)
        finally:
            logger.remove(handler_id)
    logger.info(f"failed_items: {failed_items}")
    logger.info(f"=========================START===============================")


if __name__ == '__main__':
    main()
