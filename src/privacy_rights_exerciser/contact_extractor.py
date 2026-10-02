import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PRIVACY_KEYWORDS = [
    "privacy",
    "personal data",
    "personal information",
    "data protection",
    "delete",
    "deletion",
    "erase",
    "erasure",
    "remove",
]


def extract_privacy_contacts(html, base_url):
    """
    Extract candidate email addresses and links from a privacy page.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Remove things that aren't useful for analyzing the page.
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    text = soup.get_text(" ", strip=True)

    emails = extract_emails(text)
    links = extract_privacy_links(soup, base_url)

    return {
        "emails": emails,
        "links": links,
    }


def extract_emails(text):
    """
    Find email addresses in page text.
    """

    emails = EMAIL_PATTERN.findall(text)

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(emails))


def extract_privacy_links(soup, base_url):
    """
    Find links that appear relevant to privacy/data requests.
    """

    results = []

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        text = link.get_text(" ", strip=True)

        combined = f"{text} {href}".lower()

        score = 0

        if "privacy" in combined:
            score += 5

        if "delete" in combined:
            score += 5

        if "deletion" in combined:
            score += 5

        if "personal data" in combined:
            score += 3

        if "personal information" in combined:
            score += 3

        if "data request" in combined:
            score += 5

        if "privacy request" in combined:
            score += 7

        if score > 0:
            results.append(
                {
                    "text": text,
                    "url": urljoin(base_url, href),
                    "score": score,
                }
            )

    results.sort(key=lambda item: item["score"], reverse=True)

    return results
