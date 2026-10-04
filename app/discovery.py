import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag

from app.config import USER_AGENT, REQUEST_TIMEOUT


def is_same_domain(source_url, target_url):
    """
    Allow links only from the same official domain.
    """

    source_domain = urlparse(source_url).netloc.lower()
    target_domain = urlparse(target_url).netloc.lower()

    return (
        target_domain == source_domain
        or target_domain.endswith("." + source_domain)
    )


def is_unwanted_url(url):
    """
    Ignore files and technical/navigation URLs that are
    unlikely to contain scholarship information.
    """

    url_lower = url.lower()
    unwanted_paths = [
        "/applicationform",
        "/otrappllication",
        "/scholarshipeligibility",
        "/login",
        "/logout",
        "/register",
        "/signin"
    ]

    for path in unwanted_paths:
        if path in url_lower:
            return True

    unwanted_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".webp",
        ".css",
        ".js",
        ".xml",
        ".zip",
        ".rar",
        ".mp3",
        ".mp4",
        ".avi",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx"
    ]

    for extension in unwanted_extensions:
        if url_lower.endswith(extension):
            return True

    unwanted_parts = [
        "login",
        "logout",
        "signin",
        "signup",
        "register",
        "privacy",
        "terms",
        "contact",
        "feedback",
        "sitemap",
        "javascript:",
        "mailto:"
    ]

    for part in unwanted_parts:
        if part in url_lower:
            return True

    return False


def calculate_link_score(link_text, url):
    """
    Give a score to a link based on scholarship-related
    words found in its text and URL.
    """

    combined = (
        link_text.lower()
        + " "
        + url.lower()
    )

    score = 0

    # Strong scholarship indicators
    strong_keywords = [
        "scholarship",
        "scholarships",
        "fellowship",
        "fellowships",
        "financial assistance",
        "financial aid",
        "student scholarship",
        "education scholarship"
    ]

    # Medium indicators
    medium_keywords = [
        "apply",
        "application",
        "eligibility",
        "stipend",
        "award",
        "grant",
        "student aid",
        "student support",
        "education grant"
    ]

    # Weak indicators
    weak_keywords = [
        "student",
        "education",
        "scheme",
        "benefit"
    ]

    for keyword in strong_keywords:
        if keyword in combined:
            score += 3

    for keyword in medium_keywords:
        if keyword in combined:
            score += 2

    for keyword in weak_keywords:
        if keyword in combined:
            score += 1

    return score


def discover_links(source_url):
    """
    Discover high-quality scholarship-related links
    from an official source page.
    """

    headers = {
        "User-Agent": USER_AGENT
    }

    try:

        print("\n→ Discovering links from:")
        print(source_url)

        response = requests.get(
            source_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "lxml"
        )

        discovered = []
        seen = set()

        for link in soup.find_all("a", href=True):

            # -------------------------------------------------
            # GET LINK TEXT
            # -------------------------------------------------

            link_text = link.get_text(
                " ",
                strip=True
            )

            href = link.get("href")

            if not href:
                continue

            # -------------------------------------------------
            # BUILD FULL URL
            # -------------------------------------------------

            full_url = urljoin(
                source_url,
                href
            )
            if is_unwanted_url(full_url):
                continue

            # Remove #fragment
            full_url, _ = urldefrag(full_url)

            # -------------------------------------------------
            # BASIC URL VALIDATION
            # -------------------------------------------------

            parsed = urlparse(full_url)

            if parsed.scheme not in [
                "http",
                "https"
            ]:
                continue

            # Only official/source domain
            if not is_same_domain(
                source_url,
                full_url
            ):
                continue

            # Remove unwanted files/pages
            if is_unwanted_url(full_url):
                continue

            # Avoid duplicates
            if full_url in seen:
                continue

            # -------------------------------------------------
            # CALCULATE SCHOLARSHIP SCORE
            # -------------------------------------------------

            score = calculate_link_score(
                link_text,
                full_url
            )

            # Require meaningful scholarship relevance
            if score < 3:
                continue

            seen.add(full_url)

            discovered.append(
                {
                    "url": full_url,
                    "text": link_text,
                    "score": score
                }
            )

        # -----------------------------------------------------
        # SORT BY RELEVANCE
        # -----------------------------------------------------

        discovered.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # -----------------------------------------------------
        # RETURN ONLY URLS
        # -----------------------------------------------------

        urls = [
            item["url"]
            for item in discovered
        ]

        print(
            f"✓ Discovered {len(urls)} "
            f"high-quality scholarship links"
        )

        # Show first 20 links for debugging
        print("\nTop discovered links:")

        for index, item in enumerate(
            discovered[:20],
            start=1
        ):

            print(
                f"{index}. "
                f"[Score {item['score']}] "
                f"{item['url']}"
            )

        return urls

    except Exception as e:

        print(
            f"✗ Discovery failed for {source_url}"
        )

        print(e)

        return []


# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    test_url = (
        "https://scholarships.gov.in/"
    )

    results = discover_links(
        test_url
    )

    print("\n")
    print("=" * 70)
    print("DISCOVERY TEST COMPLETED")
    print("=" * 70)

    print(
        "Total links:",
        len(results)
    )