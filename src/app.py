import os
from urllib.parse import quote

import streamlit as st

from privacy_rights_exerciser.contact_extractor import extract_privacy_contacts
from privacy_rights_exerciser.decision import classify_contacts
from privacy_rights_exerciser.fetcher import fetch_page
from privacy_rights_exerciser.policy_finder import find_privacy_policy


st.set_page_config(
    page_title="Privacy Rights Exerciser",
    page_icon="🔒",
    layout="centered",
)


def load_email_template():
    """
    Load the privacy deletion email template from a separate text file.
    """

    template_path = os.path.join(
        os.path.dirname(__file__),
        "privacy_rights_exerciser",
        "email_template.txt",
    )

    try:
        with open(template_path, "r", encoding="utf-8") as file:
            return file.read().strip()

    except FileNotFoundError:
        return """Hello,

I am writing to request the deletion of my personal data associated with this email address.

Please treat this as a request to exercise my right to privacy and request deletion of my personal data in accordance with your privacy policy and applicable data protection laws.

Please delete my email address and any personal data associated with it, except where you are legally required to retain it.

Please confirm when the deletion has been completed.

Thank you.
"""


def build_deletion_email(email):
    """
    Build a mailto URL containing the recipient, subject, and
    pre-populated privacy deletion request.
    """

    subject = "Request to Delete Personal Data"
    body = load_email_template()

    return (
        f"mailto:{email}"
        f"?subject={quote(subject)}"
        f"&body={quote(body)}"
    )


def clean_links(links, privacy_url):
    """
    Return useful privacy-request links for display.

    Removes:
    - duplicate URLs
    - generic link text such as "here"
    - links whose visible text is just a URL
    - the privacy policy itself
    """

    ignored_labels = {
        "here",
        "click here",
        "click",
        "this",
        "this link",
        "learn more",
        "read more",
    }

    seen_urls = set()
    cleaned = []

    privacy_url = privacy_url.rstrip("/")

    for link in links:
        url = link.get("url", "").strip()
        label = link.get("text", "").strip()

        if not url:
            continue

        # Don't show the privacy policy again.
        if url.rstrip("/") == privacy_url:
            continue

        # Don't show duplicate URLs.
        if url in seen_urls:
            continue

        # Don't show generic labels.
        if label.lower() in ignored_labels:
            continue

        # Don't show links whose visible text is just the URL.
        if label.startswith(("http://", "https://")):
            continue

        # Don't show empty labels.
        if not label:
            continue

        seen_urls.add(url)

        cleaned.append(
            {
                "label": label,
                "url": url,
            }
        )

    return cleaned


def display_privacy_request(decision):
    """Display the identified privacy request method."""

    st.subheader("Privacy Request")

    st.write(
        "This is the method the website appears to provide "
        "for people who want to exercise their privacy rights."
    )

    if decision["type"] == "EMAIL":

        st.markdown("#### Email")

        st.code(
            decision["email"],
            language=None,
        )

        st.write(
            "This email address appears to be associated "
            "with privacy or personal-data requests."
        )

        mailto_url = build_deletion_email(
            decision["email"]
        )

        st.link_button(
            "Open Email",
            mailto_url,
        )

    elif decision["type"] == "FORM":

        st.markdown("#### Privacy Request Form")

        st.write(
            "The website provides a dedicated page or form "
            "for submitting privacy requests."
        )

        label = decision.get("label") or "Privacy Request Form"

        st.link_button(
            f"Open {label}",
            decision["url"],
        )

    else:

        st.info(
            "We couldn't confidently identify a dedicated "
            "privacy request email address or form."
        )


def display_privacy_policy(privacy_url):
    """Display the privacy policy section."""

    st.subheader("Privacy Policy")

    st.write(
        "This is the privacy policy we used to identify "
        "the website's privacy request options."
    )

    st.link_button(
        "Open Privacy Policy",
        privacy_url,
    )


def display_related_links(links):
    """Display additional links that may help exercise privacy rights."""

    if not links:
        return

    st.subheader("Other Privacy Rights Options")

    st.write(
        "These additional links appear to relate to privacy "
        "rights, personal information, or data requests."
    )

    for link in links:

        st.markdown(
            f"**{link['label']}**"
        )

        st.link_button(
            "Open",
            link["url"],
            key=f"privacy-link-{link['url']}",
        )


st.title("Privacy Rights Exerciser")

st.write(
    "Enter a website and we'll look for its privacy policy "
    "and the options it provides for exercising your privacy rights."
)


st.markdown("#### Website")

url = st.text_input(
    "Website",
    placeholder="example.com",
    label_visibility="collapsed",
)


if st.button(
    "Find Privacy Options",
    type="primary",
    use_container_width=False,
):

    if not url.strip():

        st.error("Please enter a website.")

    else:

        try:

            # -------------------------------------------------
            # Find the privacy policy
            # -------------------------------------------------

            with st.spinner("Finding privacy policy..."):

                html, final_url = fetch_page(url)

                privacy_url = find_privacy_policy(
                    html,
                    final_url,
                )

            if not privacy_url:

                st.warning(
                    "We couldn't find a privacy policy "
                    "on this website."
                )

            else:

                # -------------------------------------------------
                # Analyze the privacy policy
                # -------------------------------------------------

                with st.spinner("Analyzing privacy policy..."):

                    policy_html, policy_final_url = fetch_page(
                        privacy_url
                    )

                    contacts = extract_privacy_contacts(
                        policy_html,
                        policy_final_url,
                    )

                    decision = classify_contacts(
                        contacts["emails"],
                        contacts["links"],
                        contacts["text"],
                    )

                # -------------------------------------------------
                # Display results
                # -------------------------------------------------

                st.divider()

                display_privacy_request(
                    decision
                )

                st.divider()

                display_privacy_policy(
                    policy_final_url
                )

                related_links = clean_links(
                    contacts["links"],
                    policy_final_url,
                )

                if related_links:

                    st.divider()

                    display_related_links(
                        related_links
                    )

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )