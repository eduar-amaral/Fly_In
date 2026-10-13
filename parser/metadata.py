from __future__ import annotations

import re
from typing import ClassVar

from .errors import ParseError


class MetadataParser:
    """Parse optional metadata blocks attached to map lines."""

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
        """Split metadata from the rest of a map line.

        Args:
            lineno: Source line number.
            content: Full raw line content.
            body: Line body that may include a metadata suffix.

        Returns:
            A tuple containing the metadata text and the cleaned body.

        Raises:
            ParseError: If the metadata block is malformed.
        """
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
        """Convert a metadata string into a key/value dictionary.

        Args:
            meta_str: Raw metadata content like "key=value key2=value2".
            lineno: Source line number for error reporting.
            content: Full raw line content.

        Returns:
            Parsed metadata dictionary.

        Raises:
            ParseError: If metadata syntax or keys are invalid.
        """
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
