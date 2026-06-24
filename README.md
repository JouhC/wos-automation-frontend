# Whiteout Survival Redemption Frontend

This repository contains the frontend for a Whiteout Survival redemption automation system. It has been migrated from a Streamlit interface to a static TypeScript web application that calls backend REST endpoints directly from the browser.

## What Changed

- Replaced the Python/Streamlit UI with a Vite-powered TypeScript frontend.
- Kept the same backend integration model through REST endpoints.
- Added a responsive player table, gift-code list, task progress tracking, and admin controls.

## Run Locally

1. Copy `.env.example` to `.env`.
2. Set `VITE_API_URL` to your backend API URL.
3. Optional: set `VITE_EXEMPT_REMOVE_PLAYER_FIDS` to hide protected players from the remove dropdown.
4. Install dependencies:

```bash
npm install
```

5. Start the dev server:

```bash
npm run dev
```

## Build For Production

```bash
npm run build
```

## Deploy On Render

Use a Render Static Site with these settings:

- Build Command: `npm ci && npm run build`
- Publish Directory: `dist`

The included `render.yaml` defines the same settings as a Render Blueprint.

## Project Structure

- `index.html` - static page shell
- `src/main.ts` - frontend logic and UI behavior
- `src/api.ts` - backend API client
- `src/styles.css` - responsive styling
- `vite.config.ts` - Vite development config
- `.env.example` - environment variable template

## Backend Endpoints Used

- `GET /players`
- `GET /giftcodes`
- `POST /players/create/`
- `POST /players/remove/` - sends the prompted admin password in the `X-Admin-Password` header
- `POST /tasks/expired-check/`
- `POST /tasks/automate-all/`
- `GET /tasks/{taskId}/`
- `GET /tasks/inprogress/`

## Notes

The backend must support CORS for the deployed frontend origin.

## Portfolio Note

This repository is included in my portfolio as the public frontend for an automation system with a separate backend core.
