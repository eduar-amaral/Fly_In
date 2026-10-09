from __future__ import annotations

import re
from typing import ClassVar

from .errors import ParseError


class MetadataParser:
    _META_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"\[([^\]]*)\]$"
    )

    _KV_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"([a-zA-Z_][a-zA-Z0-9_]*)=(\S+)"
    )

    def extract(
        self,
        lineno: int,
        content: str,
        body: str
    ) -> tuple[str, str]:
        if body.count('[') != body.count(']'):
            raise ParseError(
                f"Mismatched brackets in metadata block: {body!r}",
                lineno,
                content
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
        content: str
    ) -> dict[str, str]:
        if not meta_str.strip():
            return {}

        metadata: dict[str, str] = {}

        for match in self._KV_RE.finditer(meta_str):
            key, value = match.groups()

            if key in metadata:
                raise ParseError(
                    f"Duplicate metadata key: {key!r}",
                    lineno,
                    content
                )

            metadata[key] = value

        leftover = self._KV_RE.sub("", meta_str).strip()

        if leftover:
            raise ParseError(
                f"Invalid metadata content (expected key=value pairs), "
                f"got: {leftover!r}",
                lineno,
                content
            )

        return metadata
