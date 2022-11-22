from typing import Optional
from urllib.parse import urlparse


def are_title_almost_equal(title_a: str, title_b: str) -> bool:
    def is_valid_char(c):
        nums = {
            chr(_) for _ in range(ord('0'), ord('9') + 1)
        }
        alphabets = {
            chr(_) for _ in range(ord('a'), ord('z') + 1)
        }
        return c in nums or c in alphabets

    return tuple(filter(is_valid_char, title_a.lower())) == tuple(filter(is_valid_char, title_b.lower()))


def are_doi_equal(doi_a: Optional[str], doi_b: Optional[str]) -> bool:
    if doi_a is None and doi_b is None:
        return True
    elif doi_a is None or doi_b is None:
        return False
    else:
        return urlparse(doi_a).path.lstrip("/").lower() == urlparse(doi_b).path.lstrip("/").lower()
