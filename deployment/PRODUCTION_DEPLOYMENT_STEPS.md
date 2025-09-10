# MantraPath Initial Production Deployment (Phase 1 - Replace localhost)

Objective: Bring the stack online on an Ubuntu VM behind Nginx reachable at a real domain, eliminating user‑facing `localhost`.

## 1. Assumptions
- Ubuntu 22.04+ VM with sudo.
- Domain (e.g. `app.example.com`) pointed via DNS A record to server public IP.
- Docker + Docker Compose installed.
- You will terminate HTTP (initially) then add HTTPS with Certbot later.

## 2. Pull / Update Code
```
cd /opt/mantrapath   # or your chosen path
git clone <repo> .   # if not already
git pull             # if updating
```

## 3. Create Backend Env File
```
cp backend/.env.production.example backend/.env
vim backend/.env   # fill CHANGE_ME values, set DOMAIN, maybe PROTOCOL=http for now
```

Key edits:
- DOMAIN=app.example.com
- PROTOCOL=http (switch to https after cert install)
- SECRET_KEY / JWT_SECRET_KEY (generate strong values: `openssl rand -hex 48`)
- SMTP settings if email verification needed (or set SKIP_EMAIL_VERIFICATION=true temporarily)

## 4. Frontend Production Env
```
cp frontend/.env.production.example frontend/.env.production
vim frontend/.env.production  # set VITE_DOMAIN=app.example.com
```

## 5. Build Frontend
Install Node 18+ (or use container build):
```
cd frontend
npm ci
npm run build
```
Result: `frontend/dist/` static assets.

## 6. Nginx (Host Mode, Simple First Pass)
Serve the built frontend directly and reverse proxy API/WebSockets.

Create `/etc/nginx/sites-available/mantrapath`:
```
server {
    listen 80;
    server_name app.example.com;

    root /opt/mantrapath/frontend/dist;
    index index.html;

    # Static files (cache aggressively)
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        add_header Cache-Control "public, max-age=31536000, immutable";
        try_files $uri =404;
    }

    # SPA fallback
    location / {
        try_files $uri /index.html;
    }

    # API -> API Gateway
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSockets (Gateway WS listener on 8080)
    location /ws/ {
        proxy_pass http://127.0.0.1:8080/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health { return 200 'ok'; add_header Content-Type text/plain; }
}
```
Enable and test:
```
ln -s /etc/nginx/sites-available/mantrapath /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

## 7. Start Backend Stack
```
cd backend
docker compose -f docker-compose.prod.yml --env-file .env up -d --build postgres redis nats
# (Optional) wait for health
docker compose ps

# Start core services
docker compose -f docker-compose.prod.yml --env-file .env up -d api-gateway auth-service profile-service mood-service chatbot-service community-service notification-service ml-service models-service translation-service voice-service ai-context-store action-orchestrator memory-service
```

Check health:
```
curl http://127.0.0.1:8000/health/live
curl http://127.0.0.1:8000/docs | head
```

## 8. Verify Frontend
Open: `http://app.example.com` (should load SPA)
Network tab: API calls should target `http://app.example.com/api/...`

## 9. Add HTTPS (Later)
```
apt install -y certbot python3-certbot-nginx
certbot --nginx -d app.example.com --redirect
```
Set PROTOCOL=https in backend `.env` + rebuild any services needing APP_URL; rebuild frontend with `VITE_PROTOCOL=https`.

## 10. Remove Remaining localhost References (Next Phase)
Planned work:
1. Replace hard-coded `http://localhost:PORT` in frontend source with env-driven (VITE_) constants.
2. Replace backend defaults (e.g. `APP_URL` fallback in `shared/auth.py`).
3. Update scripts & docs.
4. Optionally containerize Nginx + frontend into compose to avoid host coupling.

## 11. Troubleshooting Quick List
| Symptom | Check |
|---------|-------|
| 502 from Nginx | Is api-gateway container healthy? `docker compose logs api-gateway` |
| WebSockets failing | Ensure port 8080 published & proxied; check Upgrade headers |
| Email links point to localhost | Confirm APP_URL & restart auth-service |
| CORS errors | Add domain to CORS_ORIGINS or set wildcard temporarily |

---
Phase 1 complete when: domain serves frontend, API reachable at /api, WebSockets connect, no user-facing localhost.
