from dataclasses import dataclass
from typing import Optional, Dict, ClassVar

from work.work import Work


@dataclass
class JournalPaper(Work):
    zotero_item_type: ClassVar[str] = "journalArticle"
    publication: Optional[str] = None
    journal_abbr: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None

    def update_zotero_item_data(self, data: dict) -> Dict:
        data = super().update_zotero_item_data(data)

        self._change_zotero_item_type(data)

        self._update_zotero_item_key(data, "publicationTitle", "publication")
        self._update_zotero_item_key(data, "journalAbbreviation", "journal_abbr")
        self._update_zotero_item_key(data, "volume", "volume")
        self._update_zotero_item_key(data, "issue", "issue")
        self._update_zotero_item_key(data, "pages", "pages")
        return data
