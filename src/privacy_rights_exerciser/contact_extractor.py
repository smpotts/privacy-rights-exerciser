import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PRIVACY_REQUEST_KEYWORDS = (
    "privacy request",
    "privacy requests",
    "privacy rights",
    "your privacy rights",
    "my privacy rights",
    "data subject request",
    "data subject rights",
    "data request",
    "data requests",
    "personal data request",
    "personal information request",
    "delete my data",
    "delete your data",
    "delete personal data",
    "delete personal information",
    "request deletion",
    "deletion request",
    "data deletion",
    "right to erasure",
    "erasure request",
    "exercise your rights",
)


def extract_privacy_contacts(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    text = soup.get_text(" ", strip=True)

    return {
        "text": text,
        "emails": extract_emails(text),
        "links": extract_privacy_links(soup, base_url),
    }


def extract_emails(text):
    emails = EMAIL_PATTERN.findall(text)
    return list(dict.fromkeys(emails))


def extract_privacy_links(soup, base_url):
    """Extract privacy-related web links, excluding email links."""

    links = []

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        text = link.get_text(" ", strip=True)

        if href.lower().startswith("mailto:"):
            continue

        if EMAIL_PATTERN.search(href) or EMAIL_PATTERN.search(text):
            continue

        url = urljoin(base_url, href)

        if url.lower().startswith("mailto:"):
            continue

        if EMAIL_PATTERN.search(url):
            continue

        searchable_text = f"{text} {href}".lower()

        if not any(
            keyword in searchable_text
            for keyword in PRIVACY_REQUEST_KEYWORDS
        ):
            continue

        links.append(
            {
                "text": text,
                "url": url,
            }
        )

    return links