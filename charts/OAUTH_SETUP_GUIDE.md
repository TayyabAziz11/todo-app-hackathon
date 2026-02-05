# OAuth Setup Guide for Todo App

## Overview

This guide explains how to configure Google and GitHub OAuth login for your Todo application in both local development and dev cluster environments.

## Prerequisites

1. **Google OAuth Credentials**
   - Go to: https://console.cloud.google.com/
   - Create or select a project
   - Enable Google+ API
   - Create OAuth 2.0 Client ID
   - Application type: Web application

2. **GitHub OAuth App**
   - Go to: https://github.com/settings/developers
   - Click "New OAuth App"
   - Register your application

## OAuth Configuration

### Local Development (port-forward)

#### 1. Configure OAuth Providers

**Google Cloud Console:**
- Add authorized redirect URI:
  ```
  http://localhost:3000/auth/google/callback
  ```

**GitHub OAuth App:**
- Set Authorization callback URL:
  ```
  http://localhost:3000/auth/github/callback
  ```

#### 2. Update values-local.yaml

The OAuth credentials are already configured in `charts/todo-backend/values-local.yaml`:

```yaml
localSecrets:
  googleClientId: "your-google-client-id.apps.googleusercontent.com"
  googleClientSecret: "your-google-client-secret"
  githubClientId: "your-github-client-id"
  githubClientSecret: "your-github-client-secret"

oauthRedirectUris:
  google: "http://localhost:3000/auth/google/callback"
  github: "http://localhost:3000/auth/github/callback"
```

**⚠️ Security Note:** Never commit real OAuth credentials to version control in production!

#### 3. Deploy Configuration

```bash
# Upgrade Helm release
helm upgrade todo-backend charts/todo-backend \
  -f charts/todo-backend/values.yaml \
  -f charts/todo-backend/values-local.yaml \
  -n todo-dev

# Restart deployment
kubectl rollout restart deployment/todo-backend -n todo-dev
kubectl rollout status deployment/todo-backend -n todo-dev
```

#### 4. Verify Environment Variables

```bash
# Check OAuth credentials
kubectl exec -n todo-dev deployment/todo-backend -- env | grep -E "GOOGLE|GITHUB"
```

**Expected Output:**
```
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:3000/auth/github/callback
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

---

### Dev Cluster (with Ingress)

#### 1. Configure OAuth Providers

**Google Cloud Console:**
- Add authorized redirect URI:
  ```
  https://todo-dev.example.com/auth/google/callback
  ```
  Replace `todo-dev.example.com` with your actual domain.

**GitHub OAuth App:**
- Set Authorization callback URL:
  ```
  https://todo-dev.example.com/auth/github/callback
  ```
  Replace `todo-dev.example.com` with your actual domain.

#### 2. Update values-dev.yaml

Edit `charts/todo-backend/values-dev.yaml` and update the domain:

```yaml
oauthRedirectUris:
  google: "https://todo-dev.example.com/auth/google/callback"
  github: "https://todo-dev.example.com/auth/github/callback"
```

#### 3. Create Kubernetes Secret

For dev cluster, create the OAuth secret manually:

```bash
kubectl create secret generic todo-backend-secrets \
  --namespace=todo-dev \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=SECRET_KEY='your-jwt-secret-key-min-32-chars' \
  --from-literal=OPENAI_API_KEY='sk-your-openai-api-key' \
  --from-literal=GOOGLE_CLIENT_ID='your-google-client-id.apps.googleusercontent.com' \
  --from-literal=GOOGLE_CLIENT_SECRET='your-google-client-secret' \
  --from-literal=GITHUB_CLIENT_ID='your-github-client-id' \
  --from-literal=GITHUB_CLIENT_SECRET='your-github-client-secret'
```

**Or use external secret managers:**
- Sealed Secrets
- External Secrets Operator
- HashiCorp Vault
- Cloud provider secret managers (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)

#### 4. Deploy Configuration

```bash
# Upgrade Helm release for dev cluster
helm upgrade todo-backend charts/todo-backend \
  -f charts/todo-backend/values.yaml \
  -f charts/todo-backend/values-dev.yaml \
  -n todo-dev

# Restart deployment
kubectl rollout restart deployment/todo-backend -n todo-dev
```

---

## Testing OAuth Login

### Local Development (port-forward)

**Prerequisites:**
```bash
# Terminal 1 - Backend
kubectl port-forward -n todo-dev svc/todo-backend 8000:8000

# Terminal 2 - Frontend
kubectl port-forward -n todo-dev svc/todo-frontend 3000:3000
```

**Test Steps:**

1. **Open Application:**
   - Navigate to: `http://localhost:3000`

2. **Test Google OAuth:**
   - Click "Sign in with Google" button
   - Should redirect to: `https://accounts.google.com/o/oauth2/v2/auth?...`
   - After Google consent, redirects to: `http://localhost:3000/auth/google/callback`
   - Backend exchanges code for user info
   - User logged in, JWT token in localStorage

3. **Test GitHub OAuth:**
   - Click "Sign in with GitHub" button
   - Should redirect to: `https://github.com/login/oauth/authorize?...`
   - After GitHub authorization, redirects to: `http://localhost:3000/auth/github/callback`
   - Backend exchanges code for user info
   - User logged in, JWT token in localStorage

4. **Verify in Browser Console (F12):**
   ```javascript
   localStorage.getItem('token')  // Should return JWT token
   ```

### Dev Cluster (with Ingress)

**Test Steps:**

1. **Open Application:**
   - Navigate to: `https://todo-dev.example.com`

2. **Test OAuth Login:**
   - Click "Sign in with Google" or "Sign in with GitHub"
   - OAuth flow should complete successfully
   - User logged in with JWT token

---

## Verification Commands

### Check OAuth Endpoints

**Test Google OAuth URL generation:**
```bash
kubectl exec -n todo-dev deployment/todo-backend -- \
  curl -s http://localhost:8000/api/auth/google/url
```

**Expected Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=your-google-client-id.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fgoogle%2Fcallback&...",
  "provider": "google"
}
```

**Test GitHub OAuth URL generation:**
```bash
kubectl exec -n todo-dev deployment/todo-backend -- \
  curl -s http://localhost:8000/api/auth/github/url
```

**Expected Response:**
```json
{
  "auth_url": "https://github.com/login/oauth/authorize?client_id=your-github-client-id&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fgithub%2Fcallback&...",
  "provider": "github"
}
```

### Check Backend Logs

**Monitor OAuth login attempts:**
```bash
kubectl logs -n todo-dev deployment/todo-backend -f | grep -i "oauth\|google\|github"
```

### Check Environment Variables

**Verify all OAuth variables:**
```bash
kubectl exec -n todo-dev deployment/todo-backend -- env | \
  grep -E "GOOGLE|GITHUB|FRONTEND_URL|CORS" | sort
```

---

## Troubleshooting

### Error: "OAuth is not configured"

**Cause:** OAuth credentials not set in environment variables

**Solution:**
```bash
# 1. Verify secret exists
kubectl get secret todo-backend-secrets -n todo-dev

# 2. Check secret contains OAuth keys
kubectl describe secret todo-backend-secrets -n todo-dev

# 3. Verify environment variables in pod
kubectl exec -n todo-dev deployment/todo-backend -- env | grep GOOGLE

# 4. If missing, restart deployment
kubectl rollout restart deployment/todo-backend -n todo-dev
```

### Error: "redirect_uri_mismatch"

**Cause:** Redirect URI in request doesn't match configured URI in OAuth provider

**Solution:**

1. **Check backend redirect URI:**
   ```bash
   kubectl exec -n todo-dev deployment/todo-backend -- \
     env | grep REDIRECT_URI
   ```

2. **Update OAuth provider settings:**
   - Google: https://console.cloud.google.com/ → Credentials → Edit OAuth 2.0 Client
   - GitHub: https://github.com/settings/developers → Edit OAuth App

3. **Ensure redirect URIs match exactly:**
   - Local: `http://localhost:3000/auth/{provider}/callback`
   - Dev: `https://your-domain.com/auth/{provider}/callback`

### OAuth Login Completes but User Not Created

**Cause:** Database connection issue or missing user table

**Solution:**
```bash
# 1. Check backend logs
kubectl logs -n todo-dev deployment/todo-backend --tail=100

# 2. Verify database connection
kubectl exec -n todo-dev deployment/todo-backend -- env | grep DATABASE_URL

# 3. Check if user table exists
kubectl exec -n todo-dev deployment/todo-backend -- \
  curl -s http://localhost:8000/health
```

### CORS Errors During OAuth Callback

**Cause:** CORS_ORIGINS doesn't include frontend URL

**Solution:**
```bash
# 1. Check CORS configuration
kubectl exec -n todo-dev deployment/todo-backend -- env | grep CORS

# 2. Ensure CORS includes frontend URL
# For local: http://localhost:3000
# For dev: https://todo-dev.example.com

# 3. Update values-local.yaml or values-dev.yaml if needed
helm upgrade todo-backend charts/todo-backend \
  -f charts/todo-backend/values.yaml \
  -f charts/todo-backend/values-local.yaml \
  -n todo-dev
```

---

## Environment Variables Reference

### Required OAuth Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 Client ID | `123456-abc.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret | `GOCSPX-...` |
| `GOOGLE_REDIRECT_URI` | Google OAuth callback URL | `http://localhost:3000/auth/google/callback` |
| `GITHUB_CLIENT_ID` | GitHub OAuth App Client ID | `Ov23liVpPJiFDXwoyCiW` |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App Client Secret | `6b64364b6c9a207a7551e98e63c5931d9bc6dc07` |
| `GITHUB_REDIRECT_URI` | GitHub OAuth callback URL | `http://localhost:3000/auth/github/callback` |

### Related Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FRONTEND_URL` | Frontend application URL | `http://localhost:3000` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,...` |
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars) | `your-secret-key...` |
| `DATABASE_URL` | Database connection string | `postgresql://...` |

---

## Security Best Practices

### 1. Never Commit Secrets to Git

```bash
# Add to .gitignore
charts/todo-backend/values-production.yaml
charts/todo-backend/secrets.yaml
*.secret.yaml
.env
```

### 2. Use External Secret Managers

**For production, use:**
- Sealed Secrets (Kubernetes-native)
- External Secrets Operator (multi-cloud)
- HashiCorp Vault (enterprise)
- Cloud provider secret managers

### 3. Rotate OAuth Credentials Regularly

- Google: Regenerate client secret every 90 days
- GitHub: Rotate client secret periodically
- Update Kubernetes Secret after rotation

### 4. Restrict OAuth Scopes

**Google OAuth:**
- Only request: `openid`, `email`, `profile`
- Don't request unnecessary permissions

**GitHub OAuth:**
- Only request: `read:user`, `user:email`
- Don't request `repo` or `admin` scopes unless needed

### 5. Validate Redirect URIs

- Always use HTTPS in production
- Never use wildcards in redirect URIs
- Validate state parameter to prevent CSRF

---

## Summary

✅ **OAuth Configuration Complete**

**Local Development:**
- Google OAuth: ✅ Configured
- GitHub OAuth: ✅ Configured
- Redirect URIs: ✅ `http://localhost:3000/auth/{provider}/callback`
- Environment Variables: ✅ Injected via Kubernetes Secret
- Testing: ✅ Ready via port-forward

**Dev Cluster:**
- OAuth Redirect URIs: ✅ Template in values-dev.yaml
- Secret Creation: ✅ Documented (manual or external secret manager)
- Deployment: ✅ Ready via Helm upgrade

**Next Steps:**
1. Start port-forward sessions (backend and frontend)
2. Open `http://localhost:3000` in browser
3. Test Google and GitHub OAuth login
4. Verify JWT token in localStorage
5. For dev cluster: Update domain in values-dev.yaml and create secret

**Files Modified:**
- `charts/todo-backend/values.yaml` - Added OAuth structure
- `charts/todo-backend/values-local.yaml` - Added OAuth credentials and redirect URIs
- `charts/todo-backend/values-dev.yaml` - Added OAuth configuration for dev cluster
- `charts/todo-backend/templates/configmap.yaml` - Added redirect URI injection
- `charts/todo-backend/templates/deployment.yaml` - Added OAuth env var injection
- `charts/todo-backend/templates/secret-local.yaml` - Added OAuth secrets

**Support:**
- For issues, check backend logs: `kubectl logs -n todo-dev deployment/todo-backend -f`
- Verify environment variables: `kubectl exec -n todo-dev deployment/todo-backend -- env | grep GOOGLE`
- Test OAuth endpoints: `/api/auth/google/url` and `/api/auth/github/url`
