# Internet Provider Comparison

A full-stack application that allows users to compare internet providers despite unreliable third-party APIs. Built to handle API failures gracefully while maintaining smooth user experience.

## Architecture

### Backend (`backend/`): 

Deployed on render.com. Using Free Tear -> Slow startup. [Swagger UI](https://net-comparison-backend.onrender.com/docs#/)


FastAPI service with individual provider resilience but blocking aggregation endpoint. Frontend compensates with parallel calls. [Details →](backend/README.md)

## Frontend (`frontend/`):

Deployed on Vercel. [Net-Comparison](https://net-comparison-frontend.vercel.app/)

React + TypeScript UI implementing progressive loading by calling individual provider endpoints in parallel. Created with the help of [loveable](https://lovable.dev/). [Details →](frontend/README.md)