#!/bin/bash
#===============================================================================
# Todo App - Full Stack Setup Script for WSL Ubuntu 22.04
#===============================================================================
# This script automates the complete setup of:
#   - Backend: Python 3.13 + FastAPI
#   - Frontend: Node.js 20 + Next.js
#   - Database: PostgreSQL (local) or Neon Cloud
#
# Usage: bash setup.sh [--local-db | --neon | --skip-db]
#
# Options:
#   --local-db    Install and configure local PostgreSQL
#   --neon        Use Neon Cloud (will prompt for connection string)
#   --skip-db     Skip database setup entirely
#   (no option)   Interactive prompt to choose
#
# Author: Auto-generated setup script
# Date: 2026-01-19
#===============================================================================

set -e  # Exit on any error

#-------------------------------------------------------------------------------
# Configuration
#-------------------------------------------------------------------------------
PROJECT_DIR="/mnt/e/Certified Cloud Native Generative and Agentic AI Engineer/Q4 part 2/Q4 part 2/Hackathon-2/Todo-app"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Database defaults (for local PostgreSQL)
DB_USER="todouser"
DB_PASSWORD="todopassword"
DB_NAME="todo_app_dev"
DB_HOST="localhost"
DB_PORT="5432"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

#-------------------------------------------------------------------------------
# Helper Functions
#-------------------------------------------------------------------------------

print_header() {
    echo ""
    echo -e "${BLUE}===============================================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}===============================================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${CYAN}>>> $1${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

print_info() {
    echo -e "${YELLOW}[INFO] $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check minimum version (major only)
check_min_version() {
    local current="$1"
    local minimum="$2"
    local current_major=$(echo "$current" | cut -d'.' -f1 | tr -d 'v')
    [ "$current_major" -ge "$minimum" ]
}

# Generate secure random string
generate_secret() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
    openssl rand -base64 32 | tr -d '/+=' | head -c 43
}

# Wait for user confirmation
wait_for_enter() {
    echo ""
    read -p "Press Enter to continue..."
    echo ""
}

#-------------------------------------------------------------------------------
# Pre-flight Checks
#-------------------------------------------------------------------------------

preflight_checks() {
    print_header "Pre-flight Checks"

    # Check if running on Linux/WSL
    if [[ "$(uname -s)" != "Linux" ]]; then
        print_error "This script is designed for Linux/WSL. Detected: $(uname -s)"
        exit 1
    fi

    # Check if project directory exists
    if [[ ! -d "$PROJECT_DIR" ]]; then
        print_error "Project directory not found: $PROJECT_DIR"
        print_info "Please ensure the project is cloned/copied to the correct location."
        exit 1
    fi

    # Check if backend directory exists
    if [[ ! -d "$BACKEND_DIR" ]]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi

    # Check if frontend directory exists
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi

    # Check for requirements.txt
    if [[ ! -f "$BACKEND_DIR/requirements.txt" ]]; then
        print_error "Backend requirements.txt not found!"
        exit 1
    fi

    # Check for package.json
    if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
        print_error "Frontend package.json not found!"
        exit 1
    fi

    print_success "All pre-flight checks passed!"
}

#-------------------------------------------------------------------------------
# System Prerequisites Installation
#-------------------------------------------------------------------------------

install_system_prerequisites() {
    print_header "Installing System Prerequisites"

    print_step "Updating package lists..."
    sudo apt update

    print_step "Installing essential build tools..."
    sudo apt install -y \
        build-essential \
        curl \
        wget \
        git \
        software-properties-common \
        ca-certificates \
        gnupg \
        lsb-release

    print_success "System prerequisites installed!"
}

#-------------------------------------------------------------------------------
# Python 3.13 Installation
#-------------------------------------------------------------------------------

install_python() {
    print_header "Python 3.13 Installation"

    # Check if Python 3.13 is already installed
    if command_exists python3.13; then
        local python_version=$(python3.13 --version 2>&1 | cut -d' ' -f2)
        print_success "Python 3.13 already installed: $python_version"
        return 0
    fi

    print_step "Adding deadsnakes PPA for Python 3.13..."
    sudo add-apt-repository -y ppa:deadsnakes/ppa

    print_step "Updating package lists..."
    sudo apt update

    print_step "Installing Python 3.13 and related packages..."
    sudo apt install -y \
        python3.13 \
        python3.13-venv \
        python3.13-dev \
        python3.13-distutils 2>/dev/null || true

    # Verify installation
    if command_exists python3.13; then
        local python_version=$(python3.13 --version 2>&1)
        print_success "Python installed: $python_version"
    else
        print_error "Failed to install Python 3.13"
        exit 1
    fi
}

#-------------------------------------------------------------------------------
# Node.js 20.x Installation
#-------------------------------------------------------------------------------

install_nodejs() {
    print_header "Node.js 20.x LTS Installation"

    # Check if Node.js is already installed with sufficient version
    if command_exists node; then
        local node_version=$(node --version 2>&1)
        if check_min_version "$node_version" 18; then
            print_success "Node.js already installed with sufficient version: $node_version"
            print_info "npm version: $(npm --version)"
            return 0
        else
            print_warning "Node.js installed but version too old: $node_version (need 18+)"
            print_step "Upgrading Node.js..."
        fi
    fi

    print_step "Setting up NodeSource repository for Node.js 20.x..."

    # Remove old NodeSource list if exists
    sudo rm -f /etc/apt/sources.list.d/nodesource.list 2>/dev/null || true

    # Install Node.js 20.x
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

    print_step "Installing Node.js..."
    sudo apt install -y nodejs

    # Verify installation
    if command_exists node && command_exists npm; then
        print_success "Node.js installed: $(node --version)"
        print_success "npm installed: $(npm --version)"
    else
        print_error "Failed to install Node.js"
        exit 1
    fi
}

#-------------------------------------------------------------------------------
# PostgreSQL Installation (Local)
#-------------------------------------------------------------------------------

install_postgresql() {
    print_header "PostgreSQL Installation (Local)"

    # Check if PostgreSQL is already installed
    if command_exists psql; then
        print_success "PostgreSQL already installed: $(psql --version)"
    else
        print_step "Installing PostgreSQL..."
        sudo apt install -y postgresql postgresql-contrib
        print_success "PostgreSQL installed!"
    fi

    # Start PostgreSQL service
    print_step "Starting PostgreSQL service..."
    sudo service postgresql start || sudo systemctl start postgresql || true

    # Wait for PostgreSQL to be ready
    sleep 2

    # Check if service is running
    if sudo service postgresql status > /dev/null 2>&1 || pgrep -x "postgres" > /dev/null; then
        print_success "PostgreSQL service is running"
    else
        print_warning "PostgreSQL service may not be running. Attempting to start..."
        sudo service postgresql start
    fi
}

setup_postgresql_database() {
    print_header "Setting Up PostgreSQL Database"

    print_step "Creating database user '$DB_USER'..."
    sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" || {
        print_warning "User may already exist, continuing..."
    }

    print_step "Creating database '$DB_NAME'..."
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

    print_step "Granting privileges..."
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

    # For PostgreSQL 15+, grant schema privileges
    sudo -u postgres psql -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null || true

    print_success "PostgreSQL database setup complete!"
    print_info "Connection string: postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
}

#-------------------------------------------------------------------------------
# Backend Setup
#-------------------------------------------------------------------------------

setup_backend() {
    print_header "Backend Setup (FastAPI + Python)"

    cd "$BACKEND_DIR"
    print_info "Working directory: $(pwd)"

    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        print_step "Creating Python virtual environment..."
        python3.13 -m venv venv
        print_success "Virtual environment created!"
    else
        print_info "Virtual environment already exists"
    fi

    # Activate virtual environment
    print_step "Activating virtual environment..."
    source venv/bin/activate

    # Verify we're in the venv
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtual environment activated: $VIRTUAL_ENV"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi

    # Upgrade pip
    print_step "Upgrading pip..."
    pip install --upgrade pip

    # Install dependencies
    print_step "Installing Python dependencies..."
    pip install -r requirements.txt

    print_success "Backend dependencies installed!"

    # Deactivate for now
    deactivate
}

setup_backend_env() {
    local db_url="$1"

    print_header "Backend Environment Configuration"

    cd "$BACKEND_DIR"

    # Generate JWT secret
    print_step "Generating secure JWT secret key..."
    source venv/bin/activate
    JWT_SECRET=$(generate_secret)
    deactivate

    print_info "Generated JWT_SECRET_KEY: ${JWT_SECRET:0:20}..."

    # Create .env file
    print_step "Creating .env configuration file..."

    cat > .env << EOF
#===============================================================================
# Todo App Backend - Environment Configuration
# Generated by setup.sh on $(date)
#===============================================================================

# =================================================
# DATABASE CONFIGURATION
# =================================================
DATABASE_URL=$db_url

# =================================================
# JWT AUTHENTICATION
# =================================================
# Secret key for JWT token signing (auto-generated)
JWT_SECRET_KEY=$JWT_SECRET

# JWT algorithm (do not change unless you know what you're doing)
JWT_ALGORITHM=HS256

# Token expiration time in minutes
JWT_EXPIRE_MINUTES=15

# =================================================
# CORS CONFIGURATION
# =================================================
# Frontend URL for CORS (adjust for production)
FRONTEND_URL=http://localhost:3000

# =================================================
# APPLICATION SETTINGS
# =================================================
# Environment: development, staging, production
APP_ENV=development

# =================================================
# OAUTH CONFIGURATION (Optional)
# =================================================
# Uncomment and configure if using OAuth providers

# Google OAuth
# GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
# GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
# GITHUB_CLIENT_ID=your-github-client-id
# GITHUB_CLIENT_SECRET=your-github-client-secret
EOF

    print_success "Backend .env file created!"
    print_info "Location: $BACKEND_DIR/.env"
}

initialize_database() {
    print_header "Database Initialization"

    cd "$BACKEND_DIR"

    print_step "Activating virtual environment..."
    source venv/bin/activate

    print_step "Creating database tables..."
    python3 -c "from app.database import create_db_and_tables; create_db_and_tables()"

    if [[ $? -eq 0 ]]; then
        print_success "Database tables created successfully!"
    else
        print_error "Failed to create database tables"
        print_info "Please check your DATABASE_URL in .env file"
        deactivate
        exit 1
    fi

    deactivate
}

#-------------------------------------------------------------------------------
# Frontend Setup
#-------------------------------------------------------------------------------

setup_frontend() {
    print_header "Frontend Setup (Next.js + React)"

    cd "$FRONTEND_DIR"
    print_info "Working directory: $(pwd)"

    # Clean install if node_modules is corrupted
    if [[ -d "node_modules" ]]; then
        print_info "node_modules directory exists"
        read -p "Do you want to clean reinstall npm packages? (y/N): " clean_install
        if [[ "$clean_install" =~ ^[Yy]$ ]]; then
            print_step "Removing existing node_modules..."
            rm -rf node_modules package-lock.json
        fi
    fi

    # Install dependencies
    print_step "Installing npm dependencies..."
    npm install

    print_success "Frontend dependencies installed!"

    # Create .env.local if it doesn't exist
    if [[ ! -f ".env.local" ]]; then
        print_step "Creating .env.local configuration..."
        cat > .env.local << EOF
# Backend API URL
# Development: http://localhost:8000
# Production: Your deployed backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
        print_success "Frontend .env.local created!"
    else
        print_info "Frontend .env.local already exists"
    fi
}

#-------------------------------------------------------------------------------
# Verification
#-------------------------------------------------------------------------------

verify_installation() {
    print_header "Installation Verification"

    echo ""
    echo "Installed Versions:"
    echo "-------------------"

    # Python
    if command_exists python3.13; then
        echo -e "  Python:     ${GREEN}$(python3.13 --version 2>&1)${NC}"
    else
        echo -e "  Python:     ${RED}NOT INSTALLED${NC}"
    fi

    # Node.js
    if command_exists node; then
        echo -e "  Node.js:    ${GREEN}$(node --version)${NC}"
    else
        echo -e "  Node.js:    ${RED}NOT INSTALLED${NC}"
    fi

    # npm
    if command_exists npm; then
        echo -e "  npm:        ${GREEN}$(npm --version)${NC}"
    else
        echo -e "  npm:        ${RED}NOT INSTALLED${NC}"
    fi

    # PostgreSQL
    if command_exists psql; then
        echo -e "  PostgreSQL: ${GREEN}$(psql --version | head -1)${NC}"
    else
        echo -e "  PostgreSQL: ${YELLOW}Not installed (using Neon Cloud?)${NC}"
    fi

    echo ""
    echo "Project Files:"
    echo "--------------"

    # Backend venv
    if [[ -d "$BACKEND_DIR/venv" ]]; then
        echo -e "  Backend venv:     ${GREEN}EXISTS${NC}"
    else
        echo -e "  Backend venv:     ${RED}MISSING${NC}"
    fi

    # Backend .env
    if [[ -f "$BACKEND_DIR/.env" ]]; then
        echo -e "  Backend .env:     ${GREEN}EXISTS${NC}"
    else
        echo -e "  Backend .env:     ${RED}MISSING${NC}"
    fi

    # Frontend node_modules
    if [[ -d "$FRONTEND_DIR/node_modules" ]]; then
        echo -e "  Frontend deps:    ${GREEN}INSTALLED${NC}"
    else
        echo -e "  Frontend deps:    ${RED}MISSING${NC}"
    fi

    # Frontend .env.local
    if [[ -f "$FRONTEND_DIR/.env.local" ]]; then
        echo -e "  Frontend .env:    ${GREEN}EXISTS${NC}"
    else
        echo -e "  Frontend .env:    ${RED}MISSING${NC}"
    fi

    echo ""
}

#-------------------------------------------------------------------------------
# Print Final Instructions
#-------------------------------------------------------------------------------

print_final_instructions() {
    print_header "Setup Complete! - Next Steps"

    cat << 'EOF'

To start the application, open TWO terminal windows:

TERMINAL 1 - Backend (FastAPI):
-------------------------------
EOF
    echo "  cd \"$BACKEND_DIR\""
    cat << 'EOF'
  source venv/bin/activate
  uvicorn main:app --reload --host 0.0.0.0 --port 8000

TERMINAL 2 - Frontend (Next.js):
--------------------------------
EOF
    echo "  cd \"$FRONTEND_DIR\""
    cat << 'EOF'
  npm run dev


VERIFICATION:
-------------
  1. Backend health check:
     curl http://localhost:8000/health
     # Expected: {"status":"ok","version":"2.0.0"}

  2. API Documentation:
     Open http://localhost:8000/docs in your browser

  3. Frontend:
     Open http://localhost:3000 in your browser


QUICK START COMMANDS:
---------------------
# Start backend (from project root):
EOF
    echo "  cd \"$BACKEND_DIR\" && source venv/bin/activate && uvicorn main:app --reload"
    echo ""
    echo "# Start frontend (from project root):"
    echo "  cd \"$FRONTEND_DIR\" && npm run dev"

    cat << 'EOF'


TROUBLESHOOTING:
----------------
  - If backend fails to start: Check .env DATABASE_URL and JWT_SECRET_KEY
  - If frontend fails: Try 'rm -rf node_modules && npm install'
  - If database connection fails: Ensure PostgreSQL is running or Neon URL is correct
  - CORS errors: Verify FRONTEND_URL in backend .env matches frontend URL

EOF

    print_success "Happy coding!"
    echo ""
}

#-------------------------------------------------------------------------------
# Create Convenience Scripts
#-------------------------------------------------------------------------------

create_convenience_scripts() {
    print_header "Creating Convenience Scripts"

    # Start backend script
    print_step "Creating start-backend.sh..."
    cat > "$PROJECT_DIR/start-backend.sh" << 'EOF'
#!/bin/bash
# Start the FastAPI backend server
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
echo "Starting FastAPI backend at http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF
    chmod +x "$PROJECT_DIR/start-backend.sh"

    # Start frontend script
    print_step "Creating start-frontend.sh..."
    cat > "$PROJECT_DIR/start-frontend.sh" << 'EOF'
#!/bin/bash
# Start the Next.js frontend development server
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/frontend"
echo "Starting Next.js frontend at http://localhost:3000"
echo "Press Ctrl+C to stop"
npm run dev
EOF
    chmod +x "$PROJECT_DIR/start-frontend.sh"

    # Test health script
    print_step "Creating test-health.sh..."
    cat > "$PROJECT_DIR/test-health.sh" << 'EOF'
#!/bin/bash
# Test backend health endpoint
echo "Testing backend health endpoint..."
response=$(curl -s http://localhost:8000/health)
if [[ $? -eq 0 ]]; then
    echo "Response: $response"
    if echo "$response" | grep -q '"status":"ok"'; then
        echo "Backend is healthy!"
    else
        echo "Backend responded but may have issues"
    fi
else
    echo "Failed to connect to backend. Is it running?"
fi
EOF
    chmod +x "$PROJECT_DIR/test-health.sh"

    print_success "Convenience scripts created!"
    print_info "  - start-backend.sh  : Start the FastAPI server"
    print_info "  - start-frontend.sh : Start the Next.js dev server"
    print_info "  - test-health.sh    : Test backend health endpoint"
}

#-------------------------------------------------------------------------------
# Database Mode Selection
#-------------------------------------------------------------------------------

select_database_mode() {
    # Check command line arguments first
    case "${1:-}" in
        --local-db)
            DB_MODE="local"
            return
            ;;
        --neon)
            DB_MODE="neon"
            return
            ;;
        --skip-db)
            DB_MODE="skip"
            return
            ;;
    esac

    # Interactive selection
    print_header "Database Configuration"

    echo "Choose your database setup:"
    echo ""
    echo "  1) Local PostgreSQL - Install and configure PostgreSQL locally"
    echo "  2) Neon Cloud       - Use Neon's free PostgreSQL cloud service"
    echo "  3) Skip             - I'll configure the database manually later"
    echo ""

    while true; do
        read -p "Enter your choice (1/2/3): " choice
        case $choice in
            1)
                DB_MODE="local"
                break
                ;;
            2)
                DB_MODE="neon"
                break
                ;;
            3)
                DB_MODE="skip"
                break
                ;;
            *)
                print_warning "Invalid choice. Please enter 1, 2, or 3."
                ;;
        esac
    done
}

get_neon_connection_string() {
    print_header "Neon Cloud Database Configuration"

    cat << 'EOF'
To get your Neon connection string:

  1. Go to https://neon.tech and sign up/login
  2. Create a new project (free tier available)
  3. Go to your project dashboard
  4. Click "Connection Details"
  5. Copy the connection string (starts with postgresql://)

The connection string looks like:
  postgresql://username:password@ep-xxxx-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require

EOF

    while true; do
        read -p "Paste your Neon connection string: " NEON_URL

        # Validate it looks like a PostgreSQL URL
        if [[ "$NEON_URL" =~ ^postgresql:// ]]; then
            DATABASE_URL="$NEON_URL"
            print_success "Connection string accepted!"
            break
        else
            print_warning "Invalid connection string. It should start with 'postgresql://'"
            read -p "Try again? (Y/n): " retry
            if [[ "$retry" =~ ^[Nn]$ ]]; then
                print_info "You can manually edit backend/.env later with your DATABASE_URL"
                DATABASE_URL="postgresql://user:password@host/database?sslmode=require"
                break
            fi
        fi
    done
}

#-------------------------------------------------------------------------------
# Main Script
#-------------------------------------------------------------------------------

main() {
    clear

    cat << 'EOF'

  ╔════════════════════════════════════════════════════════════════════════════╗
  ║                                                                            ║
  ║   ████████╗ ██████╗ ██████╗  ██████╗      █████╗ ██████╗ ██████╗           ║
  ║   ╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗    ██╔══██╗██╔══██╗██╔══██╗          ║
  ║      ██║   ██║   ██║██║  ██║██║   ██║    ███████║██████╔╝██████╔╝          ║
  ║      ██║   ██║   ██║██║  ██║██║   ██║    ██╔══██║██╔═══╝ ██╔═══╝           ║
  ║      ██║   ╚██████╔╝██████╔╝╚██████╔╝    ██║  ██║██║     ██║               ║
  ║      ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝     ╚═╝  ╚═╝╚═╝     ╚═╝               ║
  ║                                                                            ║
  ║            Full Stack Setup Script for WSL Ubuntu 22.04                    ║
  ║                                                                            ║
  ╚════════════════════════════════════════════════════════════════════════════╝

EOF

    echo ""
    print_info "This script will set up the complete Todo App development environment"
    print_info "including Python 3.13, Node.js 20, and optionally PostgreSQL."
    echo ""

    # Confirm before proceeding
    read -p "Do you want to continue? (Y/n): " confirm
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi

    # Pre-flight checks
    preflight_checks

    # Select database mode
    select_database_mode "$1"

    # Install system prerequisites
    install_system_prerequisites

    # Install Python 3.13
    install_python

    # Install Node.js 20.x
    install_nodejs

    # Database setup based on mode
    case $DB_MODE in
        local)
            install_postgresql
            setup_postgresql_database
            DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
            ;;
        neon)
            get_neon_connection_string
            ;;
        skip)
            print_warning "Skipping database setup. You'll need to configure DATABASE_URL manually."
            DATABASE_URL="postgresql://user:password@localhost:5432/todo_app_dev"
            ;;
    esac

    # Setup backend
    setup_backend
    setup_backend_env "$DATABASE_URL"

    # Initialize database (skip if user chose to skip db setup)
    if [[ "$DB_MODE" != "skip" ]]; then
        initialize_database
    else
        print_warning "Skipping database initialization. Run this after configuring DATABASE_URL:"
        echo "  cd \"$BACKEND_DIR\" && source venv/bin/activate"
        echo "  python3 -c \"from app.database import create_db_and_tables; create_db_and_tables()\""
    fi

    # Setup frontend
    setup_frontend

    # Create convenience scripts
    create_convenience_scripts

    # Verify installation
    verify_installation

    # Print final instructions
    print_final_instructions
}

#-------------------------------------------------------------------------------
# Script Entry Point
#-------------------------------------------------------------------------------

# Trap errors
trap 'print_error "An error occurred on line $LINENO. Exiting."; exit 1' ERR

# Run main function with all arguments
main "$@"
