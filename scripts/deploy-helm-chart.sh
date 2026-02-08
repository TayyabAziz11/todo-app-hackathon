#!/bin/bash

##############################################################################
# Helm Chart Deployment Script for Todo App Phase V.1
#
# This script automates the deployment of Todo App microservices using Helm
# with comprehensive validation and error handling.
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="todo-app-dev"
RELEASE_NAME="todo-app"
CHART_PATH="./helm/todo-app"
VALUES_FILE="values-minikube.yaml"

##############################################################################
# Helper Functions
##############################################################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    fi
    print_success "$1 is installed"
    return 0
}

##############################################################################
# Prerequisite Checks
##############################################################################

check_prerequisites() {
    print_header "Checking Prerequisites"

    local all_good=true

    # Check required commands
    check_command "kubectl" || all_good=false
    check_command "helm" || all_good=false
    check_command "dapr" || all_good=false

    # Check Kubernetes cluster
    if kubectl cluster-info &> /dev/null; then
        print_success "Kubernetes cluster is accessible"
    else
        print_error "Cannot access Kubernetes cluster"
        all_good=false
    fi

    # Check Dapr installation
    if dapr status -k &> /dev/null; then
        print_success "Dapr is installed in cluster"
    else
        print_error "Dapr is not installed in cluster"
        print_info "Run: dapr init -k"
        all_good=false
    fi

    # Check Helm version
    helm_version=$(helm version --short 2>/dev/null | grep -o 'v[0-9]*' | cut -c2-)
    if [ "$helm_version" -ge 3 ]; then
        print_success "Helm version 3+ detected"
    else
        print_error "Helm version 3+ required"
        all_good=false
    fi

    if [ "$all_good" = false ]; then
        print_error "Prerequisites check failed"
        exit 1
    fi

    print_success "All prerequisites satisfied"
}

##############################################################################
# Namespace Setup
##############################################################################

setup_namespace() {
    print_header "Setting Up Namespace"

    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        print_info "Namespace $NAMESPACE already exists"
    else
        print_info "Creating namespace $NAMESPACE"
        kubectl create namespace "$NAMESPACE"
        print_success "Namespace created"
    fi

    # Label namespace for Dapr
    kubectl label namespace "$NAMESPACE" istio-injection=disabled --overwrite 2>/dev/null || true
    print_success "Namespace configured"
}

##############################################################################
# Docker Images Validation
##############################################################################

check_docker_images() {
    print_header "Validating Docker Images"

    local services=("todo-service" "user-service" "chat-service" "notification-service" "audit-service" "analytics-service")
    local missing_images=()

    # Use Minikube's Docker daemon if available
    if command -v minikube &> /dev/null; then
        eval $(minikube docker-env 2>/dev/null) || true
    fi

    for service in "${services[@]}"; do
        if docker images | grep -q "${service}.*dev"; then
            print_success "Image ${service}:dev found"
        else
            print_warning "Image ${service}:dev not found"
            missing_images+=("$service")
        fi
    done

    if [ ${#missing_images[@]} -gt 0 ]; then
        print_warning "Missing images: ${missing_images[*]}"
        print_info "Build images first or deployment will fail"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "All required images are available"
    fi
}

##############################################################################
# Helm Chart Validation
##############################################################################

validate_chart() {
    print_header "Validating Helm Chart"

    # Check chart exists
    if [ ! -d "$CHART_PATH" ]; then
        print_error "Chart directory not found: $CHART_PATH"
        exit 1
    fi
    print_success "Chart directory found"

    # Check Chart.yaml
    if [ ! -f "$CHART_PATH/Chart.yaml" ]; then
        print_error "Chart.yaml not found"
        exit 1
    fi
    print_success "Chart.yaml found"

    # Check values file
    if [ ! -f "$CHART_PATH/$VALUES_FILE" ]; then
        print_error "Values file not found: $VALUES_FILE"
        exit 1
    fi
    print_success "Values file found"

    # Lint chart
    print_info "Running Helm lint..."
    if helm lint "$CHART_PATH" -f "$CHART_PATH/$VALUES_FILE"; then
        print_success "Chart passed lint checks"
    else
        print_error "Chart failed lint checks"
        exit 1
    fi

    # Dry run
    print_info "Running dry-run..."
    if helm install "$RELEASE_NAME" "$CHART_PATH" \
        -f "$CHART_PATH/$VALUES_FILE" \
        -n "$NAMESPACE" \
        --dry-run --debug > /dev/null 2>&1; then
        print_success "Dry-run successful"
    else
        print_error "Dry-run failed"
        print_info "Run manually to see errors: helm install $RELEASE_NAME $CHART_PATH -f $CHART_PATH/$VALUES_FILE -n $NAMESPACE --dry-run --debug"
        exit 1
    fi
}

##############################################################################
# Helm Deployment
##############################################################################

deploy_chart() {
    print_header "Deploying Helm Chart"

    # Check if release already exists
    if helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
        print_warning "Release $RELEASE_NAME already exists"
        read -p "Upgrade existing release? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Upgrading release..."
            helm upgrade "$RELEASE_NAME" "$CHART_PATH" \
                -f "$CHART_PATH/$VALUES_FILE" \
                -n "$NAMESPACE" \
                --wait \
                --timeout 5m
            print_success "Release upgraded successfully"
        else
            print_info "Skipping deployment"
            return 0
        fi
    else
        print_info "Installing release..."
        helm install "$RELEASE_NAME" "$CHART_PATH" \
            -f "$CHART_PATH/$VALUES_FILE" \
            -n "$NAMESPACE" \
            --wait \
            --timeout 5m
        print_success "Release installed successfully"
    fi

    # Show release status
    helm status "$RELEASE_NAME" -n "$NAMESPACE"
}

##############################################################################
# Post-Deployment Validation
##############################################################################

validate_deployment() {
    print_header "Validating Deployment"

    print_info "Waiting for pods to be ready (max 2 minutes)..."

    local timeout=120
    local elapsed=0
    local interval=5

    while [ $elapsed -lt $timeout ]; do
        local not_ready=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -v "Running\|Completed" | wc -l)
        local total=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)

        if [ "$not_ready" -eq 0 ] && [ "$total" -gt 0 ]; then
            print_success "All pods are ready"
            break
        fi

        print_info "Waiting... ($elapsed/$timeout seconds) - $not_ready/$total pods not ready"
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    # Show pod status
    echo ""
    print_info "Pod Status:"
    kubectl get pods -n "$NAMESPACE"

    echo ""
    print_info "Service Status:"
    kubectl get svc -n "$NAMESPACE"

    # Check for Dapr sidecars
    echo ""
    print_info "Checking Dapr Sidecars:"
    local pods=$(kubectl get pods -n "$NAMESPACE" -o name 2>/dev/null)
    for pod in $pods; do
        local containers=$(kubectl get "$pod" -n "$NAMESPACE" -o jsonpath='{.spec.containers[*].name}' 2>/dev/null)
        if echo "$containers" | grep -q "daprd"; then
            print_success "$pod has Dapr sidecar"
        else
            print_warning "$pod missing Dapr sidecar"
        fi
    done
}

##############################################################################
# Usage Instructions
##############################################################################

print_usage_instructions() {
    print_header "Deployment Complete!"

    cat << EOF
${GREEN}✓ Todo App has been successfully deployed to Kubernetes${NC}

${BLUE}Quick Start Commands:${NC}

1. Check deployment status:
   ${YELLOW}kubectl get pods -n $NAMESPACE${NC}
   ${YELLOW}kubectl get svc -n $NAMESPACE${NC}

2. View logs for a service:
   ${YELLOW}kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=todo-service -c todo-service${NC}
   ${YELLOW}kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=todo-service -c daprd${NC}

3. Port-forward to access services:
   ${YELLOW}kubectl port-forward -n $NAMESPACE svc/todo-service 8000:8000${NC}
   ${YELLOW}kubectl port-forward -n $NAMESPACE svc/user-service 8001:8000${NC}

4. Test service health:
   ${YELLOW}curl http://localhost:8000/health/ready${NC}
   ${YELLOW}curl http://localhost:8000/health/live${NC}

5. View Helm release info:
   ${YELLOW}helm status $RELEASE_NAME -n $NAMESPACE${NC}
   ${YELLOW}helm get values $RELEASE_NAME -n $NAMESPACE${NC}

6. Upgrade deployment:
   ${YELLOW}helm upgrade $RELEASE_NAME $CHART_PATH -f $CHART_PATH/$VALUES_FILE -n $NAMESPACE${NC}

7. Uninstall:
   ${YELLOW}helm uninstall $RELEASE_NAME -n $NAMESPACE${NC}

${BLUE}Troubleshooting:${NC}
- Check events: ${YELLOW}kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'${NC}
- Describe pod: ${YELLOW}kubectl describe pod <pod-name> -n $NAMESPACE${NC}
- Check Dapr: ${YELLOW}dapr status -k${NC}

EOF
}

##############################################################################
# Main Execution
##############################################################################

main() {
    print_header "Todo App Helm Deployment Script"

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --namespace|-n)
                NAMESPACE="$2"
                shift 2
                ;;
            --release|-r)
                RELEASE_NAME="$2"
                shift 2
                ;;
            --values|-f)
                VALUES_FILE="$2"
                shift 2
                ;;
            --skip-checks)
                SKIP_CHECKS=true
                shift
                ;;
            --help|-h)
                cat << EOF
Usage: $0 [OPTIONS]

Options:
  -n, --namespace NAME    Kubernetes namespace (default: todo-app-dev)
  -r, --release NAME      Helm release name (default: todo-app)
  -f, --values FILE       Values file (default: values-minikube.yaml)
  --skip-checks           Skip prerequisite checks
  -h, --help              Show this help message

Examples:
  $0
  $0 --namespace my-namespace --release my-app
  $0 -f values-production.yaml
EOF
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Run deployment steps
    if [ "$SKIP_CHECKS" != true ]; then
        check_prerequisites
        check_docker_images
    fi

    setup_namespace
    validate_chart
    deploy_chart
    validate_deployment
    print_usage_instructions
}

# Run main function
main "$@"
