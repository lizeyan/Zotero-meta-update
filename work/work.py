from dataclasses import dataclass
from typing import List, Optional
import requests
from loguru import logger


@dataclass
class Work:
    title: str
    doi: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None

    def lookup(self):
        """
        lookup the current work on databases and fill or correct the fields
        :return:
        """
        pass

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

    @staticmethod
    def search_on_crossref_by_doi(doi: str) -> Optional[dict]:
        try:
            data = requests.get(f"https://api.crossref.org/works/{doi}").json()
            return data
        except Exception as e:
            logger.error(f"search_on_crossref_by_doi {doi} failed: {e}")
        finally:
            return None

    @staticmethod
    def search_on_crossref_by_title(title: str) -> Optional[dict]:
        try:
            data = requests.get(f"https://api.crossref.org/works", params={"query": title}).json()
            return data
        except Exception as e:
            logger.error(f"search_on_crossref_by_doi {doi} failed: {e}")
        finally:
            return None

    @staticmethod
    def search_on_DBLP_by_doi(doi: str) -> Optional[dict]:
        pass  # TODO

    @staticmethod
    def search_on_DBLP_by_title(title: str) -> Optional[dict]:
        pass  # TODO
