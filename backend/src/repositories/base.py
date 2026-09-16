from typing import TypeVar, Generic, Type, Optional, List, Any
from django.db import models

T = TypeVar('T', bound=models.Model)


class BaseRepository(Generic[T]):
    """
    Abstract Base Repository providing standard data access methods.
    Isolates Django ORM details from business services.
    """

    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Fetch single entity by primary key or return None."""
        try:
            return self.model.objects.get(pk=entity_id)
        except self.model.DoesNotExist:
            return None

    def list_all(self) -> List[T]:
        """List all entities of this type."""
        return list(self.model.objects.all())

    def save(self, entity: T) -> T:
        """Persist an entity instance."""
        entity.save()
        return entity

    def delete(self, entity: T) -> None:
        """Remove an entity instance."""
        entity.delete()
