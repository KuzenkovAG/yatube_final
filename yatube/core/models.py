from django.db import models


class ModelWithDate(models.Model):
    """Abstract model with Date Field."""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ("-created",)
