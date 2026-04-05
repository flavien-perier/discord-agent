from __future__ import annotations

import logging

import aiohttp

logger = logging.getLogger(__name__)


async def send_notification(webhook_url: str, payload: dict, session: aiohttp.ClientSession) -> None:
    try:
        async with session.post(webhook_url, json={"embeds": [payload]}) as response:
            if not (200 <= response.status < 300):
                text = await response.text()
                logger.warning(f"Webhook request failed with status {response.status}: {text}")
    except Exception as e:
        logger.warning(f"Error sending notification: {e}")
