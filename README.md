# OpenSOC SaaS v6 – Production Hardening Starter

This package is a production-style hardening upgrade for an OpenSOC multi-tenant SaaS layer around Wazuh.

## What's new in v6
- Real Alembic-ready initial migration file and migration helper commands
- OIDC login endpoints scaffolded with Authlib for enterprise SSO
- Background worker with retry queue and dead-letter queue for notifications
- Periodic Wazuh sync worker hooks with tenant-aware sync jobs
- Secret rotation endpoint for tenant integrations
- Readiness, liveness, and operational metrics endpoints
- Stronger audit logging around sync, notification, and secret rotation events
- Optional tenant-scoped policy config model for future enforcement
- Frontend admin console upgraded for ops visibility

## Quick start
1. Copy `.env.example` to `.env`
2. Generate secrets:
   ```bash
   python - <<'PY'
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   PY
   ```
3. Put the generated value into `FERNET_KEY`
4. Set `JWT_SECRET` and your Wazuh / SMTP / OIDC values
5. Start the stack:
   ```bash
   docker compose up --build
   ```
6. API: `http://localhost:8000`
7. Frontend: `http://localhost:5173`
8. Reverse proxy: `http://localhost:8080`

## Default credentials
- `admin@example.com`
- `ChangeMe123!`

Change them immediately.

## Useful endpoints
- `GET /health/live`
- `GET /health/ready`
- `GET /api/ops/metrics`
- `GET /api/ops/jobs/dead-letter`
- `POST /api/ops/rotate-secret/{provider}`
- `GET /api/auth/oidc/login`

## Notes
- This is a hardened starter, not a finished enterprise product.
- OIDC needs provider-specific metadata and redirect configuration.
- For self-signed lab certificates set `WAZUH_VERIFY_SSL=false`, but use trusted certificates in production.
- The worker uses Redis queues with retry and dead-letter handling.
