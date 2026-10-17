from __future__ import annotations

import asyncio
import logging

import aiohttp

from .fetcher import LEAKS_DIR, fetch_commit_diff, fetch_commits, fetch_leak_file
from .formatter import format_notification
from .notifier import send_notification

logger = logging.getLogger(__name__)

MAX_COMMIT_PAGES = 3


async def fetch_new_commit_shas(last_seen_sha: str, session: aiohttp.ClientSession) -> list[str]:
    for page in range(1, MAX_COMMIT_PAGES + 1):
        commits = await fetch_commits(session, page=page)
        if not commits:
            return []
        shas = [commit["id"] for commit in commits]
        try:
            cutoff = shas.index(last_seen_sha)
            return shas[:cutoff]
        except ValueError:
            if len(commits) < 100:
                logger.warning("Last seen commit not found in history, considering all recent commits as new")
                return shas
            continue
    logger.warning("More than the maximum number of pages of new commits, considering only the most recent ones")
    return [commit["id"] for commit in await fetch_commits(session, page=MAX_COMMIT_PAGES)]


async def fetch_new_leaks(sha: str, session: aiohttp.ClientSession) -> list:
    diffs = await fetch_commit_diff(sha, session)

    leaks = []
    for entry in diffs:
        path = entry["new_path"]
        if not path.startswith(LEAKS_DIR):
            continue
        if entry.get("deleted_file") or not entry.get("new_file"):
            continue
        try:
            leaks.append(await fetch_leak_file(path, session))
        except Exception as e:
            logger.error(f"Failed to fetch new leak file {path} from commit {sha}: {e}")

    return leaks


async def run(webhook_url: str, poll_interval: int) -> None:
    async with aiohttp.ClientSession() as session:
        head_commits = await fetch_commits(session)
        last_seen_sha = head_commits[0]["id"]
        logger.info(f"Initialized at commit {last_seen_sha[:10]}, monitoring started")

        await asyncio.sleep(poll_interval)

        while True:
            try:
                new_shas = await fetch_new_commit_shas(last_seen_sha, session)
                logger.info(f"Found {len(new_shas)} new commit(s)")

                for sha in reversed(new_shas):
                    leaks = await fetch_new_leaks(sha, session)
                    for leak in leaks:
                        payload = format_notification(leak)
                        await send_notification(webhook_url, payload, session)

                if new_shas:
                    last_seen_sha = new_shas[0]

            except Exception as e:
                logger.error(f"Error during poll cycle: {e}")

            await asyncio.sleep(poll_interval)
