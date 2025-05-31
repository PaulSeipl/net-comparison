# Internet Provider Comparison

A full-stack application that allows users to compare internet providers despite unreliable third-party APIs. Built to handle API failures gracefully while maintaining smooth user experience.

## Architecture

- **Backend** (`backend/`): FastAPI service with individual provider resilience but blocking aggregation endpoint. Frontend compensates with parallel calls. [Details →](backend/README.md)
- **Frontend** (`frontend/`): React + TypeScript UI implementing progressive loading by calling individual provider endpoints in parallel. [Details →](frontend/README.md)