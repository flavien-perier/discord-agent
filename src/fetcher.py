from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import aiohttp
import yaml


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


async def fetch_leaks(url: str, session: aiohttp.ClientSession) -> list[Leak]:
    async with session.get(url) as response:
        response.raise_for_status()
        content = await response.text()

    raw_data = yaml.safe_load(content)

    leaks = []
    for entry in raw_data:
        leak_date = entry.get("date", "")
        if isinstance(leak_date, date):
            leak_date = str(leak_date)

        leak = Leak(
            processor=entry.get("processor", ""),
            organization_type=entry.get("organization_type", "private_company"),
            date=leak_date,
            data=entry.get("data", []),
            volume=entry.get("volume"),
            sensitive=entry.get("sensitive", False),
            status=entry.get("status"),
            subcontractor=entry.get("subcontractor"),
        )
        leaks.append(leak)

    return leaks
