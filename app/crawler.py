import requests
from bs4 import BeautifulSoup


def crawl_page(url):
    """
    Crawl a webpage and return:
    - URL
    - Page title
    - Clean readable text
    - Raw HTML
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        print("Crawling:", url)

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        # Detect the correct encoding
        response.encoding = response.apparent_encoding

        # Keep original HTML
        raw_html = response.text

        # Parse HTML
        soup = BeautifulSoup(
            raw_html,
            "lxml"
        )

        # Remove unnecessary elements
        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "svg"
            ]
        ):
            element.decompose()

        # Get page title
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        else:
            title = ""

        # Extract readable text
        text = soup.get_text(
            separator=" ",
            strip=True
        )

        # Return all crawler information
        return {
            "url": url,
            "title": title,
            "text": text,
            "html": raw_html
        }

    except requests.exceptions.Timeout:
        print("Crawling failed: Request timed out")
        return None

    except requests.exceptions.HTTPError as error:
        print("Crawling failed: HTTP error")
        print(error)
        return None

    except requests.exceptions.ConnectionError:
        print("Crawling failed: Connection error")
        return None

    except requests.RequestException as error:
        print("Crawling failed:")
        print(error)
        return None

    except Exception as error:
        print("Unexpected crawling error:")
        print(error)
        return None


# ============================================
# TEST
# ============================================

if __name__ == "__main__":

    test_url = "https://scholarships.gov.in/All-Scholarships"

    print("=" * 70)
    print("CRAWLER TEST")
    print("=" * 70)

    page = crawl_page(test_url)

    if page:

        print("\n✓ PAGE CRAWLED SUCCESSFULLY")

        print("\nURL:")
        print(page["url"])

        print("\nTITLE:")
        print(page["title"])

        print("\nTEXT LENGTH:")
        print(len(page["text"]))

        print("\nHTML LENGTH:")
        print(len(page["html"]))

        print("\nFIRST 500 CHARACTERS OF TEXT:")
        print("-" * 70)
        print(page["text"][:500])

        print("\n" + "=" * 70)
        print("CRAWLER TEST PASSED")
        print("=" * 70)

    else:

        print("\n✗ CRAWLER TEST FAILED")