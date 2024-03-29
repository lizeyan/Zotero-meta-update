from work import ConferencePaper, JournalPaper, are_doi_equal, Preprint
from database import lookup


def test_lookup_1():
    work = lookup(title='TraceCRL: contrastive representation learning for microservice trace analysis')
    assert isinstance(work, ConferencePaper)
    assert work.authors == [
        'Zhang, Chenxi', 'Peng, Xin', 'Zhou, Tong', 'Sha, Chaofeng', 'Yan, Zhenghui', 'Chen, Yiru', 'Yang, Hong',
    ]
    assert work.series == "ESEC/FSE '22"
    assert work.proceeding_name == 'Proceedings of the 30th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering'
    assert work.conference_name == "ESEC/FSE '22: 30th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering"
    print(work)


def test_lookup_2():
    work = lookup(title='Adaptive Performance Anomaly Detection for Online Service Systems via Pattern Sketching')
    assert isinstance(work, ConferencePaper)
    assert work.authors == [
        'Chen, Zhuangbin', 'Liu, Jinyang', 'Su, Yuxin', 'Zhang, Hongyu', 'Ling, Xiao',
        'Yang, Yongqiang', 'Lyu, Michael R.'
    ]
    assert work.series == "ICSE '22"
    assert work.proceeding_name == 'Proceedings of the 44th International Conference on Software Engineering'
    assert work.conference_name == "ICSE '22: 44th International Conference on Software Engineering"
    print(work)


def test_lookup_3():
    work = lookup(
        title='CableMon: Improving the Reliability of Cable Broadband Networks via Proactive Network Maintenance')
    assert isinstance(work, ConferencePaper)
    assert work.doi is None
    assert work.authors == ['Jiyao Hu', 'Zhenyu Zhou', 'Xiaowei Yang 0001', 'Jacob Malone', 'Jonathan W. Williams']
    assert work.proceeding_name == "17th USENIX Symposium on Networked Systems Design and Implementation, NSDI 2020, Santa Clara, CA, USA, February 25-27, 2020."
    assert work.conference_name == "NSDI 2020"
    print(work)


def test_lookup_4():
    work = lookup(
        title='Anomaly Detection and Failure Root Cause Analysis in (Micro) Service-Based Cloud Applications: A Survey')
    print(work)
    assert isinstance(work, JournalPaper)
    assert are_doi_equal(work.doi, 'http://dx.doi.org/10.1145/3501297')
    assert work.authors == ['Soldani, Jacopo', 'Brogi, Antonio']
    assert work.publication == "ACM Computing Surveys"
    assert work.journal_abbr == "ACM Comput. Surv."
    assert work.volume == "55"
    assert work.issue == "3"
    assert work.pages == "1-39"
    print(work)


def test_lookup_5():
    work = lookup(title="B-MEG: Bottlenecked-Microservices Extraction Using Graph Neural Networks")
    print(work)
    assert isinstance(work, ConferencePaper)
    assert are_doi_equal(work.doi, 'https://doi.org/10.1145/3491204.3527494')
    assert work.authors == ['Somashekar, Gagan', 'Dutt, Anurag', 'Vaddavalli, Rohith', 'Varanasi, Sai Bhargav',
                            'Gandhi, Anshul']
    assert work.conference_name == "ICPE '22: ACM/SPEC International Conference on Performance Engineering"
    assert work.proceeding_name == "Companion of the 2022 ACM/SPEC International Conference on Performance Engineering"
    assert work.series == "ICPE '22"


def test_lookup_6():
    work = lookup(doi='http://dx.doi.org/10.1145/3501297')
    print(work)
    assert isinstance(work, JournalPaper)
    assert are_doi_equal(work.doi, 'http://dx.doi.org/10.1145/3501297')
    assert work.authors == ['Soldani, Jacopo', 'Brogi, Antonio']
    assert work.publication == "ACM Computing Surveys"
    assert work.journal_abbr == "ACM Comput. Surv."
    assert work.volume == "55"
    assert work.issue == "3"
    assert work.pages == "1-39"
    print(work)


def test_lookup_7():
    work = lookup(
        title="The Life and Death of SSDs and HDDs: Similarities, Differences, and Prediction Models",
        doi="10.48550/arXiv.2012.12373"
    )
    print(work)
    assert isinstance(work, Preprint)
    assert work.authors == ['Riccardo Pinciroli', 'Lishan Yang', 'Jacob Alter', 'Evgenia Smirni']
    assert work.repository == "arXiv"
    assert work.archive_ID == 'arXiv:2012.12373'


def test_lookup_8():
    work = lookup(
        title='Robust and Explainable Autoencoders for Unsupervised Time Series Outlier Detection—Extended Version'
    )
    print(work)
    assert isinstance(work, Preprint)
    assert are_doi_equal(work.doi, '10.48550/ARXIV.2204.03341')
    assert work.repository == 'arXiv'
    assert work.archive_ID == 'arXiv:2204.03341'


def test_lookup_9():
    work = lookup(
        title='Threshold compression for 3G scalable monitoring'
    )
    print(work)
    assert isinstance(work, ConferencePaper)
    assert work.authors == ['Lee, Suk-Bok', 'Dan Pei', 'Hajiaghayi, MohammadTaghi', 'Pefkianakis, Ioannis', 'Songwu Lu',
                            'He Yan', 'Zihui Ge', 'Yates, Jennifer', 'Kosseifi, Mario']
    assert work.series == "INFOCOM 2012"


def test_lookup_10():
    work = lookup(title="Software Engineering Meets Deep Learning: A Literature Review")
    print(work)
    assert isinstance(work, Preprint)
    assert work.archive_ID == 'arXiv:1909.11436'
    assert work.authors == ['Fabio Ferreira', 'Luciana Lourdes Silva', 'Marco Túlio Valente']


def test_lookup_11():
    work = lookup(title="Topic-sensitive PageRank: a context-sensitive ranking algorithm for Web search")
    print(work)
    assert isinstance(work, JournalPaper)
    assert work.authors == ['Haveliwala, T.H.']
    assert work.doi == '10.1109/tkde.2003.1208999'


def test_lookup_12():
    work = lookup(title="SEEDB: Efﬁcient Data-Driven Visualization Recommendations to Support Visual Analytics")
    print(work)
    assert isinstance(work, JournalPaper)
    assert work.publication == 'Proc. VLDB Endow.'
    assert work.doi == '10.14778/2831360.2831371'


def test_lookup_13():
    work = lookup(
        title="G-RCA: a generic root cause analysis platform for service quality management in large IP networks",
        extra_info={"item_type": "conferencePaper"}
    )
    print(work)
    assert isinstance(work, ConferencePaper)
    assert work.doi == "10.1145/1921168.1921175"

    work = lookup(
        title="G-RCA: a generic root cause analysis platform for service quality management in large IP networks",
        extra_info={"item_type": "journalArticle"}
    )
    print(work)
    assert isinstance(work, JournalPaper)
    assert work.doi == "10.1109/tnet.2012.2188837"


def test_lookup_14():
    work = lookup(
        title="CloudRCA: A Root Cause Analysis Framework for Cloud Computing Platforms",
        extra_info={"item_type": "conferencePaper"}
    )
    print(work)
    assert isinstance(work, ConferencePaper)
    assert work.proceeding_name == "Proceedings of the 30th ACM International Conference on Information and Knowledge Management"
