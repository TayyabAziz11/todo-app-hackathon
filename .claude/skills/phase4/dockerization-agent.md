# Dockerization Agent Skill

**Skill Name**: `dockerization-agent`
**Category**: Phase IV - Container Infrastructure
**Purpose**: Containerize the Phase III Todo Chatbot frontend and backend for Kubernetes deployment
**Version**: 1.0.0
**Created**: 2026-02-03

---

## Role

Containerize the Phase III Todo Chatbot frontend and backend using AI-assisted tools to create production-ready Docker images for Kubernetes deployment.

## Responsibilities

- Analyze application structure and dependencies
- Use Docker AI Agent (Gordon) when available
- Generate Dockerfiles via AI only (no manual authoring)
- Build and tag Docker images with semantic versioning
- Ensure Kubernetes compatibility (ports, env vars, health checks)
- Optimize images for size and security
- Create multi-stage builds where appropriate
- Document build process and image metadata

## Applicable Agents

- **Primary**: dockerization-agent
- **Supporting**: infra-spec-guardian (validation), phase-iv-orchestrator (coordination)
- **Context**: Infrastructure preparation phase, before Kubernetes deployment

## Input

- Application codebase (frontend and backend)
- Dependency manifests (package.json, requirements.txt, etc.)
- Runtime requirements and environment variables
- Port mappings and service endpoints
- Build-time vs runtime dependency separation needs

## Output

- **Dockerfiles** (AI-generated):
  - Well-commented, explaining each significant layer
  - Optimized for layer caching
  - Multi-stage builds for size optimization
  - Security best practices (non-root user, minimal attack surface)

- **Build Commands**:
  - Docker build commands with appropriate tags
  - Multi-platform build instructions (if needed)
  - BuildKit optimizations enabled
  - Cache mounting strategies

- **Image Names and Tags**:
  - Semantic versioning tags (e.g., v1.0.0, latest, stable)
  - Registry naming conventions (registry/namespace/service:tag)
  - Image labeling with metadata (version, git commit, build date)

- **.dockerignore Files**:
  - Exclude unnecessary files (node_modules, .git, test files)
  - Minimize image size and build context

- **Documentation**:
  - Build instructions with prerequisites
  - Environment variable requirements
  - Port mappings and exposed services
  - Volume mount recommendations
  - Health check endpoints

## Scope & Boundaries

### Can Do
- Analyze service architecture and dependencies
- Use Docker AI (Gordon) to generate optimized Dockerfiles
- Implement multi-stage builds for minimal image sizes
- Apply security hardening (non-root users, minimal layers)
- Create build scripts and automation
- Document container specifications
- Ensure Kubernetes readiness (health checks, 12-factor compliance)

### Cannot Do
- Manually write Dockerfiles (must use AI-assisted tools)
- Deploy containers to any environment
- Run or orchestrate containers
- Bypass infra-spec-guardian validation
- Include secrets or credentials in images

## Constraints

- **No Manual Dockerfile Writing**: All Dockerfiles must be AI-generated (Gordon preferred, Claude fallback)
- **Do Not Deploy Containers**: Only create images, do not run or deploy
- **Images Must Be Reusable**: Design for Helm deployments and Kubernetes environments
- **Security First**: Non-root users, no hardcoded secrets, minimal attack surface
- **Kubernetes Compatibility**: Health endpoints, graceful shutdown, environment-based config

## Reusability Notes

- Pattern reusable for any microservice containerization
- Template for frontend (Next.js) and backend (FastAPI) services
- Applicable to Phase IV and future deployment phases
- Standardized approach for all container creation

## Dependencies

- Docker AI Agent (Gordon) - preferred path
- Claude Code - fallback for Dockerfile generation
- Phase III codebase (frontend and backend)
- Application dependency files (package.json, requirements.txt)
- infra-spec-guardian for validation

## Quality Expectations

### Dockerfile Quality
- [ ] Specific base image versions (no 'latest' tag)
- [ ] Multi-stage builds implemented where beneficial
- [ ] Non-root user configured in final stage
- [ ] .dockerignore excludes unnecessary files
- [ ] Layer ordering optimizes caching (dependencies before code)
- [ ] Health check strategy documented
- [ ] Environment variables documented with examples
- [ ] No secrets or credentials in any layer

### Image Quality
- [ ] Minimal image size (alpine variants where possible)
- [ ] Security best practices applied
- [ ] Proper labeling with metadata
- [ ] Semantic versioning tags
- [ ] Reproducible builds (pinned dependency versions)

### Kubernetes Readiness
- [ ] Health check endpoints exposed (liveness, readiness probes)
- [ ] Graceful shutdown handling (SIGTERM signals)
- [ ] 12-factor app compliance (environment-based configuration)
- [ ] No hardcoded environment-specific values
- [ ] Proper signal handling and PID 1 awareness

## Execution Workflow

### Step 1: Service Analysis
Before creating any Docker configurations:
1. Identify all services that need containerization (frontend, backend)
2. Analyze language/framework requirements and runtime dependencies
3. Review existing package managers (package.json, requirements.txt)
4. Identify build-time vs runtime dependencies
5. Check for environment-specific configurations

### Step 2: Gordon Integration (Preferred Path)
When Docker AI Agent (Gordon) is available:
1. Use Gordon to analyze the codebase and generate optimized Dockerfiles
2. Leverage Gordon's recommendations for base images, layer optimization, and security
3. Request Gordon to validate multi-stage build configurations
4. Have Gordon suggest best practices for the specific tech stack

### Step 3: Claude Code Fallback (When Gordon Unavailable)
If Gordon is not available:
1. Generate Dockerfiles using Claude Code following industry best practices
2. Use official, minimal base images (alpine variants when possible)
3. Implement multi-stage builds to minimize image size
4. Apply security hardening (non-root users, minimal layers)
5. Include .dockerignore files to exclude unnecessary files

### Step 4: Build and Tag
1. Create build commands with semantic versioning
2. Tag images appropriately (version, latest, stable)
3. Include metadata labels (git commit, build date, version)
4. Document build process

### Step 5: Validation
1. Submit to infra-spec-guardian for compliance check
2. Verify Kubernetes readiness criteria
3. Test build process locally
4. Document any deviations or special requirements

## Example Use Case

```
Context: Containerizing Phase III Todo Chatbot backend (FastAPI)

Input:
  - Backend: Python FastAPI application
  - Dependencies: requirements.txt with FastAPI, uvicorn, SQLModel
  - Port: 8000
  - Environment Variables: DATABASE_URL, SECRET_KEY, CORS_ORIGINS

Execution:

1. Service Analysis:
   - Language: Python 3.11+
   - Framework: FastAPI with uvicorn
   - Build deps: None (no compilation)
   - Runtime deps: requirements.txt

2. Gordon Generation (if available):
   "Gordon, create optimized Dockerfile for Python FastAPI app with:
    - Python 3.11-slim base
    - requirements.txt at /app/requirements.txt
    - app code at /app
    - expose port 8000
    - non-root user
    - health check at /health"

3. Output Dockerfile (AI-generated):
   ```dockerfile
   # Build stage
   FROM python:3.11-slim as builder
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir --user -r requirements.txt

   # Runtime stage
   FROM python:3.11-slim
   WORKDIR /app

   # Copy dependencies from builder
   COPY --from=builder /root/.local /root/.local
   ENV PATH=/root/.local/bin:$PATH

   # Create non-root user
   RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
   USER appuser

   # Copy application code
   COPY --chown=appuser:appuser . .

   # Expose port
   EXPOSE 8000

   # Health check
   HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
     CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

   # Run application
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

4. Build Command:
   ```bash
   docker build -t todo-backend:v1.0.0 \
     --label "version=1.0.0" \
     --label "git.commit=$(git rev-parse HEAD)" \
     --label "build.date=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     -f backend/Dockerfile \
     ./backend
   ```

5. Output Documentation:
   - Image: todo-backend:v1.0.0
   - Size: ~150MB (optimized)
   - Environment Variables Required:
     * DATABASE_URL (PostgreSQL connection string)
     * SECRET_KEY (JWT signing key)
     * CORS_ORIGINS (comma-separated origins)
   - Port: 8000
   - Health Check: GET /health
   - Non-root user: appuser (UID 1000)
```

## Technology-Specific Guidelines

### Python Services (FastAPI Backend)
- Use `python:3.11-slim` or `python:3.11-alpine`
- Implement requirements.txt caching before code copy
- Set `PYTHONUNBUFFERED=1` for proper logging
- Use `pip install --no-cache-dir` to reduce image size
- Multi-stage build to separate dependencies

### Node.js Services (Next.js Frontend)
- Use `node:18-alpine` variants
- Leverage package-lock.json for reproducible builds
- Run `npm ci` instead of `npm install` in production
- Clean npm cache after installation
- Multi-stage: build with Node, serve with nginx (for static export)

### Frontend Static Serving
- Use `nginx:alpine` for serving static builds
- Implement build stage with Node, serve stage with nginx
- Configure nginx for SPA routing if applicable
- Include security headers in nginx config

## Best Practices Enforced

1. **Multi-Stage Builds**: Separate build dependencies from runtime
2. **Layer Optimization**: Order instructions from least to most frequently changing
3. **Security First**: Non-root user, minimal attack surface, no secrets
4. **Size Matters**: Minimal image sizes, remove build artifacts
5. **Reproducibility**: Pin dependency versions, specific base image tags
6. **Health Checks**: Include HEALTHCHECK directives or document health endpoints
7. **Environment Awareness**: Use ENV for configuration, never hardcode values
8. **Signal Handling**: Ensure applications handle SIGTERM for graceful shutdown

## Integration with Phase IV Workflow

**Position in Workflow**:
```
Phase IV: spec → plan → tasks → [DOCKERIZATION] → Helm → K8s Deploy
```

**Coordination Points**:
1. After Phase III implementation complete
2. Before Helm chart creation
3. Validated by infra-spec-guardian
4. Used by helm-chart-architect for deployment config

---

**Status**: Active
**Maintained by**: Phase IV Infrastructure Team
**Last Updated**: 2026-02-03
