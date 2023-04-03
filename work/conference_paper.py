from dataclasses import dataclass
from typing import Optional, Dict, ClassVar

from work.work import Work


@dataclass
class ConferencePaper(Work):
    zotero_item_type: ClassVar[str] = "conferencePaper"
    conference_name: Optional[str] = None
    proceeding_name: Optional[str] = None
    location: Optional[str] = None
    series: Optional[str] = None
    publisher: Optional[str] = None
    pages: Optional[str] = None

    def update_zotero_item_data(self, data: dict) -> Dict:
        data = super().update_zotero_item_data(data)

        self._change_zotero_item_type(data)

        self._update_zotero_item_key(data, "conferenceName", "conference_name")
        self._update_zotero_item_key(data, "publisher", "publisher")
        self._update_zotero_item_key(data, "proceedingsTitle", "proceeding_name")
        self._update_zotero_item_key(data, "place", "location")
        self._update_zotero_item_key(data, "series", "series")
        self._update_zotero_item_key(data, "pages", "pages")
        return data
