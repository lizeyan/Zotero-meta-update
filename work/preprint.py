from dataclasses import dataclass
from typing import Optional, Dict, ClassVar

from work.work import Work


@dataclass
class Preprint(Work):
    zotero_item_type: ClassVar[str] = "preprint"
    repository: Optional[str] = None
    archive_ID: Optional[str] = None
    library_catalog: Optional[str] = None

    def update_zotero_item_data(self, data: dict) -> Dict:
        data = super().update_zotero_item_data(data)

        self._change_zotero_item_type(data)

        self._update_zotero_item_key(data, "repository", "repository")
        self._update_zotero_item_key(data, "archiveID", "archive_ID")
        self._update_zotero_item_key(data, "libraryCatalog", "library_catalog")
        return data
