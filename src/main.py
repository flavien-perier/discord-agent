from __future__ import annotations

import asyncio
import logging
import os
import sys

from . import monitor


def main() -> None:
    webhook_url = os.getenv("BONJOUR_LA_FUITE_WEBHOOK_URL", "").strip()
    if not webhook_url:
        print("Error: BONJOUR_LA_FUITE_WEBHOOK_URL environment variable is required")
        sys.exit(1)

    poll_interval_str = os.getenv("POLL_INTERVAL", "3600")
    try:
        poll_interval = int(poll_interval_str)
    except ValueError:
        print(f"Error: POLL_INTERVAL must be an integer, got '{poll_interval_str}'")
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    asyncio.run(monitor.run(webhook_url, poll_interval))


if __name__ == "__main__":
    main()
