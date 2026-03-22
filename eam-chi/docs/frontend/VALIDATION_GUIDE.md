# Frontend Validation Guide

This guide outlines the steps to validate the Generic Frontend against the new Modular Backend architecture.

## Prerequisites

1.  **Backend Running**: Ensure the FastAPI backend is running.
    ```bash
    cd backend
    source venv/bin/activate
    python -m app.main  # or uvicorn app.main:fastapi_app --reload
    ```
2.  **Frontend Running**: Ensure the Next.js frontend is running.
    ```bash
    cd frontend
    npm run dev
    ```

## Validation Scenarios

### 1. New Entity Discovery (`/project`)

**Goal**: Verify the frontend can discover and render a newly created modular entity.

1.  Navigate to `http://localhost:3000/project`.
2.  **Expectation**:
    - You should see a "List View" for **Project**.
    - Columns: Name, Description, Start Date, End Date, Status.
    - The "Add New" button should be visible.

### 2. Generic Form Rendering (`/project/new`)

**Goal**: Verify `FormView` correctly interprets the JSON metadata synced from Python models.

1.  Click "Add New" or navigate to `http://localhost:3000/project/new`.
2.  **Expectation**:
    - **Name**: Text Input.
    - **Description**: Text Area (because we defined it as `Text` in Python).
    - **Start/End Date**: Date Pickers (mapped from `DateTime/Date`).
    - **Status**: Dropdown/Select (mapped from `String` with default, though currently it might be a text input unless explicitly defined as 'select' in metadata options - _Note: We added 'active' default, generic UI might treat as text unless we refined metadata. Check if it renders as Input or Select_).
    - **Manager**: **Link Field** (Autocomplete/Dropdown). This is the critical test for the `ForeignKey("users.id")`.

### 3. Link Field Functionality

**Goal**: Verify relationships work.

1.  In the "Manager" field, type a username (e.g., "admin").
2.  **Expectation**: The dropdown should fetch users from `/api/entity/user/options`.
3.  Select a user.
4.  Save the Project.
5.  **Verification**:
    - Redirects to the Project Detail/List.
    - The "Manager" column shows the _Name/Username_ of the user, not just the ID (if the frontend `LinkField` is working correctly).

### 4. Code-First Updates (Real-time Test)

**Goal**: Verify the "Code-First" workflow.

1.  **Modify Backend**:
    - Open `backend/app/modules/project_management/models/project.py`.
    - Add a new field: `budget: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)`.
2.  **Sync**:
    - Run `python -m app.forge sync-meta` in `backend/`.
3.  **Refresh Frontend**:
    - Reload `http://localhost:3000/project/new`.
4.  **Expectation**:
    - A new "Budget" field appears automatically.
    - It accepts numeric input.

## Troubleshooting

- **Entity Not Found**: Check if `app/modules/project_management/entities/project/project.json` exists.
- **Link Field Empty**: Ensure the `user` entity has records (`python -m app.forge seed`).
- **API Errors**: Check the backend console. The generic router (`routers/entity.py`) relies on `MetaRegistry` being loaded at startup.
