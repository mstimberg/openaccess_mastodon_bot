"""
Finds DOIs, or URLs that correspond to DOIs in an HTML string (e.g. mastodon
post).
"""
import os
import logging
from html.parser import HTMLParser
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__file__)

CROSSREF_API = "https://api.crossref.org/works/{doi}/agency"
UNPAYWALL_API = "https://api.unpaywall.org/v2/{doi}"
EMAIL = os.environ.get("EMAIL", None)


class ExtractTargetsHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.targets.append(attr[1])

    def get_targets(self):
        return self.targets


class ExtractMetaTagsHTMLParser(HTMLParser):
    """Extract the meta tags from the headers of a page"""

    def __init__(self):
        super().__init__()
        self.meta_tags = {}

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            if attrs[0][0] == "name" and attrs[1][0] == "content":
                self.meta_tags[attrs[0][1]] = attrs[1][1]

    def get_meta_tags(self):
        return self.meta_tags


def find_dois(text: str):
    parser = ExtractTargetsHTMLParser()
    parser.feed(text)
    targets = parser.get_targets()
    dois = []
    for target in targets:
        parsed_url = urlparse(target)
        if parsed_url.netloc in ["doi.org", "dx.doi.org"]:
            # The URL is a DOI URL
            dois.append(parsed_url.path[1:])
        else:
            #  try to find a DOI in the meta tags of the page
            r = requests.get(target)
            if r.status_code == requests.codes.ok:
                page_parser = ExtractMetaTagsHTMLParser()
                page_parser.feed(r.text)
                meta_tags = page_parser.get_meta_tags()
                if "citation_doi" in meta_tags:
                    doi = meta_tags["citation_doi"]
                    logger.debug(f"Found DOI {doi} in meta tags of page")
                    dois.append(doi)
    logger.debug(f"Found {len(dois)} DOIs.")
    return dois


def is_datacite_doi(doi: str):
    """Returns True if this is a DataCite DOI. These URLs are not included in
    Unpaywall, but can be considered open access."""
    r = requests.get(CROSSREF_API.format(doi=doi), params={"mailto": EMAIL})
    if r.status_code == requests.codes.ok:
        response = r.json()
        if (
            response["status"] == "ok"
            and response["message"]["agency"]["id"] == "datacite"
        ):
            return True
    return False


def annotate_doi(doi: str):
    """
    Ask Unpaywall for additional information for the doi
    """
    article_info = {"orig_doi": doi}
    # DataCite DOIs are always considered open access (e.g arXiv)
    if is_datacite_doi(doi):
        article_info["is_oa"] = True
        logger.debug(f"DOI {doi} is DataCite, so it is considered open access.")
        return article_info

    # For all other DOIs, ask Unpaywall
    r = requests.get(UNPAYWALL_API.format(doi=doi), params={"email": EMAIL})

    if r.status_code == requests.codes.ok:
        article = r.json()
        if not article["is_oa"]:
            # Unpaywall does not know of any OA version
            article_info["is_oa"] = False
            logging.debug(f"Unpaywall does not know any OA version for DOI {doi}.")
            return article_info
        if (
            article["best_oa_location"]["url"].lower()
            == "https://doi.org/" + doi.lower()
            or article["best_oa_location"]["url_for_landing_page"].lower()
            == "https://doi.org/" + doi.lower()
        ):
            # the DOI is already OA
            article_info["is_oa"] = True
            logger.debug(f"DOI {doi} is already open access.")
        else:
            # the DOI is not OA, but there is an OA version
            article_info["is_oa"] = False
            best_oa_url = article["best_oa_location"].get(
                "url_for_landing_page", article["best_oa_location"]["url"]
            )
            if article["best_oa_location"]["version"] == "submittedVersion":
                article_info["oa_type"] = "preprint"
            elif article["best_oa_location"]["version"] in [
                "publishedVersion",
                "acceptedVersion",
            ]:
                article_info["oa_type"] = "postprint"
            else:
                logger.warning(
                    "*** UNKNOWN TYPE ***", article["best_oa_location"]["version"]
                )
                article_info["oa_type"] = None
            article_info["oa_url"] = best_oa_url
            article_info["title"] = article["title"]
            article_info["journal"] = article["journal_name"]
            article_info["year"] = article["year"]
            authors = [a["family"] for a in article["z_authors"]]
            article_info["authors"] = authors
            logger.debug(
                f"DOI {doi} is not open access, "
                f"but there is an OA version at {best_oa_url}."
            )
    else:
        logger.warning(f"Unpaywall returned {r.status_code} for DOI {doi}")
    return article_info


def annotate_dois(dois: list[str]):
    """
    Return a dictionary with additional information for each DOI:
    open: boolean indicating whether the DOI is open access
    if open is False, additionally gives:
    best_oa: an URL for the best open access version (if available)
    oa_type: the type of open access (preprint/postprint)
    """
    return [annotate_doi(doi) for doi in dois]
