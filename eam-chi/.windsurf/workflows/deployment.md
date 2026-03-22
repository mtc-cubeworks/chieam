---
description: Deploy frontend and backend updates
---

# Deployment Workflow

This workflow describes how to pull latest changes, build, and restart both frontend and backend services.

## Steps

1. **Pull latest changes from main branch**
   ```bash
   cd /home/cwadmin/eam-tests/eam-2.1-fastapi-nextjs
   git stash  # Stash local changes if any
   git pull origin main
   ```

2. **Install dependencies and build frontend**
   ```bash
   cd frontend
   pnpm install
   NODE_ENV=production pnpm build
   ```

3. **Restart frontend systemd service**
   ```bash
   sudo systemctl restart eam-frontend.service
   ```

4. **Install dependencies and restart backend**
   ```bash
   cd ../backend
   pnpm install  # If dependencies changed
   sudo systemctl restart eam-backend.service
   ```

5. **Verify services are running**
   ```bash
   # Check frontend
   curl -I http://127.0.0.1:3010
   # Should return HTTP/1.1 200 OK
   
   # Check backend
   curl http://127.0.0.1:8010/health
   # Should return health status
   
   # Check systemd services
   sudo systemctl status eam-frontend.service --no-pager
   sudo systemctl status eam-backend.service --no-pager
   # Both services should be active (running)
   ```

## Important Notes

- **Frontend**: Uses systemd service (eam-frontend.service) with Nitro node-server preset
- **Backend**: Uses systemd service (eam-backend.service)
- **Configuration**: Frontend uses `/api` reverse proxy path to backend
- **Environment**: Always use `NODE_ENV=production` for builds
- **Stashing**: Use `git stash` before pull if you have local changes
- **Verification**: Always test the site after deployment
- **Persistence**: Both services survive SSH disconnect and system reboots

## Troubleshooting

If frontend fails to start:
- Check if `.output/server/index.mjs` exists
- Verify systemd logs: `sudo journalctl -u eam-frontend.service --since "5 min ago"`
- Check nuxt.config.ts has `nitro: { preset: 'node-server' }`
- Verify port 3010 is not in use: `sudo ss -ltnp | grep 3010`

If backend fails to start:
- Check systemd logs: `sudo journalctl -u eam-backend.service --since "5 min ago"`
- Verify backend is listening on 127.0.0.1:8010
- Check database connectivity

## Quick Commands

```bash
# Full deployment
cd /home/cwadmin/eam-tests/eam-2.1-fastapi-nextjs && \
git stash && git pull origin main && \
cd frontend && pnpm install && NODE_ENV=production pnpm build && \
sudo systemctl restart eam-frontend.service && \
cd ../backend && sudo systemctl restart eam-backend.service && \
echo "Deployment complete - test the site now"
```

```bash
# Restart services only (no rebuild)
sudo systemctl restart eam-frontend.service
sudo systemctl restart eam-backend.service
```
