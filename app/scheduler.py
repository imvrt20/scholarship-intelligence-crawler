import time
from datetime import datetime

from app.main import main


def run_scheduler(interval_hours=24):
    """
    Runs the scholarship crawler repeatedly.

    Default:
    Runs once every 24 hours.
    """

    interval_seconds = interval_hours * 60 * 60

    print("=" * 70)
    print("SCHOLARSHIP INTELLIGENCE SCHEDULER")
    print("=" * 70)

    print(f"Scheduler started.")
    print(f"Crawler will run every {interval_hours} hours.")

    while True:

        print("\n")
        print("=" * 70)
        print("STARTING SCHEDULED CRAWL")
        print("=" * 70)

        print(
            "Time:",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        try:
            main()

        except Exception as e:
            print("\nCrawler error:")
            print(e)

        print("\n")
        print("=" * 70)
        print("CRAWL COMPLETED")
        print("=" * 70)

        print(
            f"Next crawl in {interval_hours} hours..."
        )

        time.sleep(interval_seconds)


if __name__ == "__main__":
    run_scheduler(24)