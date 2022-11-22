from work import ConferencePaper, lookup, JournalPaper, are_doi_equal, Preprint


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
