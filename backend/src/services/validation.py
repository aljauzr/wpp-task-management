from src.models import TaskStatus
from .exceptions import ValidationError


def validate_required_text(value: object, field: str, max_length: int) -> str:
    if value is None:
        raise ValidationError(f"{field} is required.", field)
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be a string.", field)
    value = value.strip()
    if not value:
        raise ValidationError(f"{field} must not be empty.", field)
    if len(value) > max_length:
        raise ValidationError(
            f"{field} must be at most {max_length} characters.", field
        )
    return value


def validate_description(value: object) -> str:
    if not isinstance(value, str):
        raise ValidationError("description must be a string.", "description")
    return value


def validate_status(value: object) -> str:
    if not isinstance(value, str) or value not in TaskStatus.values:
        raise ValidationError(
            "status must be one of TODO, IN_PROGRESS, DONE.", "status"
        )
    return value
