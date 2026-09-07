# Python Backend (Django DRF) Guidelines

## Architecture & Modular Design
- **Framework**: Django & Django REST Framework (DRF).
- **Structure**: The `stsv_app` is structured modularly by splitting standard Django files into directories:
  - `models/`: Database models separated by domain.
  - `views/`: DRF ViewSets and API views.
  - `serializers/`: DRF Serializers for request validation and response formatting.
  - `services/`: Business logic layer. Keep fat models and fat views to a minimum by offloading complex operations to this layer.

## Best Practices
- **Thin Views**: Views should only handle HTTP routing, request parsing (via serializers), calling the appropriate service, and returning the response.
- **Service Layer**: Complex database queries, external API calls, and business rules should live in `services/`.
- **Validation**: Rely on DRF serializers for request data validation.
- **Exceptions**: Use custom exceptions defined in `exceptions.py` or standard DRF exceptions to return consistent error responses.
- **Permissions**: Handle access control at the view level using custom permissions from `permissions.py`.
