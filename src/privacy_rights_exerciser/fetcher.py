from urllib.parse import urlparse

import requests


USER_AGENT = (
    "Mozilla/5.0 (compatible; PrivacyHelper/0.1; "
    "+http://localhost:5000)"
)


def normalize_url(url):
    """Make sure the URL has a scheme."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    if not parsed.netloc:
        raise ValueError("That doesn't appear to be a valid website.")

    return url


def fetch_page(url):
    """Download a webpage and return (html, final_url)."""
    url = normalize_url(url)

    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=10,
        allow_redirects=True,
    )

    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "text/html" not in content_type:
        raise ValueError("The website did not return an HTML page.")

    return response.text, response.url
