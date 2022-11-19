import pytest

from work import ConferencePaper
from work.search_item import search_on_crossref_by_title, search_on_DBLP_by_title


@pytest.mark.parametrize(
    "title,doi", [
        (
                "Diagnosing Performance Issues in Microservices with Heterogeneous Data Source",
                "10.1109/ISPA-BDCloud-SocialCom-SustainCom52081.2021.00074",
        ),
        (
                "Robust KPI Anomaly Detection for Large-Scale Software Services with Partial Labels",
                "10.1109/ISSRE52982.2021.00023",
        ),
        (
                "Dynamic Application Call Graph Formation and Service Identification in Cloud Data Centers",
                "10.1109/TNSM.2022.3201095",
        ),
        (
                "Gandalf: An Intelligent, {End-To-End} Analytics Service for Safe Deployment in {Large-Scale} Cloud Infrastructure",
                None,
        ),
    ]
)
def test_search_with_title_crossref(title, doi):
    def is_doi_equal(a, b):
        return a.lower().endswith(b.lower())

    data = search_on_crossref_by_title(title)
    if doi is not None:
        assert data is not None and is_doi_equal(data["DOI"], doi)
    else:
        assert data is None


@pytest.mark.parametrize(
    "title,doi", [
        (
                "Diagnosing Performance Issues in Microservices with Heterogeneous Data Source",
                "10.1109/ISPA-BDCloud-SocialCom-SustainCom52081.2021.00074",
        ),
        (
                "Robust KPI Anomaly Detection for Large-Scale Software Services with Partial Labels",
                "10.1109/ISSRE52982.2021.00023",
        ),
        (
                "Dynamic Application Call Graph Formation and Service Identification in Cloud Data Centers",
                None,
        ),
    ]
)
def test_search_with_title_DBLP(title, doi):
    def is_doi_equal(a, b):
        return a.lower().endswith(b.lower())

    data = search_on_DBLP_by_title(title)
    if doi is not None:
        assert data is not None and is_doi_equal(data["doi"], doi)
    else:
        assert data is None


@pytest.mark.parametrize(
    "title,url", [
        (
                "Gandalf: An Intelligent, {End-To-End} Analytics Service for Safe Deployment in {Large-Scale} Cloud Infrastructure",
                "https://dblp.org/rec/conf/nsdi/LiCHDHSYLWLC20",
        ),
    ]
)
def test_search_with_title_DBLP_no_doi(title, url):
    def is_doi_equal(a, b):
        return a.lower().endswith(b.lower())

    data = search_on_DBLP_by_title(title)
    if url is not None:
        assert data is not None and is_doi_equal(data["url"], url)
    else:
        assert data is None
