from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
from typing import List, Optional, Dict, Set

from loguru import logger

from work.utils import are_doi_equal, are_title_almost_equal


@dataclass
class Work:
    title: Optional[str] = None
    doi: Optional[str] = None
    authors: Optional[List[str]] = None
    date: Optional[str] = None
    url: Optional[str] = None

    def copy_from(self, work: Optional["Work"]):
        """
        Copy the values from an existing `Work` object
        :param work:
        :return:
        """
        if work is None:
            return self
        if type(work) != type(self):
            logger.warning(f"Cannot copy from {type(work)} to {type(self)}")
            return self
        for key, value in work.__dict__.items():
            if key in self.__dict__:
                setattr(self, key, value)
        return self

    @cached_property
    def zotero_itemtype_fields(self) -> Set[str]:
        """
        The fields of the item type in Zotero
        :return:
        """
        raise NotImplementedError()

    @property
    def zotero_generic_fields(self) -> Set[str]:
        """
        The fields in all item types in Zotero, which will not occur in `zotero_itemtype_fields`
        :param work:
        :return:
        """
        return {
            'collections',
            'creators',
            'dateAdded',
            'dateModified',
            'itemType',
            'key',
            'relations',
            'tags',
            'version',
        }

    @cached_property
    def zotero_fields(self) -> Set[str]:
        return self.zotero_generic_fields | self.zotero_itemtype_fields

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
        """
        Update the work with the data from Crossref
        :param data: see an example at https://api.crossref.org/works/10.1023/a:1010933404324
        :return:
        """
        if data is None:
            return
        if "title" in data and len(data["title"]) > 0:
            self.title = data["title"][0]
            if "subtitle" in data and len(data["subtitle"]) > 0 and data['subtitle'][0] != "":
                self.title += ": " + data['subtitle'][0]
        if "author" in data:
            self.authors = [
                (
                    author["family"] + ", " + author["given"]
                    if 'given' in author and 'family' in author
                    else (author["family"] if 'family' in author else author['given'])
                )
                for author in data["author"]
            ]
        if "published-print" in data:
            self.date = '-'.join(map(str, data["published-print"]["date-parts"][0]))
        if "URL" in data:
            self.url = data["URL"]
        if "DOI" in data:
            self.doi = data["DOI"]

    def update_with_DBLP_item_data(self, data: Optional[Dict]):
        """
        Update the work with the data from DBLP
        :param data: see an example at "https://dblp.org/search/publ/api?format=json&q=random forest Breiman"
        :return:
        """
        if data is None:
            return
        if "title" in data:
            self.title = data["title"]
        if "authors" in data:
            self.authors = [author["text"] for author in data["authors"]["author"]]
        if "year" in data:
            self.date = data["year"]
        if "url" in data:
            self.url = data["url"]
        if "doi" in data:
            self.doi = data["doi"]

    def update_zotero_item_data(self, data: dict) -> Dict:
        """
        Update the given Zotero metadata dictionary with the data from this work
        :param data: The 'data' section of a Zotero item
        :return: the updated metadata (deepcopyed from the parameter)
        """
        data = deepcopy(data)

        # If DOI mismatched, then the lookup stage is buggy, we should not update the data
        if data.get("DOI", "") != "" and not are_doi_equal(data["DOI"], self.doi):
            if getattr(self, "library_catalog", "") == "arXiv.org" or getattr(self, "repository", "") == 'arXiv':
                # If the item is from arXiv, then DBLP could miss its DOI
                pass
            else:
                raise RuntimeError(f"DOI mismatch: {data['DOI']=} {self.doi=} {data['key']=}. Skip update metadata")
        # If title mismatched, there could be a problem
        if data.get("DOI", "") == "" and not are_title_almost_equal(data["title"], self.title):
            logger.warning(f"Title mismatch: {data['title']=} {self.title=} {data['key']=}.")

        # Update creators
        if "creators" not in data:
            logger.debug(f"creators not in {data['key']=}, create it")
            data["creators"] = []
        new_author_infos = []
        for name in self.authors:
            if ', ' in name:
                new_author_infos.append({
                    "creatorType": "author",
                    "firstName": name.split(", ")[1],
                    "lastName": name.split(", ")[0],
                })
            else:
                new_author_infos.append({
                    "creatorType": "author",
                    "name": name,
                })
        # If the length of the new author list is different from the old one and is not empty, then we will use the new list
        if len(new_author_infos) != len(data["creators"]) and len(new_author_infos) > 0:
            logger.debug(f"update creator from {data['creators']} to {new_author_infos} for {data['key']=}")
            data["creators"] = new_author_infos
        else:
            # If the length of two lists are equal, we will update each different item.
            for idx, (author_info, new_author_info) in enumerate(zip(data["creators"], new_author_infos)):
                if author_info != new_author_info:
                    if 'name' in new_author_info and author_info.get('firstName', "") != "" and author_info.get('lastName', "") != "":
                        logger.info(
                            "Since the author name is not in the format of 'last name, first name', "
                            f"we do not update the author info: {new_author_info=} {author_info=}"
                        )
                    else:
                        logger.info(f"update creators from {author_info} to {new_author_info} for {data['key']=}")
                        data["creators"][idx] = new_author_info

        # Update other fileds
        self._update_zotero_item_key(data, "DOI", "doi")
        self._update_zotero_item_key(data, "title", "title")
        if self.date is not None and self.date not in data.get('date', ""):
            # e.g., self.date is '2016' (on DBLP, only year is recorded) and data['date'] is '2016-11-07'
            self._update_zotero_item_key(data, "date", "date")
        self._update_zotero_item_key(data, "url", "url")
        return data

    def _update_zotero_item_key(self, data: Dict, field_name: str, attr_name: str):
        """
        If self.attr_name is not None and it is not equal to data[field_name], update the data[field_name] with self.attr_name
        :param data:
        :param field_name:
        :param attr_name:
        :return:
        """
        if getattr(self, attr_name) is not None and data.get(field_name, "") != getattr(self, attr_name):
            logger.info(
                f"update {field_name=} from {data.get(field_name, '')} to {getattr(self, attr_name)} for {data['key']=}"
            )
            data[field_name] = getattr(self, attr_name)
