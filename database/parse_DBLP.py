from typing import Optional, Dict

from loguru import logger

from database.search_item import get_venue_info_on_DBLP, search_journal_by_openAlex
from work import Work, Preprint, JournalPaper, ConferencePaper


def parse_DBLP_item(item: Dict) -> Optional[Work]:
    if item is None:
        return
    title = item.get("title", None).rstrip(" .")
    if "authors" in item:
        if isinstance(item["authors"]["author"], list):
            authors = [author["text"] for author in item["authors"]["author"]]
        else:
            authors = [item["authors"]["author"]['text']]
    else:
        authors = None
    date = item.get("year", None)
    url = item.get("url", None)
    doi = item.get("doi", None)

    if item["type"] == "Conference and Workshop Papers":
        work = ConferencePaper(
            title=title,
            authors=authors,
            date=date,
            url=url,
            doi=doi,
        )
        if "publisher" in item:
            work.publisher = item["publisher"]
        if "venue" in item:
            work.conference_name = f"{item['venue']} {item['year']}"
            work.proceeding_name = f"{item['venue']} {item['year']}"
        venue_info = get_venue_info_on_DBLP("/".join(item["key"].split("/")[:-1]), item["year"])
        if venue_info is not None:
            work.proceeding_name = venue_info["title"]
            work.series = f"{venue_info['booktitle']} {item['year']}"
            work.conference_name = work.series
        if "pages" in item:
            work.pages = item["pages"]
    elif item["type"] == "Journal Articles":
        work = JournalPaper(
            title=title,
            authors=authors,
            date=date,
            url=url,
            doi=doi,
        )
        if "venue" in item:
            work.journal_abbr = item['venue']
            work.publication = item['venue']
        if "volume" in item:
            work.volume = item["volume"]
        if "pages" in item:
            work.pages = item["pages"]
        if "number" in item:
            work.issue = item["number"]
        journal_info = search_journal_by_openAlex(title=work.publication)
        if journal_info is not None:
            if 'display_name' in journal_info:
                work.publication = journal_info['display_name']
            if "alternate_names" in journal_info:
                work.journal_abbr = journal_info["alternate_names"][0]
    elif item["type"] == "Informal Publications" or item["type"] == "Informal and Other Publications":
        work = Preprint(
            title=title,
            authors=authors,
            date=date,
            url=url,
            doi=doi,
        )
        if 'venue' in item:
            if item['venue'] == 'CoRR':
                work.repository = 'arXiv'
            else:
                work.repository = item['venue']
        if 'volume' in item:
            work.archive_ID = item['volume']
            if work.repository == "arXiv":
                work.archive_ID = f"arXiv:{work.archive_ID.split('/')[-1]}"
        if work.repository == "arXiv":
            work.library_catalog = "arXiv.org"
    else:
        logger.error(
            f"Unrecognized type {item.get('type', '')} "
            f"for {item.get('doi', '')=} {item.get('title', 'NaN')=}"
        )
        work = None
    return work