from dataclasses import dataclass
from functools import cached_property
from typing import Optional, Dict, Set

import requests
from loguru import logger

from work.work import Work


@dataclass
class Preprint(Work):
    repository: Optional[str] = None
    archive_ID: Optional[str] = None
    library_catalog: Optional[str] = None

    @cached_property
    def zotero_itemtype_fields(self) -> Set[str]:
        return {_["field"] for _ in requests.get(
            "https://api.zotero.org/itemTypeFields?itemType=preprint",
            #     headers=headers,
            params={
                "format": "json",
            },
        ).json()}

    def update_with_crossref_item_data(self, data: Optional[Dict]):
        """
        Crossref just does not have preprints
        :param data:
        :return:
        """
        super().update_with_crossref_item_data(data)

    def update_with_DBLP_item_data(self, data: Optional[Dict]):
        super().update_with_DBLP_item_data(data)
        if 'venue' in data:
            if data['venue'] == 'CoRR':
                self.repository = 'arXiv'
            else:
                self.repository = data['venue']
        if 'volume' in data:
            self.archive_ID = data['volume']
            if self.repository == "arXiv":
                self.archive_ID = f"arXiv:{self.archive_ID.split('/')[-1]}"
        if self.repository == "arXiv":
            self.library_catalog = "arXiv.org"

    def update_zotero_item_data(self, data: dict) -> Dict:
        data = super().update_zotero_item_data(data)
        key = data['key']
        if data['itemType'] != 'preprint':
            logger.debug(f"Change itemType from {data['itemType']} to preprint for {key=}")
            for field in set(data.keys()) - self.zotero_fields:
                logger.debug(f"delete field {field=}")
                del data[field]
            for field in self.zotero_fields:
                if field not in data:
                    logger.debug(f"add field {field=}")
                    data[field] = ""
            data["itemType"] = "preprint"

        self._update_zotero_item_key(data, "repository", "repository")
        self._update_zotero_item_key(data, "archiveID", "archive_ID")
        self._update_zotero_item_key(data, "libraryCatalog", "library_catalog")
        return data
