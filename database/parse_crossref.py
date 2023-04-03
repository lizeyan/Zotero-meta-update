from typing import Dict, Optional, List

from loguru import logger

from work import Work, ConferencePaper, JournalPaper

__all__ = ["parse_crossref_item"]


def _get_title(item):
    if "title" in item and len(item["title"]) > 0:
        title = item["title"][0].rstrip(". ")
        if "subtitle" in item and len(item["subtitle"]) > 0 and item['subtitle'][0] != "":
            title += ": " + item['subtitle'][0].rstrip(". ")
    else:
        title = None

    return title


def _get_authors(item):
    if "author" in item:
        authors = [
            (
                author["family"] + ", " + author["given"]
                if 'given' in author and 'family' in author
                else (author["family"] if 'family' in author else author['given'])
            )
            for author in item["author"]
        ]
    else:
        authors = None
    return authors


def parse_crossref_item(item: Dict) -> Optional[Work]:
    if item is None:
        return

    title: Optional[str] = _get_title(item)

    authors: Optional[List[str]] = _get_authors(item)

    if "published-print" in item:
        date = '-'.join(map(str, item["published-print"]["date-parts"][0]))
    else:
        date = None

    if "URL" in item:
        url = item["URL"]
    else:
        url = None

    if "DOI" in item:
        doi = item["DOI"]
    else:
        doi = None

    if item["type"] == "proceedings-article":
        work = ConferencePaper(
            title=title,
            authors=authors,
            date=date,
            url=url,
            doi=doi,
        )
        work.publisher = item.get("publisher", None)
        if 'container-title' in item:
            work.proceeding_name = item['container-title'][0]
        if 'event' in item:
            work.conference_name = item['event']['name']
            if 'acronym' in item['event']:
                work.series = item['event']['acronym']
            if 'location' in item['event']:
                work.location = item['event']['location']
    elif item["type"] == "journal-article":
        work = JournalPaper(
            title=title,
            authors=authors,
            date=date,
            url=url,
            doi=doi,
        )
        if 'container-title' in item:
            work.publication = item['container-title'][0]
        if 'short-container-title' in item and len(item['short-container-title']) > 0:
            work.journal_abbr = item['short-container-title'][0]
        if "volume" in item:
            work.volume = item["volume"]
        if "page" in item:
            work.pages = item["page"]
        if "journal-issue" in item:
            if "issue" in item["journal-issue"]:
                work.issue = item["journal-issue"]["issue"]
    else:
        logger.error(
            f"Unrecognized type {item['type']} for {item['DOI']=} {item['title']=}"
        )
        work = None
    return work
