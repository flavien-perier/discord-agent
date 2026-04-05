from __future__ import annotations

import asyncio
import logging

import aiohttp

from .fetcher import fetch_leaks
from .formatter import format_notification
from .notifier import send_notification

logger = logging.getLogger(__name__)

LEAKS_YAML_URL = "https://framagit.org/aeris/bonjour-la-fuite/-/raw/main/leaks.yaml?ref_type=heads"


async def run(webhook_url: str, poll_interval: int) -> None:
    async with aiohttp.ClientSession() as session:
        initial_leaks = await fetch_leaks(LEAKS_YAML_URL, session)
        known_keys: set[tuple[str, str]] = {(leak.processor, leak.date) for leak in initial_leaks}
        logger.info(f"Initialized with {len(known_keys)} known leaks, monitoring started")

        await asyncio.sleep(poll_interval)

        while True:
            try:
                leaks = await fetch_leaks(LEAKS_YAML_URL, session)

                new_leaks = [l for l in leaks if (l.processor, l.date) not in known_keys]
                logger.info(f"Found {len(new_leaks)} new leak(s)")

                for leak in new_leaks:
                    payload = format_notification(leak)
                    await send_notification(webhook_url, payload, session)

                for leak in leaks:
                    known_keys.add((leak.processor, leak.date))

            except Exception as e:
                logger.error(f"Error during poll cycle: {e}")

            await asyncio.sleep(poll_interval)
