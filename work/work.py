from dataclasses import dataclass
from functools import cached_property
from typing import List, Optional, Dict, Set

from work.search_item import search_on_DBLP_by_title, search_on_crossref_by_title, search_on_crossref_by_doi


@dataclass
class Work:
    title: Optional[str] = None
    doi: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None

    @cached_property
    def zotero_item_fields(self) -> Set[str]:
        raise NotImplementedError()

    def is_preprint(self) -> bool:
        """
        :return:  whether the work is a pre-print version
        """
        is_arxiv = self.doi is not None and 'arXiv' in self.doi
        return is_arxiv

    def formal_publish_doi(self) -> Optional[str]:
        """
        :return:
        """
        if not self.is_preprint():
            return self.doi
        else:
            raise NotImplementedError()  # TODO

    def update_with_crossref_item_data(self, data: Optional[Dict]):
        if data is None:
            return
        if "title" in data:
            self.title = data["title"][0]
        if "author" in data:
            self.authors = [author["given"] + " " + author["family"] for author in data["author"]]
        if "published-print" in data:
            self.year = data["published-print"]["date-parts"][0][0]
        if "publisher" in data:
            self.publisher = data["publisher"]
        if "URL" in data:
            self.url = data["URL"]
        if "DOI" in data:
            self.doi = data["DOI"]

    def update_with_DBLP_item_data(self, data: Optional[Dict]):
        if data is None:
            return
        if "title" in data:
            self.title = data["title"]
        if "authors" in data:
            self.authors = [author["text"] for author in data["authors"]["author"]]
        if "year" in data:
            self.year = data["year"]
        if "publisher" in data:
            self.publisher = data["publisher"]
        if "url" in data:
            self.url = data["url"]
        if "doi" in data:
            self.doi = data["doi"]
