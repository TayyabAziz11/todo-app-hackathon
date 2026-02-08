# ArgoCD Hello World Example

Complete GitOps repository structure for deploying your first app with ArgoCD.

## Structure

```
hello-world/
├── k8s/
│   ├── deployment.yaml    # Application deployment
│   └── service.yaml       # Service definition
├── application.yaml       # ArgoCD Application manifest
└── README.md
```

## Quick Start

1. **Push to Git:**
   ```bash
   # Initialize Git repo
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR-ORG/YOUR-REPO.git
   git push -u origin main
   ```

2. **Update application.yaml:**
   ```yaml
   source:
     repoURL: https://github.com/YOUR-ORG/YOUR-REPO.git  # Your repo URL
   ```

3. **Deploy with ArgoCD:**
   ```bash
   # Apply the Application manifest
   kubectl apply -f application.yaml

   # Or use CLI
   argocd app create hello-app \
     --repo https://github.com/YOUR-ORG/YOUR-REPO.git \
     --path k8s \
     --dest-namespace default \
     --dest-server https://kubernetes.default.svc \
     --sync-policy automated \
     --auto-prune \
     --self-heal
   ```

4. **Watch deployment:**
   ```bash
   argocd app get hello-app
   argocd app sync hello-app  # If not using auto-sync
   ```

5. **Access the app:**
   ```bash
   kubectl port-forward svc/hello-app 8080:80
   # Visit http://localhost:8080
   ```

## GitOps Workflow

1. Update `k8s/deployment.yaml` (e.g., change replicas or image tag)
2. Commit and push to Git
3. ArgoCD automatically detects changes and syncs (if auto-sync enabled)
4. Verify deployment: `argocd app get hello-app`
