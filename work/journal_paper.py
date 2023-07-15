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
        key = self.publication.strip()
        if key in PREFERRED_JOURNAL_ABBR:
            self.journal_abbr = PREFERRED_JOURNAL_ABBR[key]

        data = super().update_zotero_item_data(data)

        self._change_zotero_item_type(data)

        self._update_zotero_item_key(data, "publicationTitle", "publication")
        self._update_zotero_item_key(data, "journalAbbreviation", "journal_abbr")
        self._update_zotero_item_key(data, "volume", "volume")
        self._update_zotero_item_key(data, "issue", "issue")
        self._update_zotero_item_key(data, "pages", "pages")
        return data


PREFERRED_JOURNAL_ABBR = {
    "Proceedings of the VLDB Endowment": "PVLDB",
    "Journal of Systems and Software": "JSS",
    "IEEE Transactions on Software Engineering": "TSE",
    "IEEE Transactions on Parallel and Distributed Systems": "TPDS",
    "ACM Transactions on Software Engineering and Methodology": "TOSEM",
    "IEEE Transactions on Neural Networks and Learning Systems": "TNNLS",
    "IEEE Transactions on Network and Service Management": "TNSM",
    "IEEE Transactions on Knowledge and Data Engineering": "TKDE",
    "IEEE Transactions on Services Computing": "TSC",
    "IEEE/ACM Transactions on Networking": "TON",
}
