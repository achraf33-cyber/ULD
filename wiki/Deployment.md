# Deployment

## Environment

Copy `.env.example` → `.env`:

- `DASHBOARD_LLAMACTL_KEY` — llamactl management bearer token
- Intel paths, `intel_conf`, service prefix

## Manual run

```bash
cd frontend && npm install && npm run build
# output → backend/frontend_dist

cd backend && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

## Systemd

```bash
cp deploy/llama-dashboard.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now llama-dashboard
```

Service runs from `/root/llama-dashboard` with `.env` loaded.

## After code changes

```bash
cd frontend && npm run build   # writes to backend/frontend_dist
ruff check backend/app
systemctl restart llama-dashboard
```

## Gitea

- Remote: `http://192.168.10.14/achraf/llama-dashboard.git`
- Push triggers CI on `main`
- Wiki: see [wiki/README.md](../wiki/README.md)
