# Aegis Cloud

Web dashboard for managing Windows PCs remotely. FastAPI backend + Next.js frontend.

## Stack

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, SQLAlchemy 2.0, PostgreSQL 16, Redis
- **Auth**: JWT with refresh tokens, 2FA (TOTP), OAuth (Google/GitHub)

## Quick Start

```bash
git clone https://github.com/Aztech-1729/aegiscloud.git
cd aegiscloud
docker compose up -d
```

Frontend: http://localhost:3000  
API: http://localhost:8000  
Docs: http://localhost:8000/docs

## Project Structure

```
aegiscloud/
├── frontend/           # Next.js app
│   └── src/
│       ├── app/        # Pages (dashboard/, auth/, blog/, about/, etc.)
│       ├── components/  # UI, layout, landing components
│       ├── lib/         # Utilities, API client
│       ├── stores/      # Zustand stores
│       └── hooks/       # Custom hooks
├── backend/            # FastAPI app
│   └── app/
│       ├── api/v1/     # Route handlers
│       ├── models/     # SQLAlchemy models
│       ├── schemas/    # Pydantic schemas
│       ├── services/   # Business logic
│       ├── core/       # Config, security, logging
│       └── db/         # Database session
└── docs/               # Documentation
```

## Environment Variables

### Backend
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/aegis_cloud
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:3000
LEMONSQUEEZY_API_KEY=            # Optional — for payments
```

### Frontend
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```
