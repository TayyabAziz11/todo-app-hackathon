---
id: "0019"
title: "Oracle Cloud OKE Deployment Complete"
stage: green
date: "2026-02-08"
surface: agent
model: claude-sonnet-4-5-20250929
feature: "005-name-phase5-cloud"
branch: 005-name-phase5-cloud
user: tayyab
command: "/sp.implement (continued)"
labels: ["oracle-cloud", "kubernetes", "helm", "deployment", "nat-gateway", "oke", "docker"]
links:
  spec: "specs/005-name-phase5-cloud/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - helm/todo-app-oracle/Chart.yaml
  - helm/todo-app-oracle/values.yaml
  - helm/todo-app-oracle/values-oracle.yaml
  - helm/todo-app-oracle/templates/_helpers.tpl
  - helm/todo-app-oracle/templates/namespace.yaml
  - helm/todo-app-oracle/templates/backend-deployment.yaml
  - helm/todo-app-oracle/templates/backend-service.yaml
  - helm/todo-app-oracle/templates/frontend-deployment.yaml
  - helm/todo-app-oracle/templates/frontend-service.yaml
  - backend/app/database.py
tests:
  - "curl POST /api/auth/register → 200 + JWT"
  - "curl POST /api/{user_id}/tasks → task created (id=30)"
  - "kubectl get pods -n todo-app → both 1/1 Running"
  - "TCP port 5432 to Neon PostgreSQL → open"
---

## Prompt

Continue Oracle Cloud (OKE) deployment. Fix pod internet access so backend can connect to Neon PostgreSQL. User confirmed: "yes do also read how to in means what specs hacathon read this :Hackathon II - Todo Spec-Driven Development.md and also use context7 how to do"

## Response

Successfully deployed Todo App to Oracle Kubernetes Engine (OKE) Free Tier with full end-to-end validation.

### Steps Completed

1. **Helm charts created** for monolithic app (not the Dapr microservices):
   - Backend (FastAPI) as ClusterIP
   - Frontend (Next.js) as LoadBalancer
   - Images: `docker.io/tayyabaziz11/todo-backend:v5.0.0-oracle` and `docker.io/tayyabaziz11/todo-frontend:v5.0.0-oracle`

2. **Docker images built and pushed** to Docker Hub with `v5.0.0-oracle` tag

3. **Fixed issues**:
   - Image pull: Added `docker.io/` prefix (CRI-O short name enforcement)
   - Backend startup blocking: Added `connect_timeout: 10` to SQLAlchemy engine
   - CORS updated to `http://129.151.136.242`

4. **Fixed pod internet access** (critical):
   - Created NAT Gateway: `ocid1.natgateway.oc1.me-abudhabi-1.aaaaaaaa4ul3rhl2bodiwjoflgwcpm4sakjjusc5627vsrfw6w4j5f7wq2zq`
   - Created new route table `oke-node-routetable-nat` routing `0.0.0.0/0` via NAT Gateway
   - Updated node subnet (`10.0.10.0/24`) to use this route table
   - Kept existing Internet Gateway route table for K8s API endpoint and LB subnets

5. **Validated end-to-end**:
   - User registration works (JWT returned)
   - Task creation works (task ID 30 created)
   - Frontend accessible at `http://129.151.136.242`
   - Backend connected to Neon PostgreSQL (tables created on startup)

### Final State
- Public URL: `http://129.151.136.242`
- Frontend: Running 1/1
- Backend: Running 1/1, connected to Neon DB
- Cluster: `taskflow-cluster` in `me-abudhabi-1` (OKE Free Tier)
