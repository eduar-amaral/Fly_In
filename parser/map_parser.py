from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic import ValidationError

from models import Connection, ParsedMap, Zone, ZoneKind

from .errors import ParseError
from .metadata import MetadataParser
from .validator import MapValidator


class MapParser:
    """Read a map file and turn it into a validated domain model.

    The parser accepts the custom map format used by the project and builds a
    ParsedMap object with zones and connections.
    """

    _ZONE_PREFIXES: ClassVar[dict[str, ZoneKind]] = {
        "start_hub:": ZoneKind.START,
        "end_hub:": ZoneKind.END,
        "hub:": ZoneKind.NORMAL,
    }

    def __init__(self, filepath: str | Path) -> None:
        """Create a parser for a specific map file.

        Args:
            filepath: Path to the map file.
        """
        self._path = Path(filepath)
        self._metadata = MetadataParser()
        self._validator = MapValidator()

    def load(self) -> ParsedMap:
        """Load and parse the map file.

        Returns:
            A ParsedMap with all zones, connections, and drone count.
        """
        lines = self._read_file()
        return self._parse_all(lines)

    def _read_file(self) -> list[tuple[int, str]]:
        """Read map contents while ignoring blank lines and comments."""
        if not self._path.exists():
            raise FileNotFoundError(f"Map file not found: {self._path}")

        result: list[tuple[int, str]] = []

        with open(self._path, encoding="utf-8") as file:
            for lineno, raw in enumerate(file, start=1):
                stripped = raw.strip()

                if stripped and not stripped.startswith('#'):
                    result.append((lineno, stripped))

        return result

    def _parse_all(self, lines: list[tuple[int, str]]) -> ParsedMap:
        """Parse a list of normalized file lines into a `ParsedMap` model."""
        if not lines:
            raise ValueError("Map file is empty.")

        nb_drones = self._validator.validate_nb_drones(lines[0])

        zones: list[Zone] = []
        connections: list[Connection] = []

        zone_names: set[str] = set()
        seen_connections: set[frozenset[str]] = set()
        seen_kinds: set[ZoneKind] = set()

        for lineno, content in lines[1:]:
            zone_prefix = self._find_zone_prefix(content)

            if zone_prefix is not None:
                prefix, kind = zone_prefix

                zone = self._parse_zone_line(
                    lineno,
                    content,
                    prefix,
                    kind,
                    nb_drones,
                )

                self._register_zone(
                    zone,
                    zone_names,
                    lineno,
                    content,
                )

                if kind in (ZoneKind.START, ZoneKind.END):
                    if kind in seen_kinds:
                        raise ParseError(
                            f"Duplicate {kind.value} hub definition.",
                            lineno,
                            content,
                        )

                    seen_kinds.add(kind)

                zones.append(zone)

            elif content.startswith("connection:"):
                connection = self._parse_connection_line(
                    lineno,
                    content,
                    zone_names,
                    seen_connections,
                )

                seen_connections.add(frozenset({
                    connection.from_zone,
                    connection.to_zone
                }))

                connections.append(connection)

            else:
                raise ParseError(
                    "Unrecognised line prefix.",
                    lineno,
                    content,
                )

        if ZoneKind.START not in seen_kinds:
            raise ValueError("Map has no start_hub definition.")

        if ZoneKind.END not in seen_kinds:
            raise ValueError("Map has no end_hub definition.")

        try:
            return ParsedMap(
                nb_drones=nb_drones,
                zones=zones,
                connections=connections
            )

        except ValidationError as error:
            raise ValueError(str(error)) from error

    def _find_zone_prefix(
        self,
        content: str,
    ) -> tuple[str, ZoneKind] | None:
        """Return the zone prefix and kind when the line declares a zone."""
        for prefix, kind in self._ZONE_PREFIXES.items():
            if content.startswith(prefix):
                return prefix, kind

        return None

    def _parse_zone_line(
        self,
        lineno: int,
        content: str,
        prefix: str,
        kind: ZoneKind,
        nb_drones: int,
    ) -> Zone:
        """Parse a single zone declaration and validate its coordinates."""
        body = content[len(prefix):].strip()

        meta_str, body = self._metadata.extract(lineno, content, body)

        parts = body.split()

        if len(parts) == 3:
            name, raw_x, raw_y = parts

        elif len(parts) == 2:
            name = prefix.removesuffix(":")
            raw_x, raw_y = parts

        else:
            raise ParseError(
                f"{prefix} expects '<x> <y> [metadata]' or "
                f"'<name> <x> <y> [metadata]', "
                f"got {len(parts)} token(s): {body!r}",
                lineno,
                content,
            )

        x = self._validator.validate_coord(
            "x",
            raw_x,
            lineno,
            content,
        )

        y = self._validator.validate_coord(
            "y",
            raw_y,
            lineno,
            content
        )

        metadata = self._metadata.parse(
            meta_str,
            lineno,
            content,
        )

        zone_type = self._validator.validate_zone_type(
            metadata,
            lineno,
            content,
        )

        default_capacity = (
            nb_drones if kind in (ZoneKind.START, ZoneKind.END) else 1
        )

        max_drones = self._validator.validate_positive_int(
            metadata,
            "max_drones",
            default=default_capacity,
            lineno=lineno,
            content=content,
        )

        color = metadata.get("color")

        try:
            return Zone(
                name=name,
                x=x,
                y=y,
                kind=kind,
                zone_type=zone_type,
                color=color,
                max_drones=max_drones,
            )

        except ValidationError as error:
            raise ParseError(str(error), lineno, content) from error

    def _parse_connection_line(
        self,
        lineno: int,
        content: str,
        zone_names: set[str],
        seen_connections: set[frozenset[str]],
    ) -> Connection:
        """Parse a connection declaration between two already-defined zones."""
        body = content[len("connection:"):].strip()

        meta_str, body = self._metadata.extract(lineno, content, body)

        parts = body.split("-")

        if len(parts) != 2:
            raise ParseError(
                "Connection must be 'connection: <zone1>-<zone2>.'",
                lineno,
                content
            )

        from_zone, to_zone = parts[0].strip(), parts[1].strip()

        if not from_zone or not to_zone:
            raise ParseError(
                f"Connection zone name cannot be empty, got: {body!r}",
                lineno,
                content
            )

        for zone_name in (from_zone, to_zone):
            if zone_name not in zone_names:
                raise ParseError(
                    f"Connection references undefined zone {zone_name!r}. "
                    "Zones must be defined connections.",
                    lineno,
                    content,
                )

        pair = frozenset({from_zone, to_zone})

        if pair in seen_connections:
            raise ParseError(
                f"Duplicate connection between {from_zone!r} and {to_zone!r}.",
                lineno,
                content
            )

        metadata = self._metadata.parse(meta_str, lineno, content)

        capacity = self._validator.validate_positive_int(
            metadata,
            "max_link_capacity",
            default=1,
            lineno=lineno,
            content=content
        )

        try:
            return Connection(
                from_zone=from_zone,
                to_zone=to_zone,
                max_link_capacity=capacity
            )

        except ValidationError as e:
            raise ParseError(str(e), lineno, content) from e

    def _register_zone(
        self,
        zone: Zone,
        zone_names: set[str],
        lineno: int,
        content: str
    ) -> None:
        """Register a zone while rejecting duplicate names in the map."""
        if zone.name in zone_names:
            raise ParseError(
                f"Duplicate zone name: {zone.name!r}. "
                f"Zone names must be unique.",
                lineno,
                content
            )

        zone_names.add(zone.name)
