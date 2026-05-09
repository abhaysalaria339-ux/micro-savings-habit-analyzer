# Micro-Savings Habit Analyzer Frontend

React frontend for the Micro-Savings Habit Analyzer.

## Requirements

- Node.js 20+
- npm

## Local Setup

From the frontend folder:

```powershell
cd "D:\Codex Project\frontend"
npm install
copy .env.example .env
```

## Run The Frontend

```powershell
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Environment

Default backend API URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Development mode falls back to this local API URL when `.env` has not been
created yet. Production builds must still set `VITE_API_BASE_URL`.

## Verification

```powershell
npm run build
npm run lint
```

## Production Build

Build the static production bundle:

```powershell
npm run build:production
```

Required production variable:

```env
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

Build output:

```text
dist/
```

Deploy `dist/` to a static hosting service, or use the existing Docker image
which serves the same build through Nginx.

## Docker Runtime

Build the production image:

```powershell
docker build -t micro-savings-frontend .
```

Build with a deployed backend API URL:

```powershell
docker build --build-arg VITE_API_BASE_URL=https://api.example.com/api/v1 -t micro-savings-frontend .
```

Run the frontend container:

```powershell
docker run --rm -p 5173:80 micro-savings-frontend
```
