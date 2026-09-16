from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model providing self-updating timestamps.
    Used by all domain entities.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when entity was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when entity was last updated"
    )

    class Meta:
        abstract = True
