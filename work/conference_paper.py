from dataclasses import dataclass
from datetime import datetime, timezone
from functools import cached_property
from typing import Optional, Dict, Set

import requests
from loguru import logger

from work.search_item import get_venue_info_on_DBLP
from work.work import Work


@dataclass
class ConferencePaper(Work):
    conference_name: Optional[str] = None
    proceeding_name: Optional[str] = None
    location: Optional[str] = None
    series: Optional[str] = None
    publisher: Optional[str] = None
    pages: Optional[str] = None

    @cached_property
    def zotero_itemtype_fields(self) -> Set[str]:
        return {_["field"] for _ in requests.get(
            "https://api.zotero.org/itemTypeFields?itemType=conferencePaper",
            #     headers=headers,
            params={
                "format": "json",
            },
        ).json()}

    def update_with_crossref_item_data(self, data: Optional[Dict]):
        super().update_with_crossref_item_data(data)
        if "publisher" in data:
            self.publisher = data["publisher"]
        if 'container-title' in data:
            self.proceeding_name = data['container-title'][0]
        if 'event' in data:
            self.conference_name = data['event']['name']
            if 'acronym' in data['event']:
                self.series = data['event']['acronym']
            if 'location' in data['event']:
                self.location = data['event']['location']

    def update_with_DBLP_item_data(self, data: Optional[Dict]):
        super().update_with_DBLP_item_data(data)
        if "publisher" in data:
            self.publisher = data["publisher"]
        if "venue" in data:
            self.conference_name = f"{data['venue']} {data['year']}"
            self.proceeding_name = f"{data['venue']} {data['year']}"
        venue_info = get_venue_info_on_DBLP("/".join(data["key"].split("/")[:-1]), data["year"])
        if venue_info is not None:
            self.proceeding_name = venue_info["title"]
            self.series = f"{venue_info['booktitle']} {data['year']}"
            self.conference_name = self.series
        if "pages" in data:
            self.pages = data["pages"]

    def update_zotero_item_data(self, data: dict) -> Dict:
        data = super().update_zotero_item_data(data)
        key = data['key']
        if data['itemType'] != 'conferencePaper':
            logger.debug(f"Change itemType from {data['itemType']} to conferencePaper for {key=}")
            for field in set(data.keys()) - self.zotero_fields:
                logger.debug(f"delete field {field=}")
                del data[field]
            for field in self.zotero_fields:
                if field not in data:
                    logger.debug(f"add field {field=}")
                    data[field] = ""
            data["itemType"] = "conferencePaper"

        self._update_zotero_item_key(data, "conferenceName", "conference_name")
        self._update_zotero_item_key(data, "publisher", "publisher")
        self._update_zotero_item_key(data, "proceedingsTitle", "proceeding_name")
        self._update_zotero_item_key(data, "place", "location")
        self._update_zotero_item_key(data, "series", "series")
        self._update_zotero_item_key(data, "pages", "pages")
        return data
