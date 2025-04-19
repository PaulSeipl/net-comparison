# Internet Provider Comparison Service

A robust web application that compares internet provider offers from multiple sources, providing a seamless comparison experience despite API failures or slow responses.

## Architecture

### Backend (FastAPI)
- API Gateway pattern handling multiple provider integrations
- PostgreSQL database for caching and rate limiting (using psycopg3 with async support)
- Circuit breaker pattern for API resilience
- JWT-based sharing mechanism
- Async request handling with timeouts

### Frontend (React + TypeScript)
- Modern React (v19.1.0) with TypeScript
- Material UI for clean, responsive UI with filtering capabilities
- Vite for fast development and optimized builds
- React Query for efficient data fetching
- Share functionality using generated URLs
- Loading states and error handling

## Technologies

### Backend
- FastAPI 0.109.2
- SQLAlchemy 2.0.27 with async support
- psycopg 3.1.18 (psycopg3)
- Pydantic 2.6.1
- Python 3.12

### Frontend
- React 19.1.0
- TypeScript 5.3.3
- Material UI 5.15.10
- React Router 6.22.1
- React Query 3.39.3
- Axios 1.6.7
- Vite 5.1.3

## Project Structure
```
net-comparison/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── providers/
│   │   │   │   ├── webwunder.py
│   │   │   │   ├── byteme.py
│   │   │   │   ├── pingperfect.py
│   │   │   │   ├── verbyndich.py
│   │   │   │   └── servusspeed.py
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   └── models.py
│   │   └── services/
│   │       ├── cache.py
│   │       └── circuit_breaker.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Environment Variables
Create a `.env` file in the root directory with the following variables:
```env
# Database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=provider_comparison

# API Keys
WEBWUNDER_API_KEY=your_key
BYTEME_API_KEY=your_key
PINGPERFECT_CLIENT_ID=your_client_id
PINGPERFECT_SIGNATURE_SECRET=your_secret
VERBYNDICH_API_KEY=your_key
SERVUSSPEED_USERNAME=your_username
SERVUSSPEED_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your_secret_key
```

### Running the Application
1. Build and start the containers:
```bash
docker-compose up --build
```

2. Access the application:
- Frontend: http://localhost:5173 (Vite development server)
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Features
- Multi-provider internet offer comparison
- Robust error handling and fallback mechanisms
- Async database operations with psycopg3
- Caching system for improved performance
- Share functionality for comparison results
- Filtering and sorting capabilities
- Circuit breaker pattern for API resilience
- Fast frontend development with Vite and React 19

## API Documentation
Detailed API documentation is available at http://localhost:8000/docs when running the application.

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request


## TODO
- install new dependencies
- run everything