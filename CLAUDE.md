# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a SpeedHome property rental platform with three main components:

- **speedhome-backend/**: Flask-based Python API server
- **speedhome-frontend/**: React/Vite frontend application  
- **speedhome-selenium-tests/**: Comprehensive Selenium test suite

## Development Commands

### Frontend (speedhome-frontend/)
```bash
# Development server
npm run dev        # or pnpm dev (uses Vite on port 5173)

# Build and deployment
npm run build      # or pnpm build
npm run preview    # or pnpm preview

# Code quality
npm run lint       # or pnpm lint (ESLint)
```

### Backend (speedhome-backend/)
```bash
# Main application
python src/main.py  # Runs Flask server on port 5001

# Database migrations (using Flask-Migrate)
flask db init      # Initialize migrations
flask db migrate   # Generate migration
flask db upgrade   # Apply migrations

# Environment setup
export FLASK_APP=src/main.py
export DATABASE_URL=postgresql://user:password@localhost:5432/speedhome_db
```

### Testing
```bash
# Backend tests (from root directory)
pytest test_*.py   # Run individual test files
python test_*.py   # Direct execution of test files

# Selenium tests (speedhome-selenium-tests/)
pytest                    # Run all tests
pytest -m smoke          # Run smoke tests only  
pytest -m integration    # Run integration tests
pytest --browser=chrome  # Specify browser
pytest --headless        # Run headless
```

### Docker Deployment
```bash
# Full stack deployment
docker-compose up --build  # Builds and runs backend + PostgreSQL
# Frontend runs separately on port 5173/5174
# Backend accessible on port 5001
# Database on port 5432
```

## Architecture Overview

### Backend Architecture (Flask)
- **Entry Point**: `src/main.py` - Flask application with blueprint registration
- **Models**: SQLAlchemy models in `src/models/` (User, Property, Booking, Application, etc.)
- **Routes**: API endpoints organized by feature in `src/routes/`
- **Services**: Business logic in `src/services/` (background jobs, expiry service, etc.)
- **Admin**: Flask-Admin interface in `src/admin/`

Key features:
- Property lifecycle management with background scheduler
- Deposit management system with multiple payment workflows
- Tenancy agreement handling and notifications
- Stripe payment integration
- Document upload and management

### Frontend Architecture (React)
- **Framework**: React 19 with Vite build system
- **Styling**: Tailwind CSS with Radix UI components
- **State Management**: React Hook Form with Zod validation
- **Routing**: React Router DOM v7
- **UI Components**: Comprehensive Radix UI component library
- **Payments**: Stripe integration (@stripe/react-stripe-js)

### Test Architecture
- **Framework**: Selenium WebDriver with pytest
- **Pattern**: Page Object Model (POM) in `pages/`
- **Organization**: Role-based test files (tenant/landlord workflows)
- **Reporting**: HTML reports, Allure integration, automatic screenshots
- **Data**: Faker-based test data generation

## Database
- **Primary**: PostgreSQL (required, no SQLite fallback)
- **ORM**: SQLAlchemy with Flask-Migrate for schema management
- **Key Tables**: Users, Properties, Bookings, Applications, TenancyAgreements, Deposits

## Environment Configuration

### Backend (.env or environment variables)
```bash
DATABASE_URL=postgresql://user:password@db:5432/speedhome_db
FLASK_APP=src/main.py
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Test Environment (.env in speedhome-selenium-tests/)
```bash
BASE_URL=http://localhost:5174
API_BASE_URL=http://localhost:5001
TENANT_EMAIL=tenant@test.com
LANDLORD_EMAIL=landlord@test.com
BROWSER=chrome
HEADLESS=false
```

## Important Notes

- Frontend runs on ports 5173/5174, backend on 5001
- Database migrations are managed through Flask-Migrate, not manual schema creation
- Background jobs handle property lifecycle and deposit processing
- Test suite covers complete tenant/landlord user journeys
- Docker setup mounts source code for development with hot reload
- Package management uses pnpm for frontend (specified in package.json)