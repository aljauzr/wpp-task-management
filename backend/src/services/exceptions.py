class ServiceError(Exception):
    """Domain failure; HTTP mapping belongs to the controller layer."""

    code = "SERVICE_ERROR"

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.message = message
        self.field = field


class ValidationError(ServiceError):
    code = "VALIDATION_FAILED"


class NotFoundError(ServiceError):
    code = "NOT_FOUND"

    def __init__(self, resource: str, entity_id: int):
        self.resource = resource
        self.entity_id = entity_id
        super().__init__(f"{resource} with id {entity_id} was not found.")
