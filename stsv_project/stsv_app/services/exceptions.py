class ServiceError(Exception):
    """Base exception for all service-related errors."""
    def __init__(self, message="An error occurred in the service layer."):
        self.message = message
        super().__init__(self.message)

class ValidationError(ServiceError):
    """Raised when data validation fails before saving/processing."""
    pass

class ResourceNotFoundError(ServiceError):
    """Raised when a requested resource (like a database record) is not found."""
    pass

class PermissionDeniedError(ServiceError):
    """Raised when the user does not have permission to perform an action."""
    pass
