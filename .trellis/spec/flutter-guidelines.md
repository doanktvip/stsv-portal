# Flutter Coding Guidelines

## Architecture & Structure
- **Pattern**: Feature-first architecture.
- **Directory Structure**: 
  - `lib/features/{feature_name}/`
    - `controllers/`: Contains business logic and state management.
    - `models/`: Data models and JSON serialization logic (`fromJson`, `toJson`).
    - `repositories/`: API communication and data fetching layer.
    - `screens/`: UI components and widgets.
- **Separation of Concerns**: UI (`screens`) should only observe state and trigger actions. Business logic and API state reside in `controllers`. Raw API calls reside in `repositories`.

## State Management & Routing
- **GetX**: Use `GetX` for state management, dependency injection, and routing.
- **Controllers**: Extend `GetxController`. Use `.obs` for reactive state variables.
- **Navigation & Dialogs**: Use `Get.to()`, `Get.snackbar()`, `Get.dialog()` for UI overlays without needing `BuildContext`.

## API & Data
- **Models**: Ensure models handle null safety correctly.
- **Repositories**: Handle API exceptions and return a standard `ApiResponse` or structured data for the controller.
