from work import are_doi_equal


def test_are_doi_equal():
    assert are_doi_equal('10.1109/UCC48980.2020.00054', '10.1109/UCC48980.2020.00054')
    assert are_doi_equal('10.1109/UCC48980.2020.00054', '10.1109/ucc48980.2020.00054')
    assert not are_doi_equal('10.1109/UCC48980.2020.00054', None)
    assert not are_doi_equal(None, '10.1109/ucc48980.2020.00054')
    assert are_doi_equal(None, None)
