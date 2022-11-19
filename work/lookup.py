from typing import Optional

from loguru import logger

from work.conference_paper import ConferencePaper
from work.journal_paper import JournalPaper
from work.search_item import search_on_DBLP_by_title, search_on_crossref_by_title, search_on_crossref_by_doi
from work.work import Work

__all__ = ['lookup']


def create_work_by_crossref_item(crossref_item: dict) -> Optional[Work]:
    if crossref_item["type"] == "proceedings-article":
        work = ConferencePaper()
        work.update_with_crossref_item_data(crossref_item)
        return work
    elif crossref_item["type"] == "journal-article":
        work = JournalPaper()
        work.update_with_crossref_item_data(crossref_item)
        return work
    else:
        logger.error(
            f"Unrecognized type {crossref_item['type']} for {crossref_item['DOI']=} {crossref_item['title']=}"
        )
        return None


def create_work_by_DBLP_item(DBLP_item: dict) -> Optional[Work]:
    if DBLP_item["type"] == "Conference and Workshop Papers":
        work = ConferencePaper()
        work.update_with_DBLP_item_data(DBLP_item)
        return work
    elif DBLP_item["type"] == "Journal Articles":
        work = JournalPaper()
        work.update_with_DBLP_item_data(DBLP_item)
        return work
    else:
        logger.error(
            f"Unrecognized type {DBLP_item['type']} for {DBLP_item['doi']=} {DBLP_item['title']=}"
        )
        return None


def lookup(*, title: Optional[str] = None, doi: Optional[str] = None) -> Optional[Work]:
    """
    lookup the current work on databases and fill or correct the fields
    :return:
    """
    if doi is not None:
        crossref_item = search_on_crossref_by_doi(doi)
        if crossref_item is not None:
            logger.info(f"found item {crossref_item['DOI']=} on crossref for {doi=}")
            return create_work_by_crossref_item(crossref_item)  # 100% matched since DOI matched
        else:
            DBLP_item = search_on_DBLP_by_title(title, doi=doi)
            if DBLP_item is not None:
                logger.info(f"found item {DBLP_item['doi']=} on DBLP for {doi=}")
                return create_work_by_DBLP_item(DBLP_item)  # 100% matched since DOI matched
            else:
                logger.info(f"item not found for {doi=}")
                return None
    else:
        crossref_item = search_on_crossref_by_title(title)
        if crossref_item is not None:
            logger.info(
                f"found item {crossref_item['title']=} {crossref_item.get('DOI', '')=} on crossref for {title=}"
            )
            return create_work_by_crossref_item(crossref_item)
        else:
            DBLP_item = search_on_DBLP_by_title(title)
            if DBLP_item is not None:
                logger.info(
                    f"found item {DBLP_item['title']=} {DBLP_item.get('doi', '')=} on DBLP for {title=}"
                )
                return create_work_by_DBLP_item(DBLP_item)
            else:
                logger.info(f"item not found for {title=}")
                return None
