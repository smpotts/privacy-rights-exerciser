from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


PRIVACY_KEYWORDS = [
    "privacy",
    "privacy policy",
    "privacy-policy",
    "privacy_policy",
    "data privacy",
]


def find_privacy_policy(html, base_url):
    """
    Look for a likely privacy-policy link on the page.
    Returns the absolute URL or None.
    """

    soup = BeautifulSoup(html, "html.parser")

    candidates = []

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        text = link.get_text(" ", strip=True).lower()

        combined = f"{text} {href.lower()}"

        score = 0

        if "privacy policy" in text:
            score += 10
        elif "privacy" in text:
            score += 5

        if "privacy-policy" in href:
            score += 8
        elif "privacy" in href:
            score += 4

        if score > 0:
            absolute_url = urljoin(base_url, href)

            if is_same_domain(base_url, absolute_url):
                candidates.append((score, absolute_url))

    if not candidates:
        return None

    candidates.sort(reverse=True)

    return candidates[0][1]


def is_same_domain(url1, url2):
    """Only accept privacy links on the same domain."""

    domain1 = urlparse(url1).netloc.lower()
    domain2 = urlparse(url2).netloc.lower()

    # Remove www. so example.com and www.example.com match.
    domain1 = domain1.removeprefix("www.")
    domain2 = domain2.removeprefix("www.")

    return domain1 == domain2
