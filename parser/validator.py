from __future__ import annotations

from models import ZoneType

from .errors import ParseError


class MapValidator:
    """Validate the input format and metadata used by map files."""

    def validate_nb_drones(
        self,
        first: tuple[int, str],
    ) -> int:
        """Validate the number of drones declared on the first line."""
        lineno, content = first

        prefix = "nb_drones:"

        if not content.startswith(prefix):
            raise ParseError(
                "First line must be 'nb_drones: <positive integer>'.",
                lineno,
                content,
            )

        raw_value = content[len(prefix):].strip()

        if not raw_value:
            raise ParseError(
                "nb_drones value is missing.",
                lineno,
                content,
            )

        try:
            value = int(raw_value)
        except ValueError:
            raise ParseError(
                f"nb_drones must be a positive integer, got: {raw_value!r}",
                lineno,
                content,
            ) from None

        if value <= 0:
            raise ParseError(
                f"nb_drones must be greater than 0, got: {value}",
                lineno,
                content,
            )

        return value

    def validate_zone_type(
        self,
        metadata: dict[str, str],
        lineno: int,
        content: str,
    ) -> ZoneType:
        """Validate the zone type declared in the metadata."""
        raw_value = metadata.get("zone", ZoneType.NORMAL.value)

        try:
            return ZoneType(raw_value)
        except ValueError:
            raise ParseError(
                f"Invalid zone type: {raw_value!r}. must be one of: "
                f"{ZoneType.valid_values()}",
                lineno,
                content,
            ) from None

    def validate_positive_int(
        self,
        metadata: dict[str, str],
        key: str,
        default: int,
        lineno: int,
        content: str,
    ) -> int:
        """Validate metadata values that must be strictly positive."""
        if key not in metadata:
            return default

        raw_value = metadata[key]

        if not raw_value.isdigit():
            raise ParseError(
                (
                    f"Metadata '{key}' must be a positive integer, "
                    f"got: {raw_value!r}"
                ),
                lineno,
                content,
            )

        value = int(raw_value)

        if value <= 0:
            raise ParseError(
                f"Metadata '{key}' must be a positive integer, "
                f"got: {raw_value!r}",
                lineno,
                content,
            )

        return value

    def validate_coord(
        self,
        field: str,
        raw_value: str,
        lineno: int,
        content: str,
    ) -> int:
        """Validate the integer coordinate of a zone."""
        try:
            return int(raw_value)
        except ValueError:
            raise ParseError(
                f"Zone coordinate '{field}' must be an integer, "
                f"got: {raw_value!r}",
                lineno,
                content,
            ) from None
