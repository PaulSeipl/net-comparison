# Frontend - Internet Provider Comparison UI

**This is mostly implemented with the help of lovable.**

This directory contains the React + TypeScript frontend for the Internet Provider Comparison app. Users can enter their address, view and filter offers from multiple providers, and compare up to 4 offers side-by-side.

## Challenge

Create a responsive web UI that gracefully handles unreliable provider APIs by:
- Displaying real-time loading states per provider as results arrive
- Continuing to show available offers even when some providers fail
- Providing rich filtering, sorting, and comparison capabilities
- Maintaining smooth UX despite backend API inconsistencies

## Solution Approach

**Frontend-Implemented Progressive Loading**: Since the backend's main `/providers/offers` endpoint is blocking, the frontend implements its own parallel provider fetching to achieve progressive loading.


1. **Frontend Parallel Fetching**: `apiService.getAllOffers()` calls individual provider endpoints (`/providers/offers/{provider}`) in parallel using Promise.allSettled, enabling true progressive loading.

2. **Real-time Provider Status**: UI shows individual loading spinners per provider, updating to checkmarks as each completes successfully.

3. **Graceful Frontend Degradation**: Failed providers don't prevent display of successful results due to Promise.allSettled pattern.


## Tech Stack
- **Vite** + React + TypeScript
- **Tailwind CSS** (with PostCSS)
- **React Query** for data fetching and caching
- **React Router** for routing
- Custom UI components under `src/components/`
- API service abstraction in `src/services/apiService.tsx`
- URL state and validation in `src/utils/urlState.ts`
- Custom hooks for mobile detection (`use-mobile.tsx`) and toasts (`use-toast.ts`)
- Offer filtering/sorting utilities in `src/utils/offerUtils.tsx`

## Getting Started

1. **Install Dependencies**:
   ```pwsh
   cd frontend
   npm install
   ```

2. **Configure Environment**:
   - Edit `src/config/production.ts`, set `API_BASE_URL` and `API_KEY`.

3. **Run Development Server**:
   ```pwsh
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

4. **Build for Production**:
   ```pwsh
   npm run build
   ```

## Directory Overview
- `src/pages/Index.tsx`: main search & results view
- `src/components/`: reusable UI pieces (SearchForm, ResultsDisplay, ComparisonPanel, etc.)
- `src/services/apiService.tsx`: calls backend API per provider
- `src/utils/`: filtering, URL state, validation helpers
- `src/hooks/`: custom React hooks

## Development Guide

**Key Components**:
- `SearchForm`: Address input with validation
- `ResultsDisplay`: Manages provider loading states and progressive results
- `FilterSidebar`/`MobileFilterSidebar`: Comprehensive filtering UI
- `EnhancedOfferCard`/`MobileOfferCard`: Responsive offer display
- `ComparisonPanel`: Side-by-side offer comparison

**Data Flow**:
1. User enters address → `SearchForm`
2. API calls made per provider → `apiService.getAllOffers()`
3. Results displayed progressively → `ResultsDisplay`
4. Client-side filtering/sorting → `offerUtils.tsx`
5. Comparison functionality → `ComparisonPanel`

**Adding Features**:
- New filters: Update `FilterState` in `types/api.ts` and `filterOffers()` in `utils/offerUtils.tsx`
- UI components: Follow existing patterns in `components/`
- API changes: Update `apiService.tsx` and type definitions

**Mobile Responsiveness**: Uses `useIsMobile()` hook and separate mobile components for optimal UX.
