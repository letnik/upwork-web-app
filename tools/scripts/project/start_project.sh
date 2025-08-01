#!/bin/bash

# Скрипт для запуску всього проекту Upwork AI Assistant
# Використання: ./tools/scripts/start_project.sh [опції]

set -e

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Символи для прогрес-бару
PROGRESS_CHARS=("▰" "▱")
SPINNER_CHARS=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")

# Функції для красивого виводу
print_header() {
    echo -e "\n${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║${NC}                    ${BOLD}${WHITE}🚀 UPWORK AI ASSISTANT${NC}                    ${BOLD}${CYAN}║${NC}"
    echo -e "${BOLD}${CYAN}║${NC}                    ${BOLD}${WHITE}Project Startup Script${NC}                    ${BOLD}${CYAN}║${NC}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    local title="$1"
    echo -e "\n${BOLD}${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${WHITE}  $title${NC}"
    echo -e "${BOLD}${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_step() {
    local step="$1"
    local message="$2"
    echo -e "${BOLD}${BLUE}  📋${NC} ${BOLD}${WHITE}$step${NC} - $message"
}

print_progress() {
    local current="$1"
    local total="$2"
    local width=50
    local filled=$((current * width / total))
    local empty=$((width - filled))
    
    printf "${BOLD}${CYAN}  [${NC}"
    printf "%${filled}s" | tr ' ' "${PROGRESS_CHARS[0]}"
    printf "%${empty}s" | tr ' ' "${PROGRESS_CHARS[1]}"
    printf "${BOLD}${CYAN}]${NC} ${BOLD}${WHITE}%d%%${NC} (%d/%d)\n" $((current * 100 / total)) "$current" "$total"
}

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf "${BOLD}${CYAN}  [%c]${NC} " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

log() {
    echo -e "${GREEN}  ✅${NC} $1"
}

warn() {
    echo -e "${YELLOW}  ⚠️${NC} $1"
}

error() {
    echo -e "${RED}  ❌${NC} $1"
}

info() {
    echo -e "${BLUE}  ℹ️${NC} $1"
}

success() {
    echo -e "${GREEN}  🎉${NC} ${BOLD}$1${NC}"
}

# Змінні
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/app/backend"
FRONTEND_DIR="$PROJECT_ROOT/app/frontend"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker/docker-compose.yml"
ENV_FILE="$PROJECT_ROOT/.env"

# Функція для перевірки залежностей
check_dependencies() {
    print_section "🔍 DEPENDENCY CHECK"
    
    local deps=("docker" "docker compose" "node" "npm" "python3")
    local dep_names=("Docker" "Docker Compose" "Node.js" "npm" "Python 3")
    local total=${#deps[@]}
    local current=0
    
    for i in "${!deps[@]}"; do
        current=$((current + 1))
        print_step "Step $current/$total" "Checking ${dep_names[$i]}..."
        
        if command -v ${deps[$i]} &> /dev/null; then
            log "${dep_names[$i]} found"
            print_progress $current $total
        else
            error "${dep_names[$i]} not found"
            print_progress $current $total
            exit 1
        fi
    done
    
    success "All dependencies are available"
}

# Функція для встановлення Python залежностей
install_python_dependencies() {
    print_section "🐍 PYTHON DEPENDENCIES"
    
    cd "$PROJECT_ROOT"
    
    print_step "Step 1/3" "Checking virtual environment..."
    if [ ! -d ".venv" ]; then
        info "Creating virtual environment..."
        python3 -m venv .venv
        log "Virtual environment created"
    else
        log "Virtual environment already exists"
    fi
    
    print_step "Step 2/3" "Activating virtual environment..."
    source .venv/bin/activate
    log "Virtual environment activated"
    
    print_step "Step 3/3" "Installing dependencies..."
    info "Installing all dependencies (this may take a while)..."
    ./tools/scripts/dependencies/install.sh all base > /dev/null 2>&1
    
    success "Python dependencies installed successfully"
}

# Функція для створення .env файлу
create_env_file() {
    print_section "📝 ENVIRONMENT SETUP"
    
    if [ ! -f "$ENV_FILE" ]; then
        print_step "Step 1/1" "Creating .env file..."
        cat > "$ENV_FILE" << EOF
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/upwork_app

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=your-encryption-key-change-in-production

# Upwork API (заповніть після отримання)
UPWORK_CLIENT_ID=
UPWORK_CLIENT_SECRET=
UPWORK_CALLBACK_URL=http://localhost:8000/auth/upwork/callback

# AI Services (опціонально)
OPENAI_API_KEY=
CLAUDE_API_KEY=

# Environment
ENVIRONMENT=development
DEBUG=true

# Frontend
REACT_APP_API_URL=http://localhost:8000
EOF
        success ".env file created"
    else
        log ".env file already exists"
    fi
}

# Функція для запуску бази даних
start_database() {
    print_section "🗄️ DATABASE STARTUP"
    
    cd "$PROJECT_ROOT"
    
    print_step "Step 1/3" "Starting PostgreSQL and Redis..."
    docker compose -f docker/docker-compose.yml up -d postgres redis > /dev/null 2>&1
    log "Database containers started"
    
    print_step "Step 2/3" "Waiting for database to be ready..."
    info "Waiting for PostgreSQL to accept connections..."
    sleep 10
    
    print_step "Step 3/3" "Verifying database connection..."
    if docker compose -f docker/docker-compose.yml exec postgres pg_isready -U user -d upwork_app > /dev/null 2>&1; then
        success "Database is ready"
    else
        error "Database connection failed"
        exit 1
    fi
}

# Функція для запуску backend сервісів
start_backend() {
    print_section "🔧 BACKEND SERVICES"
    
    cd "$PROJECT_ROOT"
    
    print_step "Step 1/4" "Stopping existing containers..."
    docker compose -f docker/docker-compose.yml down > /dev/null 2>&1
    log "Existing containers stopped"
    
    print_step "Step 2/4" "Starting all services..."
    info "Starting backend services (this may take a moment)..."
    docker compose -f docker/docker-compose.yml up -d > /dev/null 2>&1
    log "All services started"
    
    print_step "Step 3/4" "Waiting for services to be ready..."
    info "Waiting for services to initialize..."
    sleep 15
    
    print_step "Step 4/4" "Verifying service status..."
    local services=("api-gateway" "auth-service" "ai-service" "analytics-service" "notification-service")
    local total=${#services[@]}
    local current=0
    local all_healthy=true
    
    for service in "${services[@]}"; do
        current=$((current + 1))
        if docker compose -f docker/docker-compose.yml ps "$service" | grep -q "Up"; then
            log "$service is running"
        else
            error "$service failed to start"
            all_healthy=false
        fi
        print_progress $current $total
    done
    
    if [ "$all_healthy" = true ]; then
        success "All backend services are running"
    else
        error "Some services failed to start"
        docker compose -f docker/docker-compose.yml logs
        exit 1
    fi
}

# Функція для встановлення залежностей Frontend
install_frontend_deps() {
    print_section "📦 FRONTEND DEPENDENCIES"
    
    cd "$FRONTEND_DIR"
    
    print_step "Step 1/2" "Checking node_modules..."
    if [ ! -d "node_modules" ]; then
        print_step "Step 2/2" "Installing npm dependencies..."
        info "Installing frontend dependencies (this may take a while)..."
        npm install > /dev/null 2>&1
        success "Frontend dependencies installed"
    else
        log "Frontend dependencies already installed"
    fi
}

# Функція для запуску Frontend
start_frontend() {
    print_section "🎨 FRONTEND STARTUP"
    
    cd "$FRONTEND_DIR"
    
    print_step "Step 1/3" "Starting React development server..."
    info "Starting frontend in background..."
    npm start > /dev/null 2>&1 &
    local frontend_pid=$!
    
    print_step "Step 2/3" "Saving process ID..."
    echo $frontend_pid > /tmp/frontend_pid
    log "Frontend PID saved: $frontend_pid"
    
    print_step "Step 3/3" "Waiting for frontend to be ready..."
    info "Waiting for React development server..."
    sleep 10
    
    success "Frontend is running (PID: $frontend_pid)"
}

# Функція для перевірки статусу
check_status() {
    print_section "📊 SERVICE STATUS"
    
    echo -e "${BOLD}${WHITE}  🐳 DOCKER CONTAINERS:${NC}"
    echo -e "${CYAN}  ──────────────────────────────────────────────────────────────────────────${NC}"
    
    # Backend сервіси
    cd "$PROJECT_ROOT"
    docker compose -f docker/docker-compose.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${BOLD}${WHITE}  🌐 ACCESS URLs:${NC}"
    echo -e "${CYAN}  ──────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${GREEN}  🎨 Frontend:${NC}     ${BOLD}http://localhost:3000${NC}"
    echo -e "${GREEN}  🔗 API Gateway:${NC}  ${BOLD}http://localhost:8000${NC}"
    echo -e "${GREEN}  🔐 Auth Service:${NC} ${BOLD}http://localhost:8001${NC}"
    echo -e "${GREEN}  🤖 AI Service:${NC}   ${BOLD}http://localhost:8003${NC}"
    echo -e "${GREEN}  📊 Analytics:${NC}    ${BOLD}http://localhost:8004${NC}"
    
    echo -e "\n${BOLD}${WHITE}  📚 API DOCUMENTATION:${NC}"
    echo -e "${CYAN}  ──────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}  📖 Swagger UI:${NC}    ${BOLD}http://localhost:8000/docs${NC}"
    echo -e "${BLUE}  📘 ReDoc:${NC}        ${BOLD}http://localhost:8000/redoc${NC}"
    
    echo -e "\n${BOLD}${WHITE}  💡 USEFUL COMMANDS:${NC}"
    echo -e "${CYAN}  ──────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}  📊 Status:${NC}      ${BOLD}$0 status${NC}"
    echo -e "${YELLOW}  📋 Logs:${NC}        ${BOLD}$0 logs${NC}"
    echo -e "${YELLOW}  🛑 Stop:${NC}        ${BOLD}$0 stop${NC}"
    echo -e "${YELLOW}  🔄 Restart:${NC}     ${BOLD}$0 restart${NC}"
}

# Функція для зупинки проекту
stop_project() {
    print_section "🛑 PROJECT SHUTDOWN"
    
    print_step "Step 1/3" "Stopping frontend..."
    if [ -f "/tmp/frontend_pid" ]; then
        local frontend_pid=$(cat /tmp/frontend_pid)
        if kill -0 "$frontend_pid" 2>/dev/null; then
            kill "$frontend_pid"
            log "Frontend stopped"
        fi
        rm -f /tmp/frontend_pid
    fi
    
    print_step "Step 2/3" "Stopping Docker containers..."
    cd "$PROJECT_ROOT"
    docker compose -f docker/docker-compose.yml down > /dev/null 2>&1
    
    print_step "Step 3/3" "Cleanup completed..."
    success "Project stopped successfully"
}

# Функція для очищення
cleanup() {
    print_section "🧹 CLEANUP"
    
    print_step "Step 1/3" "Stopping all services..."
    stop_project
    
    print_step "Step 2/3" "Removing containers and volumes..."
    cd "$PROJECT_ROOT"
    docker compose -f docker/docker-compose.yml down --volumes --remove-orphans > /dev/null 2>&1
    
    print_step "Step 3/3" "Cleaning Docker system..."
    docker system prune -f > /dev/null 2>&1
    
    success "Cleanup completed"
}

# Функція для показу логів
show_logs() {
    local service="$1"
    
    print_section "📋 SERVICE LOGS"
    
    if [ -z "$service" ]; then
        print_step "Step 1/1" "Showing logs for all services..."
        cd "$PROJECT_ROOT"
        docker compose -f docker/docker-compose.yml logs -f
    else
        print_step "Step 1/1" "Showing logs for service: $service"
        cd "$PROJECT_ROOT"
        docker compose -f docker/docker-compose.yml logs -f "$service"
    fi
}

# Функція для перезапуску
restart() {
    print_section "🔄 PROJECT RESTART"
    
    print_step "Step 1/3" "Stopping project..."
    stop_project
    
    print_step "Step 2/3" "Waiting for cleanup..."
    sleep 2
    
    print_step "Step 3/3" "Starting project..."
    start_project
}

# Функція для показу допомоги
show_help() {
    print_header
    echo -e "${BOLD}${WHITE}  USAGE:${NC} $0 [options]"
    echo ""
    echo -e "${BOLD}${WHITE}  OPTIONS:${NC}"
    echo -e "${CYAN}  ──────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${GREEN}  start, s${NC}     Start the project (default)"
    echo -e "${GREEN}  stop${NC}        Stop the project"
    echo -e "${GREEN}  restart, r${NC}   Restart the project"
    echo -e "${GREEN}  status${NC}      Show service status"
    echo -e "${GREEN}  logs [service]${NC} Show logs (all or specific service)"
    echo -e "${GREEN}  cleanup${NC}     Clean everything (containers, images, volumes)"
    echo -e "${GREEN}  help, h${NC}     Show this help"
    echo ""
    echo -e "${BOLD}${WHITE}  EXAMPLES:${NC}"
    echo -e "${CYAN}  ──────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}  $0 start${NC}          # Start the project"
    echo -e "${YELLOW}  $0 logs auth${NC}      # Show Auth Service logs"
    echo -e "${YELLOW}  $0 status${NC}         # Show status"
    echo -e "${YELLOW}  $0 cleanup${NC}        # Clean everything"
    echo ""
}

# Функція для запуску всього проекту
start_project() {
    print_header
    
    local total_steps=7
    local current_step=0
    
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps
    check_dependencies
    
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps
    install_python_dependencies
    
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps
    create_env_file
    
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps
    start_database
    
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps
    start_backend
    
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps
    install_frontend_deps
    
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps
    start_frontend
    
    check_status
    
    echo -e "\n${BOLD}${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║${NC}                    ${BOLD}${WHITE}🎉 PROJECT STARTED SUCCESSFULLY! 🎉${NC}                    ${BOLD}${GREEN}║${NC}"
    echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}\n"
    
    echo -e "${BOLD}${WHITE}  🌐 OPEN BROWSER:${NC} ${BOLD}${CYAN}http://localhost:3000${NC}"
    echo -e "${BOLD}${WHITE}  📚 API DOCS:${NC}    ${BOLD}${CYAN}http://localhost:8000/docs${NC}\n"
}

# Основний код
main() {
    local command="${1:-start}"
    
    case "$command" in
        start|s)
            start_project
            ;;
        stop)
            stop_project
            ;;
        restart|r)
            restart
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs "$2"
            ;;
        cleanup)
            cleanup
            ;;
        help|h|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Запуск основної функції
main "$@" 