import json
import xml.etree.ElementTree as ET
from functools import lru_cache
from io import StringIO
from typing import Optional

import requests
from loguru import logger
from requests.adapters import HTTPAdapter, Retry
from functools import wraps
from work.work_utils import are_title_almost_equal, are_doi_equal

_session = requests.Session()
_adapter = HTTPAdapter(
    max_retries=Retry(
        total=10, backoff_factor=1, allowed_methods=None, status_forcelist=[429, 500, 502, 503, 504]
    )
)
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)


def replace_escape_character(func):
    def replace_escape_character_(data):
        if isinstance(data, str):
            data = data.replace("&amp;", "and")
        elif isinstance(data, dict):
            for key in data:
                data[key] = replace_escape_character_(data[key])
        elif isinstance(data, list):
            for i, item in enumerate(data):
                data[i] = replace_escape_character_(item)
        return data

    @wraps(func)
    def new_func(*args, **kwargs):
        return replace_escape_character_(func(*args, **kwargs))

    return new_func


@lru_cache(maxsize=None)
@replace_escape_character
def search_on_crossref_by_doi(doi: str) -> Optional[dict]:
    logger.debug(f"search_on_crossref_by_doi {doi=}")
    try:
        data = _session.get(f"https://api.crossref.org/works/{doi}").json()
        return data["message"]
    except Exception as e:
        logger.error(f"search_on_crossref_by_doi {doi} failed: {e}")
        return None


@lru_cache(maxsize=None)
@replace_escape_character
def search_on_crossref_by_title(title: str, item_type: Optional[str] = None) -> Optional[dict]:
    """
    This function is called only when DOI is missing, so DOI is not a parameter here.
    :param title:
    :param item_type:
    :return:
    """
    logger.debug(f"search_on_crossref_by_title {title=}")
    item_type = translate_Zotero_item_type_to_CrossRef(item_type)
    try:
        data = _session.get(
            f"https://api.crossref.org/works", params={
                "query": title,
            }
        ).json()
        possible_items = []
        for item in data["message"]["items"]:
            if are_title_almost_equal(
                    item.get("title", [""])[0], title
            ) or are_title_almost_equal(
                item.get("title", [""])[0] + item.get("subtitle", [""])[0], title
            ):
                possible_items.append(item)
        if len(possible_items) == 0:
            return None
        elif len(possible_items) == 1:
            return possible_items[0]
        else:
            if item_type is not None:
                item_type_matched_items = [_ for _ in possible_items if _["type"] == item_type]
                if len(item_type_matched_items) == 1:
                    logger.info(
                        f"The item type is matched, use it. {item_type=}. "
                        f"Item types of all items: {[_.get('type', '') for _ in possible_items]}."
                    )
                    return item_type_matched_items[0]
            logger.error(
                f"I do not know how to select the possible items for {title=}:"
                f" \n{json.dumps(possible_items, indent=2)}"
            )
            return None
    except Exception as e:
        logger.error(f"search_on_crossref_by_title {title} failed: {e}")
        return None


@lru_cache(maxsize=None)
@replace_escape_character
def search_on_DBLP_by_title(
        title: str, *, doi: Optional[str] = None, first_author: Optional[str] = None,
        item_type: Optional[str] = None,
) -> Optional[dict]:
    """
    :param title:
    :param doi: Use DOI to determine which is the correct search result
    :param first_author: Use first author as additional search terms when title is not enough
    :param item_type: Use item type to select the correct search result
    :return:
    """
    logger.debug(f"search_on_DBLP_by_title {title=} {doi=}")
    item_type = translate_Zotero_item_type_to_DBLP(item_type)
    try:
        data = _session.get(
            f"https://dblp.org/search/publ/api", params={
                "q": title,
                "format": "json",
            }
        ).json()
        possible_items = []
        for item in data["result"]["hits"]["hit"]:
            info = item["info"]
            title_matched = are_title_almost_equal(info["title"], title)
            doi_matched = are_doi_equal(info.get("doi", ""), doi if doi is not None else "NaN")
            if (doi is None and title_matched) or doi_matched:
                possible_items.append(info)
            if info.get('venue', "") == 'CoRR' and title_matched:
                # For arXiv papers, DBLP can miss their DOIs
                possible_items.append(info)
        if len(possible_items) == 0:
            if first_author is not None and first_author != "":
                # If nothing found with only title, search with first author
                logger.debug(f"search_on_DBLP_by_title {title=} {doi=} with {first_author=}")
                data = _session.get(
                    f"https://dblp.org/search/publ/api", params={
                        "q": f"{title} {first_author}",
                        "format": "json",
                    }
                ).json()
                possible_items = []
                for item in data["result"]["hits"]["hit"]:
                    info = item["info"]
                    title_matched = are_title_almost_equal(info["title"], title)
                    doi_matched = are_doi_equal(info.get("doi", ""), doi if doi is not None else "NaN")
                    if (doi is None and title_matched) or doi_matched:
                        possible_items.append(info)
        if len(possible_items) == 0:
            logger.debug(f"Nothing fond for {title=} {doi=} in DBLP")
            return None
        elif len(possible_items) == 1:
            return possible_items[0]
        else:
            formal_possible_items = [_ for _ in possible_items if _['type'] != "Informal Publications"]
            if len(formal_possible_items) == 1:  # If there is only one formal publication, use it
                logger.info(
                    "There is only one formal publication, use it."
                    f"\n\tThe DOI of other items: {[_.get('doi', '') for _ in possible_items[1:]]}."
                    f"\n\tThe key of other items: {[_.get('key', '') for _ in possible_items[1:]]}."
                )
                return formal_possible_items[0]
            # if all has the same key, use the first item
            if all([
                are_doi_equal(_.get("key", ""), possible_items[0].get("key", "notFound"))
                for _ in possible_items
            ]):
                logger.info(
                    f"The keys are all the same, use the first item."
                )
                return possible_items[0]
            # if all has the same doi, use the first item
            if all([
                are_doi_equal(_.get("doi", ""), possible_items[0].get("doi", "notFound"))
                for _ in possible_items
            ]):
                logger.info(
                    f"The DOIs are all the same, use the first item."
                )
                return possible_items[0]
            if item_type is not None:
                item_type_matched_items = [_ for _ in possible_items if _["type"] == item_type]
                if len(item_type_matched_items) == 1:
                    logger.info(
                        f"The item type is matched, use it. {item_type=}. "
                        f"Item types of all items: {[_.get('type', '') for _ in possible_items]}."
                    )
                    return item_type_matched_items[0]
            logger.error(
                f"I do not know how to select the possible items for {title=}:"
                f" \n{json.dumps(possible_items, indent=2)}"
            )
            return None
    except Exception as e:
        logger.error(f"search_on_DBLP_by_title {title} failed: {e}")
        return None


@lru_cache(maxsize=None)
@replace_escape_character
def get_venue_info_on_DBLP(key: str, year: str):
    logger.debug(f"get_venue_info_on_DBLP {key=} {year=}")
    try:
        # noinspection PyTypeChecker
        venue_tree = ET.parse(StringIO(_session.get(
            f"https://dblp.org/rec/{key}/{year}.xml"
        ).content.decode("utf-8")))
        return {
            "title": venue_tree.getroot()[0].find("title").text,
            "booktitle": venue_tree.getroot()[0].find('booktitle').text,
        }
    except Exception as e:
        logger.error(f"Get venue info failed: {e}")
    return None


@lru_cache(maxsize=None)
@replace_escape_character
def search_journal_by_openAlex(title: str):
    logger.debug(f"search_journal_by_openAlex {title=}")
    try:
        # noinspection PyTypeChecker
        data = _session.get(
            "https://api.openalex.org/journals",
            params={"search": title},
        ).json()
        for item in data["results"]:
            if are_title_almost_equal(
                    title, item.get("display_name", "")
            ) or are_title_almost_equal(
                title, item.get("alternate_titles", [""])[0]
            ) or are_title_almost_equal(
                title, item.get("abbreviated_title", "")
            ):
                return item
    except Exception as e:
        logger.error(f"Get journal info failed: {e}")
    return None


def translate_Zotero_item_type_to_DBLP(item_type: Optional[str]) -> Optional[str]:
    if item_type is None:
        return None
    if item_type.lower() == 'preprint'.lower():
        return None
    elif item_type.lower() == 'conferencePaper'.lower():
        return "Conference and Workshop Papers"
    elif item_type.lower() == 'journalArticle'.lower():
        return "Journal Articles"
    else:
        return None


def translate_Zotero_item_type_to_CrossRef(item_type: Optional[str]) -> Optional[str]:
    if item_type is None:
        return None
    if item_type.lower() == 'preprint'.lower():
        return None
    elif item_type.lower() == 'conferencePaper'.lower():
        return "proceedings-article"
    elif item_type.lower() == 'journalArticle'.lower():
        return "journal-article"
    else:
        return None
