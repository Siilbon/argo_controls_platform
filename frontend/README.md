# Argo Controls Platform — Frontend

React 19 + Vite + Tailwind CSS frontend for the Argo Controls Platform. It talks to the Flask REST API in the project root.

## Project Structure

```
├── public/               Static files served as-is (favicon)
├── src/
│   ├── components/       Reusable UI components (NavBar, Footer, SearchCard, TeamCard, DataTable, DataAge)
│   ├── pages/            Page-level components (Home, SearchResults, Trend, Gcc, Status)
│   ├── App.jsx           Root component: routes (react-router), theme, signed-in user
│   ├── searches.js       Search definitions and nav links
│   ├── api.js            fetchJson, dataset ages, and trend link helpers
│   ├── main.jsx          Entry point
│   └── index.css         Tailwind import, dark mode variant, global styles
├── index.html
├── vite.config.js        Vite plugins and the /api dev proxy
└── eslint.config.js
```

## Running Locally

The frontend needs the Flask API running, so start the backend first.

1. From the project root, start Flask on port 5001:
   ```bash
   ./dev.sh flask run --debug --port 5001
   ```

2. In a second terminal, from `frontend/`:
   ```bash
   npm install      # first time only
   npm run dev
   ```

3. Open http://localhost:5173.

## Talking to the API

In development, Vite proxies any request starting with `/api` to `http://localhost:5001` (see `vite.config.js`). Use relative paths in components:

```js
fetch('/api/team')
```

If Flask runs on a different port, update the proxy target in `vite.config.js`.

## npm Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start the Vite dev server with hot reload |
| `npm run build` | Build for production into `dist/`, which Flask serves (see Deploying in the root README) |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint |
