from typing import Optional, Dict

from loguru import logger

from database import parse_DBLP_item, parse_crossref_item
from database.search_item import search_on_DBLP_by_title, search_on_crossref_by_title, search_on_crossref_by_doi
from work.conference_paper import ConferencePaper
from work.journal_paper import JournalPaper
from work.preprint import Preprint
from work.work import Work

__all__ = ['lookup']

from work import merge_works


def create_or_update_work_by_crossref_item(crossref_item: dict, orig_work: Optional[Work] = None) -> Optional[Work]:
    if crossref_item["type"] == "proceedings-article":
        work = ConferencePaper().copy_from(orig_work)
        work.update_with_crossref_item_data(crossref_item)
        return work
    elif crossref_item["type"] == "journal-article":
        work = JournalPaper().copy_from(orig_work)
        work.update_with_crossref_item_data(crossref_item)
        return work
    else:
        logger.error(
            f"Unrecognized type {crossref_item['type']} for {crossref_item['DOI']=} {crossref_item['title']=}"
        )
        return orig_work


def create_or_update_work_by_DBLP_item(DBLP_item: dict, orig_work: Optional[Work] = None) -> Optional[Work]:
    if DBLP_item["type"] == "Conference and Workshop Papers":
        work = ConferencePaper().copy_from(orig_work)
        work.update_with_DBLP_item_data(DBLP_item)
        return work
    elif DBLP_item["type"] == "Journal Articles":
        work = JournalPaper().copy_from(orig_work)
        work.update_with_DBLP_item_data(DBLP_item)
        return work
    elif DBLP_item["type"] == "Informal Publications" or DBLP_item["type"] == "Informal and Other Publications":
        work = Preprint().copy_from(orig_work)
        work.update_with_DBLP_item_data(DBLP_item)
        return work
    else:
        logger.error(
            f"Unrecognized type {DBLP_item.get('type', '')} "
            f"for {DBLP_item.get('doi', '')=} {DBLP_item.get('title', 'NaN')=}"
        )
        return orig_work


def lookup(
        *, title: Optional[str] = None, doi: Optional[str] = None, extra_info: Optional[Dict] = None
) -> Optional[Work]:
    """
    lookup the current work on databases and fill or correct the fields
    We first match items with DOI, then with title
    If there are no matched items, we will try to search with first author name as well.
    If there are multiple matched items,
    - we will first try to use the formal publication (if there is only one)
    - if all of them have the same DOI or DBLP key, we use the first one.
    - finally we use the item that have the same item type with the original meta (if there is only one)
    :return:
    """
    if extra_info is None:
        extra_info = {}
    if title == "":
        title = None
    if doi == "":
        doi = None
    if title is None and doi is None:
        logger.error("title and doi are both None")
        return None
    if title is not None:
        # Sometimes the extracted title would contain non-ascii characters, which would cause the search to fail
        title = title.replace("ﬁ", "fi")
    if doi is not None:
        work = merge_works([
            parse_DBLP_item(
                search_on_DBLP_by_title(
                    title, doi=doi,
                    first_author=extra_info.get("first_author", None),
                    item_type=extra_info.get("item_type", None),
                )
            ),
            parse_crossref_item(search_on_crossref_by_doi(doi, )),
        ])
    else:
        work = merge_works([
            parse_DBLP_item(
                search_on_DBLP_by_title(
                    title,
                    first_author=extra_info.get("first_author", None),
                    item_type=extra_info.get("item_type", None),
                )
            ),
            parse_crossref_item(search_on_crossref_by_title(
                title,
                item_type=extra_info.get("item_type", None),
            )),
        ])
    return work
