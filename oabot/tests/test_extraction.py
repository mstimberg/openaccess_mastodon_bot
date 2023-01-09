from oabot.extract import find_dois, annotate_dois


def test_parsing_with_single_doi():
    """Test that we can parse a string with a DOI in it"""
    text = "A DOI <a href='https://doi.org/10.48550/arXiv.2012.08973'>link</a>"
    dois = find_dois(text)
    assert len(dois) == 1
    assert dois[0] == "10.48550/arXiv.2012.08973"


def test_parsing_with_multiple_dois():
    """Test that we can parse a string with several DOIs in it"""
    text = """A DOI <a href='https://doi.org/10.48550/arXiv.2012.08973'>link</a>.
              Here's another one
              <a href='https://dx.doi.org/10.1016/S1474-4422(21)00074-0'>using 
              outdated syntax</a>.
           """
    dois = find_dois(text)
    assert len(dois) == 2
    assert dois[0] == "10.48550/arXiv.2012.08973"
    assert dois[1] == "10.1016/S1474-4422(21)00074-0"


def test_parsing_with_urls():
    """Test that we can extract dois from URLs that have corresponding meta tags
    in their headers"""
    text = """An <a href='https://arxiv.org/abs/2012.08973'>arXiv URL</a>.
              Here's a link to a
              <a href='https://www.nature.com/articles/s42256-020-0182-5'> 
              Nature Machine Intelligence</a> article.
           """
    dois = find_dois(text)
    assert len(dois) == 2
    assert dois[0] == "10.48550/arXiv.2012.08973"
    assert dois[1] == "10.1038/s42256-020-0182-5"


def test_unpaywall():
    dois = [
        "10.48550/arXiv.2012.08973",  # arXiv == DataCite DOI
        "10.1016/S1474-4422(21)00074-0",  # Open Access
        "10.1016/j.tics.2021.03.018",  # Closed Access with arXiv preprint
    ]
    annotated = annotate_dois(dois)
    assert len(annotated) == 3
    assert len(annotated[0]) == 2
    assert annotated[0]["is_oa"]
    assert annotated[0]["orig_doi"] == "10.48550/arXiv.2012.08973"
    assert len(annotated[1]) == 2
    assert annotated[1]["is_oa"]
    assert annotated[1]["orig_doi"] == "10.1016/S1474-4422(21)00074-0"
    assert not annotated[2]["is_oa"]
    assert annotated[2]["orig_doi"] == "10.1016/j.tics.2021.03.018"
    assert annotated[2]["oa_type"] == "preprint"
    assert annotated[2]["oa_url"] == "http://arxiv.org/abs/2012.08973"
