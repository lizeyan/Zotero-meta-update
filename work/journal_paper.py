from dataclasses import dataclass
from functools import cached_property
from typing import Optional, Dict, Set

import requests
from loguru import logger

from work.search_item import search_journal_by_openAlex
from work.work import Work


@dataclass
class JournalPaper(Work):
    publication: Optional[str] = None
    journal_abbr: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None

    @cached_property
    def zotero_itemtype_fields(self) -> Set[str]:
        return {_["field"] for _ in requests.get(
            "https://api.zotero.org/itemTypeFields?itemType=journalArticle",
            #     headers=headers,
            params={
                "format": "json",
            },
        ).json()}

    def update_with_crossref_item_data(self, data: Optional[Dict]):
        super().update_with_crossref_item_data(data)
        if 'container-title' in data:
            self.publication = data['container-title'][0]
        if 'short-container-title' in data and len(data['short-container-title']) > 0:
            self.journal_abbr = data['short-container-title'][0]
        if "volume" in data:
            self.volume = data["volume"]
        if "page" in data:
            self.pages = data["page"]
        if "journal-issue" in data:
            if "issue" in data["journal-issue"]:
                self.issue = data["journal-issue"]["issue"]

    def update_with_DBLP_item_data(self, data: Optional[Dict]):
        super().update_with_DBLP_item_data(data)
        if "venue" in data:
            self.journal_abbr = data['venue']
            self.publication = data['venue']
        if "volume" in data:
            self.volume = data["volume"]
        if "pages" in data:
            self.pages = data["pages"]
        if "number" in data:
            self.issue = data["number"]
        journal_info = search_journal_by_openAlex(title=self.publication)
        if journal_info is not None:
            if 'display_name' in journal_info:
                self.publication = journal_info['display_name']
            if "alternate_names" in journal_info:
                self.journal_abbr = journal_info["alternate_names"][0]

    def update_zotero_item_data(self, data: dict) -> Dict:
        data = super().update_zotero_item_data(data)
        key = data['key']
        if data['itemType'] != 'journalArticle':
            logger.debug(f"Change itemType from {data['itemType']} to journalArticle for {key=}")
            for field in set(data.keys()) - self.zotero_fields:
                logger.debug(f"delete field {field=}")
                del data[field]
            for field in self.zotero_fields:
                if field not in data:
                    logger.debug(f"add field {field=}")
                    data[field] = ""
            data['itemType'] = 'journalArticle'

        self._update_zotero_item_key(data, "publicationTitle", "publication")
        self._update_zotero_item_key(data, "journalAbbreviation", "journal_abbr")
        self._update_zotero_item_key(data, "volume", "volume")
        self._update_zotero_item_key(data, "issue", "issue")
        self._update_zotero_item_key(data, "pages", "pages")
        return data
