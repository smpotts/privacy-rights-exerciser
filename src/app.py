from flask import Flask, render_template, request
from privacy_rights_exerciser.fetcher import fetch_page
from privacy_rights_exerciser.policy_finder import find_privacy_policy
from privacy_rights_exerciser.contact_extractor import extract_privacy_contacts


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        url = request.form.get("url", "").strip()

        if not url:
            error = "Please enter a website."
        else:
            try:
                # Step 1: Fetch the website
                html, final_url = fetch_page(url)

                # Step 2: Find the privacy policy
                privacy_url = find_privacy_policy(
                    html,
                    final_url,
                )

                if not privacy_url:
                    result = {
                        "input_url": url,
                        "final_url": final_url,
                        "privacy_url": None,
                        "emails": [],
                        "links": [],
                    }

                else:
                    # Step 3: Fetch the privacy policy
                    policy_html, policy_final_url = fetch_page(
                        privacy_url
                    )

                    # Step 4: Extract candidate emails and links
                    contacts = extract_privacy_contacts(
                        policy_html,
                        policy_final_url,
                    )

                    result = {
                        "input_url": url,
                        "final_url": final_url,
                        "privacy_url": policy_final_url,
                        "emails": contacts["emails"],
                        "links": contacts["links"],
                    }

            except Exception as e:
                error = str(e)

    return render_template(
        "index.html",
        result=result,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
