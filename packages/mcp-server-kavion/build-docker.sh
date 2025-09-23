#!/bin/bash

# Kavion MCP Server Docker Build Script
# This script builds and optionally runs the Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -b, --build     Build the Docker image"
    echo "  -r, --run       Run the container after building"
    echo "  -s, --stop      Stop running containers"
    echo "  -l, --logs      Show container logs"
    echo "  -c, --clean     Clean up containers and images"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --build                    # Build the image"
    echo "  $0 --build --run              # Build and run"
    echo "  $0 --stop                     # Stop containers"
    echo "  $0 --logs                     # Show logs"
    echo "  $0 --clean                    # Clean up"
}

# Function to build the Docker image
build_image() {
    print_status "Building Kavion MCP Server Docker image..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Build the image from workspace root
    docker build -f ../../Dockerfile.kavion -t kavion-mcp-server:latest ../../
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully!"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to run the container
run_container() {
    print_status "Starting Kavion MCP Server container..."
    
    # Check if image exists
    if ! docker image inspect kavion-mcp-server:latest > /dev/null 2>&1; then
        print_warning "Image not found. Building first..."
        build_image
    fi
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    # Start the container
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_success "Container started successfully!"
        print_status "Server is running at: http://localhost:3000"
        print_status "Health check: http://localhost:3000/health"
        print_status "MCP endpoint: http://localhost:3000/mcp"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

# Function to stop containers
stop_containers() {
    print_status "Stopping Kavion MCP Server containers..."
    docker-compose down
    print_success "Containers stopped"
}

# Function to show logs
show_logs() {
    print_status "Showing container logs..."
    docker-compose logs -f
}

# Function to clean up
cleanup() {
    print_status "Cleaning up containers and images..."
    
    # Stop and remove containers
    docker-compose down 2>/dev/null || true
    
    # Remove the image
    docker rmi kavion-mcp-server:latest 2>/dev/null || true
    
    # Remove dangling images
    docker image prune -f
    
    print_success "Cleanup completed"
}

# Function to check if required environment variables are set
check_env() {
    local missing_vars=()
    
    if [ -z "$SUPABASE_URL" ]; then
        missing_vars+=("SUPABASE_URL")
    fi
    
    if [ -z "$SUPABASE_ANON_KEY" ]; then
        missing_vars+=("SUPABASE_ANON_KEY")
    fi
    
    if [ -z "$USER_EMAIL" ]; then
        missing_vars+=("USER_EMAIL")
    fi
    
    if [ -z "$USER_PASSWORD" ]; then
        missing_vars+=("USER_PASSWORD")
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_warning "The following environment variables are not set:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_warning "Using default values from docker-compose.yml"
    fi
}

# Main script logic
main() {
    local build=false
    local run=false
    local stop=false
    local logs=false
    local clean=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -b|--build)
                build=true
                shift
                ;;
            -r|--run)
                run=true
                shift
                ;;
            -s|--stop)
                stop=true
                shift
                ;;
            -l|--logs)
                logs=true
                shift
                ;;
            -c|--clean)
                clean=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # If no options provided, show usage
    if [ "$build" = false ] && [ "$run" = false ] && [ "$stop" = false ] && [ "$logs" = false ] && [ "$clean" = false ]; then
        show_usage
        exit 0
    fi
    
    # Execute requested actions
    if [ "$clean" = true ]; then
        cleanup
    fi
    
    if [ "$stop" = true ]; then
        stop_containers
    fi
    
    if [ "$build" = true ]; then
        build_image
    fi
    
    if [ "$run" = true ]; then
        check_env
        run_container
    fi
    
    if [ "$logs" = true ]; then
        show_logs
    fi
}

# Run main function with all arguments
main "$@"
