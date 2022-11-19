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


def are_doi_equal(doi_a: str, doi_b: str) -> bool:
    return urlparse(doi_a).path.lstrip("/") == urlparse(doi_b).path.lstrip("/")
