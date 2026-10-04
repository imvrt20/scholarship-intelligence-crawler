from app.discovery import discover_links
from app.crawler import crawl_page
from app.extractor import (
    extract_scholarship,
    extract_multiple_scholarships
)
from app.verifier import verify_scholarship
from app.database import init_db, save_scholarship


# ============================================================
# SOURCES
# ============================================================

SOURCES = [
    {
        "name": "National Scholarship Portal",
        "url": "https://scholarships.gov.in/"
    },
    {
        "name": "UGC",
        "url": "https://www.ugc.gov.in/"
    }
]


# ============================================================
# MAIN CRAWLER
# ============================================================

def main():

    print("=" * 60)
    print("SCHOLARSHIP INTELLIGENCE CRAWLER")
    print("=" * 60)

    # --------------------------------------------------------
    # Initialize database
    # --------------------------------------------------------

    init_db()

    total_extracted = 0
    total_saved = 0
    total_skipped = 0

    # --------------------------------------------------------
    # Process each source
    # --------------------------------------------------------

    for source in SOURCES:

        source_name = source["name"]
        source_url = source["url"]

        print()
        print("=" * 60)
        print("SOURCE:", source_name)
        print("URL:", source_url)
        print("=" * 60)

        # ----------------------------------------------------
        # Discover links
        # ----------------------------------------------------

        try:

            links = discover_links(source_url)

            print("Discovered links:", len(links))

        except Exception as error:

            print("Discovery failed:")
            print(error)

            continue

        # ----------------------------------------------------
        # Crawl discovered pages
        # ----------------------------------------------------

        for url in links:

            print()
            print("-" * 60)
            print("Processing:", url)
            print("-" * 60)

            page = crawl_page(url)

            if not page:

                print("Skipping page because crawling failed.")

                continue

            page_text = page.get("text", "")
            page_html = page.get("html", "")

            # ------------------------------------------------
            # Extract scholarships
            # ------------------------------------------------

            scholarships = []

            # ------------------------------------------------
            # NSP All-Scholarships page
            # ------------------------------------------------

            if "scholarships.gov.in/All-Scholarships" in url:

                scholarships = extract_multiple_scholarships(
                    page_text,
                    url,
                    page_html
                )

            # ------------------------------------------------
            # Other pages
            # ------------------------------------------------

            else:

                scholarship = extract_scholarship(
                    page_text,
                    url
                )

                if scholarship:

                    scholarships = [scholarship]

            # ------------------------------------------------
            # Count extracted records
            # ------------------------------------------------

            total_extracted += len(scholarships)

            print(
                "Scholarships extracted from this page:",
                len(scholarships)
            )

            # ------------------------------------------------
            # Verify and save each scholarship
            # ------------------------------------------------

            for scholarship in scholarships:

                scholarship_name = scholarship.get("name")

                # ==================================================
                # FILTER 1
                # Skip records without a valid scholarship name
                # ==================================================

                if (
                    not scholarship_name
                    or scholarship_name.strip().lower() == "not specified"
                ):

                    print(
                        "Skipping: No valid scholarship name |",
                        url
                    )

                    total_skipped += 1

                    continue

                # ==================================================
                # FILTER 2
                # Skip generic "National Scholarship"
                #
                # These are usually produced by NSP information
                # pages such as:
                #
                # /Students
                # /Fellowship
                # /studentFAQs
                # /student-announcements
                # /home
                # /officers
                # etc.
                #
                # The actual scholarship listings are extracted
                # from /All-Scholarships separately.
                # ==================================================

                if (
                    scholarship_name.strip().lower()
                    == "national scholarship"
                    and
                    "scholarships.gov.in/All-Scholarships" not in url
                ):

                    print(
                        "Skipping: Generic National Scholarship result |",
                        url
                    )

                    total_skipped += 1

                    continue

                # ==================================================
                # VERIFY SCHOLARSHIP
                # ==================================================

                verified = verify_scholarship(
                    scholarship
                )

                # ==================================================
                # SAVE SCHOLARSHIP
                # ==================================================

                saved_id = save_scholarship(
                    verified
                )

                if saved_id:

                    total_saved += 1

                    print(
                        "Saved scholarship:",
                        scholarship_name
                    )

                else:

                    print(
                        "Scholarship was not saved:",
                        scholarship_name
                    )
if __name__ == "__main__":
 main()           
                    

    # ============================================================