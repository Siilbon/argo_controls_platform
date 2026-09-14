# Argo Controls Platform — Frontend

React 19 + Vite + Tailwind CSS frontend for the Argo Controls Platform. It talks to the Flask REST API in the project root.

## Project Structure

```
├── public/               Static files served as-is
├── src/
│   ├── assets/           Images imported by components
│   ├── components/       Reusable UI components (SearchCard, TeamCard)
│   ├── pages/            Page-level components (Home)
│   ├── App.jsx           Root component
│   ├── main.jsx          Entry point
│   └── index.css         Tailwind import and global styles
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
| `npm run build` | Build for production into `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint |
