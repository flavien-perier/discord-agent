from __future__ import annotations

import urllib.parse
from pathlib import Path

import jinja2

from .fetcher import Leak

ORGANIZATION_EMOJIS: dict[str, str] = {
    "private_company": ":office:",
    "public_authority": ":classical_building:",
    "association": ":handshake:",
    "federation": ":medal:",
}
DEFAULT_EMOJI = ":office:"


def format_notification(leak: Leak) -> dict:
    emoji = ORGANIZATION_EMOJIS.get(leak.organization_type, DEFAULT_EMOJI)

    if leak.sensitive:
        color = 0xE74C3C  # Red
    elif leak.status == "claimed":
        color = 0xE67E22  # Orange
    else:
        color = 0x3498DB  # Blue

    encoded_processor = urllib.parse.quote(leak.processor, safe="")
    url = f"https://bonjourlafuite.eu.org/#{encoded_processor}-{leak.date}"

    template_dir = Path(__file__).parent / "templates"
    loader = jinja2.FileSystemLoader(str(template_dir))
    env = jinja2.Environment(loader=loader)
    template = env.get_template("leak_embed.j2")

    description = template.render(
        data=leak.data,
        volume=leak.volume,
        sensitive=leak.sensitive,
        status=leak.status,
        subcontractor=leak.subcontractor,
    )

    return {
        "title": f"{emoji} {leak.processor}",
        "url": url,
        "color": color,
        "description": description,
        "footer": {"text": leak.date},
    }
