from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(slots=True)
class PostedItem:
    link: str
    posted_at: datetime


class PostedStore:
    def __init__(self, path: Path, max_items: int = 300) -> None:
        self.path = path
        self.max_items = max_items
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._items: list[PostedItem] = self._load()

    def _load(self) -> list[PostedItem]:
        if not self.path.exists():
            return []

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

        items: list[PostedItem] = []
        for item in raw:
            link = str(item.get("link", "")).strip()
            posted_at_raw = str(item.get("posted_at", "")).strip()
            if not link or not posted_at_raw:
                continue
            try:
                posted_at = datetime.fromisoformat(posted_at_raw)
            except ValueError:
                continue
            items.append(PostedItem(link=link, posted_at=posted_at))
        return items

    def save(self) -> None:
        payload = [
            {"link": item.link, "posted_at": item.posted_at.astimezone(UTC).isoformat()}
            for item in self._items[-self.max_items :]
        ]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def has_link(self, link: str) -> bool:
        canonical = link.split("?")[0]
        return any(item.link.split("?")[0] == canonical for item in self._items)

    def add_link(self, link: str) -> None:
        self._items.append(PostedItem(link=link, posted_at=datetime.now(tz=UTC)))
        self.save()

