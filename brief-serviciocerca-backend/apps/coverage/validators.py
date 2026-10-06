import re

from django.core.exceptions import ValidationError


IDENTIFIER_PATTERN = re.compile(r"^[A-Z0-9_-]+$")


def validate_identifier(value: str) -> None:
    """
    Validate identifiers used by nodes and technicians.

    Allowed characters:
    - Uppercase letters
    - Numbers
    - Hyphen
    - Underscore

    Examples:
    BASE-NORTE
    ZONA_01
    TEC-001
    """

    if not value:
        raise ValidationError(
            "Identifier cannot be empty."
        )

    if not IDENTIFIER_PATTERN.fullmatch(value):
        raise ValidationError(
            "Identifier may only contain uppercase letters, "
            "numbers, hyphens, and underscores."
        )


def validate_positive_weight(value) -> None:
    """
    Ensure graph edge weights are strictly positive.
    """

    if value is None or value <= 0:
        raise ValidationError(
            "Connection weight must be greater than zero."
        )