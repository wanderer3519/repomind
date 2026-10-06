# Low-Code Website Generator

A full-stack code generation platform that builds secure, production-ready web applications from a simple configuration file.

This tool automates the creation of a **Spring Boot (Java)** backend and an **Angular 17** frontend, complete with JWT authentication, Role-Based Access Control (RBAC), and CRUD operations.

## Features

  * **Full-Stack Generation**: Creates a complete backend and frontend codebase in seconds.
  * **Secure Authentication**:
      * **JWT & Basic Auth** support.
      * **BCrypt** password hashing.
      * **Email Verification** flow (optional).
  * **Role-Based Access Control (RBAC)**:
      * Granular permissions (e.g., `Admin` can `create`, `User` can `view-own`).
      * Auto-generated Security Guards and `@PreAuthorize` annotations.
  * **Dynamic Frontend**:
      * Generates Angular 17 Standalone Components.
      * Auto-creates Forms, Lists, and Routing configurations.
      * Smart inputs (Dropdowns for Enums, Lookups for References).
  * **Production Ready**:
      * Uses **Maven** for backend and **npm** for frontend.
      * Includes Swagger UI (`/swagger-ui.html`).
      * Includes H2 Database (In-Memory or File).

-----

## Project Structure

```text
/
├── backend-generator/      # The Logic Engine (C Code)
│   ├── src/                #    - Generators (Auth, CRUD, Security)
│   ├── grammar/            #    - Flex/Bison Parser for .cfg files
│   └── templates/          #    - Java Code Blueprints (.tpl)
│
├── frontend-generator/     # The UI Engine (Node.js)
│   ├── scripts/            #    - Logic to generate Angular components
│   └── blueprints/         #    - Angular Templates (.tpl) & Shell
│
├── config/                 # Configuration Files
│   └── test2.cfg           #    - The input specification
│
├── output/                 # Generated Artifacts (Ignored by Git)
│   ├── backend/            #    - The generated Spring Boot App
│   └── frontend/           #    - The generated Angular App
│
├── tests/                  # Integration Tests (Python)
└── Makefile                # Master Build System
```

-----

## Prerequisites

Ensure you have the following installed on your system:

1.  **C Toolchain**: `gcc`, `make`, `flex`, `bison` (For the generator core).
2.  **Java Backend**: JDK 17+, `mvn` (Maven).
3.  **Frontend**: Node.js (v18+), `npm`.
4.  **CLI Tools**: Angular CLI (`npm install -g @angular/cli@17`).
5.  **Testing**: Python 3, `pip` (and `requests` library).

-----

## Quick Start

The entire build process is automated via a Master Makefile.

### 1\. Build & Generate Everything

This compiles the generator, parses the config, and builds both apps.

```bash
make all
```

### 2\. Run the Backend

Open a terminal and start the Spring Boot server.

```bash
cd output/backend
mvn spring-boot:run
```

  * **API**: `http://localhost:8080`
  * **Swagger UI**: `http://localhost:8080/swagger-ui.html`

### 3\. Run the Frontend

Open a second terminal and start the Angular app.

```bash
cd output/frontend
ng serve
```

  * **UI**: `http://localhost:4200`

-----

## Configuration Guide

The generator is driven by a `.cfg` file (e.g., `config/test2.cfg`).

### Basic Syntax

```properties
# 1. Application Settings
Project       : MyAppName
Auth          : jwt          # or 'basic'
EmailVerify   : No           # or 'Yes'

# 2. Define Admin Credentials (bootstrapped on start)
AdminEmail    : admin@example.com
AdminPassword : secretpassword

# 3. Define Tables
Table Team
Field id          : AUTO-ID
Field name        : TEXT
Field description : LONGTEXT

Table Ticket
Field id          : AUTO-ID
Field title       : TEXT
Field status      : CHOICE [ TODO | IN_PROGRESS | DONE ]
Field sprint      : REF Sprint  # Foreign Key to 'Sprint' table

# 4. Define Permissions (Role on Table : actions)
# Actions: create, view-all, view-own, create-own
Admin on Team :
can create, view-all

User on Ticket :
can create-own, view-own
```

-----

## Development Workflow

You don't need to rebuild everything when making changes. Use these specific commands:

| Command | Description | Use Case |
| :--- | :--- | :--- |
| **`make generate-spec`** | Updates `app-spec.json` only. | You changed `test2.cfg` but only want to update the JSON spec. |
| **`make generate-backend`** | Updates Java files only. | You modified a C generator file (e.g., `crud_generator.c`) or a Java template. |
| **`make generate-frontend`** | Updates Angular files only. | You changed the `app-spec.json` or an Angular template (`.tpl`). |
| **`make install-frontend`** | Reinstalls Angular + Gens files. | Use if you broke the frontend or need a fresh `npm install`. |
| **`make test`** | Runs Python Integration Tests. | Verifies the backend logic (Login, CRUD, Security). |

-----

## Testing

The project includes an automated test suite to verify the backend logic before you even open the browser.

```bash
make test
```

This runs `tests/complex_api_tester.py`, which performs:

1.  **Admin Login**: Verifies credentials and retrieves JWT.
2.  **CRUD Operations**: Creates Teams/Sprints via API.
3.  **Security Checks**: Verifies that standard Users get `403 Forbidden` when accessing Admin resources.
4.  **Data Isolation**: Checks that Users can only see their own data (if configured).

-----

## License

This project is generated for educational and development purposes.