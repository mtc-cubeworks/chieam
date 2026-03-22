# Semi-Frappe EAM Frontend

A modern Vue.js frontend built with Nuxt 4 and NuxtUI for the Semi-Frappe Enterprise Asset Management system.

## Tech Stack

- **Framework**: Nuxt 4
- **UI Library**: NuxtUI
- **Styling**: Tailwind CSS
- **TypeScript**: Full TypeScript support
- **State Management**: Vue 3 Composition API with useState
- **API Client**: Custom $fetch wrapper with authentication

## Features

- 🎨 Modern UI with NuxtUI components
- 🔐 Authentication with JWT tokens
- 📱 Responsive design
- 🌙 Dark mode support
- 📊 Dynamic entity management
- 🔄 Workflow management
- 👥 User and role management (admin)

## Getting Started

1. Install dependencies:

```bash
source ~/.nvm/nvm.sh
nvm use 20
pnpm install
```

2. Create the frontend environment file:

```bash
cat > .env <<'EOF'
NODE_ENV=production
HOST=127.0.0.1
PORT=3012
NUXT_PUBLIC_API_URL=http://127.0.0.1:8012/api
NUXT_PUBLIC_WS_URL=ws://127.0.0.1:8012
EOF
```

3. Start the development server:

```bash
pnpm dev
```

The development application will be available at `http://localhost:3000` unless you override the port.

For the configured local `eam-met` instance, the running frontend is available at `http://127.0.0.1:3012/`.

## Project Structure

```
frontend/
├── app/
│   ├── components/     # Vue components
│   ├── composables/    # Reusable composition functions
│   ├── layouts/        # Layout components
│   ├── middleware/     # Route middleware
│   ├── pages/          # File-based routing
│   └── plugins/        # Nuxt plugins
├── assets/             # Static assets
├── public/             # Public files
└── types/              # TypeScript type definitions
```

## Key Composables

### useApi()

Provides methods to interact with the backend API:

- `getMeta()` - Get entity metadata list
- `getEntityMeta(entity)` - Get specific entity metadata
- `getEntityList(entity, params)` - Get paginated entity list
- `getEntityDetail(entity, id)` - Get single entity record
- `postEntityAction(entity, request)` - Perform CRUD actions
- `login(username, password)` - Authenticate user

### useAuth()

Manages authentication state:

- `login()` - Login with credentials
- `logout()` - Clear auth state and redirect
- `initAuth()` - Initialize auth from localStorage

## Authentication

The application uses JWT-based authentication:

- Access tokens are stored in localStorage
- Tokens are automatically attached to API requests
- 401 responses trigger automatic logout

## Routing

The app uses file-based routing with the following structure:

- `/` - Home page (requires auth)
- `/login` - Login page
- `/entity/[name]` - Entity list view
- `/entity/[name]/create` - Create new entity
- `/entity/[name]/edit/[id]` - Edit entity
- `/entity/[name]/detail/[id]` - Entity details
- `/workflow` - Workflow management
- `/admin` - Admin panel

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `.output` directory.
