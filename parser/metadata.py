from __future__ import annotations

import re
from typing import ClassVar

from .errors import ParseError


class MetadataParser:
    _META_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"\[([^\]]*)\]\s*$"
    )

    _ITEM_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)="
        r"(?P<value>[A-Za-z0-9_-]+)$"
    )

    def extract(
        self,
        lineno: int,
        content: str,
        body: str,
    ) -> tuple[str, str]:
        if body.count('[') != body.count(']'):
            raise ParseError(
                f"Mismatched brackets in metadata block: {body!r}",
                lineno,
                content,
            )

        match = self._META_RE.search(body)
        if match:
            metadata = match.group(1)
            clean_body = body[:match.start()].strip()
            return metadata, clean_body

        return "", body

    def parse(
        self,
        meta_str: str,
        lineno: int,
        content: str,
    ) -> dict[str, str]:
        if not meta_str.strip():
            return {}

        metadata: dict[str, str] = {}
        tokens = meta_str.split()

        for token in tokens:
            match = self._ITEM_RE.fullmatch(token)
            if match is None:
                raise ParseError(
                    "Invalid metadata content "
                    f"(expected key=value pairs), got: {meta_str!r}",
                    lineno,
                    content,
                )

            key = match.group("key")
            if key in metadata:
                raise ParseError(
                    f"Duplicate metadata key: {key!r}",
                    lineno,
                    content,
                )

            metadata[key] = match.group("value")

        return metadata
