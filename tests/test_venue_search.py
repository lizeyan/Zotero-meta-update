from work import search_journal_by_openAlex


def test_journal_search_by_openAlex():
    data = search_journal_by_openAlex("IEEE Trans Neural Netw Learn Syst")
    assert data is not None and data["display_name"] == "IEEE transactions on neural networks and learning systems"
    data = search_journal_by_openAlex("ACM Computing Surveys")
    assert data is not None and data["display_name"] == "ACM Computing Surveys"

