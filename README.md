# Whiteout Survival Redemption Frontend

This repository has been migrated from a Streamlit front-end to a static TypeScript web application.

## What changed
- Replaced the Python/Streamlit UI with a Vite-powered TypeScript frontend.
- The app now calls the same backend REST endpoints directly from the browser.
- Added a responsive player table, gift code list, task progress tracking, and admin controls.

## Run locally
1. Copy `.env.example` to `.env`.
2. Set `VITE_API_URL` to your backend API URL.
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the dev server:
   ```bash
   npm run dev
   ```

## Build for production
```bash
npm run build
```

## Project structure
- `index.html` — static page shell
- `src/main.ts` — frontend logic and UI behavior
- `src/api.ts` — backend API client
- `src/styles.css` — responsive styling
- `vite.config.ts` — Vite development config
- `.env.example` — environment variable template

## Backend endpoints used
- `GET /players`
- `GET /giftcodes`
- `POST /players/create/`
- `POST /players/remove/`
- `POST /tasks/expired-check/`
- `POST /tasks/automate-all/`
- `GET /tasks/{taskId}/`
- `GET /tasks/inprogress/`

> Note: The backend must support CORS for the deployed frontend origin.

