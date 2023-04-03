import copy
from copy import deepcopy
from dataclasses import dataclass
from typing import List, Optional, Dict, Set, ClassVar

import requests
from loguru import logger

from work.work_utils import are_doi_equal, are_title_almost_equal


@dataclass
class Work:
    zotero_item_type: ClassVar[str] = "NotImplemented"
    title: Optional[str] = None
    doi: Optional[str] = None
    authors: Optional[List[str]] = None
    date: Optional[str] = None
    url: Optional[str] = None

    def copy_from(self, work: Optional["Work"], ignore_type: bool = False):
        """
        Copy the values from an existing `Work` object
        :param work:
        :param ignore_type: allow to copy from a different type of work
        :return:
        """
        if work is None:
            return self
        if type(work) != type(self) and not ignore_type:
            logger.warning(f"Cannot copy from {type(work)} to {type(self)}")
            return self
        for key, value in work.__dict__.items():
            if key in self.__dict__:
                setattr(self, key, value)
        return self

    def update_from(self, work: Optional["Work"]):
        if work is None:
            return self
        for key in self.__dict__.keys():
            if key in work.__dict__:
                value = getattr(work, key)
                if value is not None:
                    setattr(self, key, value)

    @classmethod
    def zotero_itemtype_fields(cls) -> Set[str]:
        """
        The fields of the item type in Zotero
        :return:
        """
        return {_["field"] for _ in requests.get(
            f"https://api.zotero.org/itemTypeFields?itemType={cls.zotero_item_type}",
            #     headers=headers,
            params={
                "format": "json",
            },
        ).json()}

    @classmethod
    def zotero_generic_fields(cls) -> Set[str]:
        """
        The fields in all item types in Zotero, which will not occur in `zotero_itemtype_fields`
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

    @classmethod
    def zotero_fields(cls) -> Set[str]:
        return cls.zotero_generic_fields() | cls.zotero_itemtype_fields()

    def is_preprint(self) -> bool:
        """
        :return:  whether the work is a pre-print version
        """
        is_arxiv = self.doi is not None and 'arXiv' in self.doi
        return is_arxiv

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
                    if 'name' in new_author_info and author_info.get('firstName', "") != "" and author_info.get(
                            'lastName', "") != "":
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

    def _change_zotero_item_type(self, data: Dict):
        logger.debug(f"Change itemType from {data['itemType']} to {self.zotero_item_type} for key={data['key']}")
        logger.debug(f"\tOriginal fields: {sorted(data.keys())}")
        logger.debug(f"\tTarget fields: {sorted(self.zotero_fields())}")
        for field in set(data.keys()) - self.zotero_fields():
            logger.debug(f"delete field {field=}")
            del data[field]
        for field in self.zotero_fields():
            if field not in data:
                logger.debug(f"add field {field=}")
                data[field] = ""
        data["itemType"] = self.zotero_item_type
        return data


def merge_works(works: List[Optional["Work"]]) -> Optional["Work"]:
    """
    Merge works by substituting the item values in order. Use the last one's type.
    :param works:
    :return:
    """
    works = list(filter(lambda _: _ is not None, works))
    if len(works) == 0:
        return None
    ret_work = copy.deepcopy(works[-1])
    for work in works:
        ret_work.update_from(work)
    return ret_work
