from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field
from datetime import date

import aiohttp
import yaml

PROJECT_URL = "https://framagit.org/api/v4/projects/aeris%2Fbonjour-la-fuite"
COMMITS_URL = f"{PROJECT_URL}/repository/commits"
LEAKS_DIR = "leaks/"


@dataclass
class Leak:
    processor: str
    organization_type: str = "private_company"
    date: str = ""
    data: list[str] = field(default_factory=list)
    volume: str | None = None
    sensitive: bool = False
    status: str | None = None
    subcontractor: str | None = None


def parse_leak(content: str) -> Leak:
    entry = yaml.safe_load(content) or {}

    leak_date = entry.get("date", "")
    if isinstance(leak_date, date):
        leak_date = str(leak_date)

    return Leak(
        processor=entry.get("processor", ""),
        organization_type=entry.get("organization_type", "private_company"),
        date=leak_date,
        data=entry.get("data", []),
        volume=entry.get("volume"),
        sensitive=entry.get("sensitive", False),
        status=entry.get("status"),
        subcontractor=entry.get("subcontractor"),
    )


async def fetch_commits(session: aiohttp.ClientSession, page: int = 1, per_page: int = 100) -> list[dict]:
    params = {"ref_name": "main", "page": page, "per_page": per_page}
    async with session.get(COMMITS_URL, params=params) as response:
        response.raise_for_status()
        return await response.json()


async def fetch_commit_diff(sha: str, session: aiohttp.ClientSession) -> list[dict]:
    url = f"{COMMITS_URL}/{sha}/diff"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


async def fetch_leak_file(path: str, session: aiohttp.ClientSession) -> Leak:
    encoded_path = urllib.parse.quote(path, safe="")
    url = f"{PROJECT_URL}/repository/files/{encoded_path}/raw"
    async with session.get(url, params={"ref": "main"}) as response:
        response.raise_for_status()
        content = await response.text()
    return parse_leak(content)
