import re


# Words that strongly suggest an email is intended for
# privacy/data-rights requests.
STRONG_EMAIL_KEYWORDS = [
    "privacy",
    "privacy request",
    "privacy rights",
    "data protection",
    "data subject",
    "personal data",
    "personal information",
    "delete your data",
    "delete personal data",
    "delete personal information",
    "deletion request",
    "data deletion",
    "erasure",
    "right to erasure",
    "exercise your rights",
    "exercise privacy rights",
]


# Words that suggest a link is a privacy/data request form.
FORM_KEYWORDS = [
    "privacy request",
    "privacy requests",
    "privacy rights",
    "data request",
    "data requests",
    "data subject request",
    "submit a request",
    "request personal data",
    "delete personal data",
    "delete my data",
    "delete your data",
    "data deletion",
    "deletion request",
    "request deletion",
    "exercise your rights",
]


def classify_contacts(emails, links, text):
    """
    Decide whether the privacy policy provides:

        EMAIL
        FORM
        UNKNOWN

    Returns a dictionary containing the classification and
    the evidence used to make the decision.
    """

    email_result = find_privacy_email(emails, text)

    if email_result:
        return {
            "type": "EMAIL",
            "email": email_result["email"],
            "reason": email_result["reason"],
            "score": email_result["score"],
        }

    form_result = find_privacy_form(links)

    if form_result:
        return {
            "type": "FORM",
            "url": form_result["url"],
            "label": form_result["text"],
            "reason": form_result["reason"],
            "score": form_result["score"],
        }

    return {
        "type": "UNKNOWN",
        "reason": (
            "We could not confidently identify a dedicated "
            "privacy or deletion request method."
        ),
        "score": 0,
    }


def find_privacy_email(emails, text):
    """
    Look for an email that appears to be intended for
    privacy/data-rights requests.

    We currently use the email address itself plus the
    surrounding page text.
    """

    if not emails:
        return None

    text_lower = text.lower()

    candidates = []

    for email in emails:
        email_lower = email.lower()

        score = 0
        reasons = []

        # Strong signal from the email address itself.
        if "privacy" in email_lower:
            score += 10
            reasons.append("email address contains 'privacy'")

        if "dpo" in email_lower:
            score += 10
            reasons.append("email address contains 'dpo'")

        if "data.protection" in email_lower:
            score += 10
            reasons.append(
                "email address contains 'data.protection'"
            )

        if "dataprotection" in email_lower:
            score += 10
            reasons.append(
                "email address contains 'dataprotection'"
            )

        # Look for relevant language near the email address.
        context = get_email_context(
            text_lower,
            email_lower,
        )

        for keyword in STRONG_EMAIL_KEYWORDS:
            if keyword in context:
                score += 5
                reasons.append(
                    f"nearby text contains '{keyword}'"
                )

        if score > 0:
            candidates.append(
                {
                    "email": email,
                    "score": score,
                    "reason": "; ".join(reasons),
                }
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda candidate: candidate["score"],
        reverse=True,
    )

    # Conservative threshold.
    if candidates[0]["score"] < 5:
        return None

    return candidates[0]


def get_email_context(text, email, window=500):
    """
    Return text surrounding an email address.
    """

    position = text.find(email)

    if position == -1:
        return ""

    start = max(0, position - window)
    end = min(len(text), position + len(email) + window)

    return text[start:end]


def find_privacy_form(links):
    """
    Find the strongest privacy/data-request link.
    """

    candidates = []

    for link in links:
        text = link.get("text", "")
        url = link.get("url", "")

        combined = f"{text} {url}".lower()

        score = link.get("score", 0)

        reasons = []

        for keyword in FORM_KEYWORDS:
            if keyword in combined:
                score += 5
                reasons.append(
                    f"contains '{keyword}'"
                )

        if score > 0:
            candidates.append(
                {
                    "url": url,
                    "text": text,
                    "score": score,
                    "reason": "; ".join(reasons),
                }
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda candidate: candidate["score"],
        reverse=True,
    )

    # Again, be conservative.
    if candidates[0]["score"] < 5:
        return None

    return candidates[0]
