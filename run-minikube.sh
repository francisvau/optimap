#!/bin/bash

bash ./scripts/setup-hooks.sh

SCRIPT_DIR="$(dirname "$0")"

if [[ -f "$SCRIPT_DIR/.env" ]]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
else
    echo "Error: .env file not found in $SCRIPT_DIR"
    exit 1
fi

# Default behavior
CLEANUP_ENABLED=true
BUILD=false
SHUTDOWN=false
RUN_FRONTEND=false
RUN_BACKEND=false
RUN_ENGINE=false


# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -b|--build) BUILD=true ;;
        -d) CLEANUP_ENABLED=false ;;  # Keep deployments running on exit
        --frontend) RUN_FRONTEND=true; RUN_BACKEND=true; RUN_ENGINE=true ;;
        --backend) RUN_BACKEND=true ;;
        --engine) RUN_ENGINE=true ;;
        --down) SHUTDOWN=true ;;
        *) echo "Usage: $0 [-b] [-d] [--down]"; exit 1 ;;
    esac
    shift
done

if [ "$RUN_FRONTEND" = false ] && [ "$RUN_BACKEND" = false ] && [ "$RUN_ENGINE" = false ]; then
    RUN_FRONTEND=true
    RUN_BACKEND=true
    RUN_ENGINE=true
fi

if [ "$SHUTDOWN" = true ]; then
    echo "Shutting down..."
    
    echo "Unmounting Minikube directories..."
    pkill -f "minikube mount"

    echo "Deleting Kubernetes manifests..."
    minikube kubectl -- delete -f platform/dev/k8s-manifest
    
    echo "Shutdown complete."
    exit 0
fi

cleanup() {
    echo "Cleaning up..."
    # Stop all minikube mounts
    pkill -f "minikube mount"
    
    # Delete tunnel
    pkill -f "minikube tunnel"
    
    # Delete manifests
    minikube kubectl -- delete -f platform/dev/minikube/frontend --ignore-not-found=true
    minikube kubectl -- delete -f platform/dev/minikube/backend --ignore-not-found=true
    minikube kubectl -- delete -f platform/dev/minikube/engine --ignore-not-found=true
    minikube kubectl -- delete -f platform/dev/minikube/k8s-manifest --ignore-not-found=true

    exit 0
}

trap cleanup SIGINT

if ! minikube status | grep -q "Running"; then
    echo "Minikube is not running. Starting it..."
    minikube start --driver=docker
fi

if ! minikube addons list | grep -q "ingress.*enabled"; then
    echo "Minikube ingress addon is not enabled. Enabling it..."
    minikube addons enable ingress
fi

if [[ "$BUILD" == true ]]; then
    echo "Building Docker images..."
    if [ "$RUN_FRONTEND" = true ]; then
        docker build -t optimap-frontend-dev frontend -f frontend/Dockerfile.dev
        minikube image load optimap-frontend-dev:latest
    fi

    if [ "$RUN_BACKEND" = true ]; then
        docker build -t optimap-backend-dev backend -f backend/Dockerfile.dev
        minikube image load optimap-backend-dev:latest
    fi

    if [ "$RUN_ENGINE" = true ]; then
        docker build -t optimap-engine-dev engine -f engine/Dockerfile.dev
        minikube image load optimap-engine-dev:latest
    fi
fi

# Mount local directories to Minikube
pkill -f "minikube mount"

# Mount local directories to Minikube
minikube mount "$BACKEND_PATH:/mnt/data/backend" &
minikube mount "$FRONTEND_PATH:/mnt/data/frontend" &
minikube mount "$ENGINE_PATH:/mnt/data/engine" &

echo "Applying k8s manifest..."
minikube kubectl -- apply -f platform/dev/minikube/k8s-manifest

if [ "$RUN_FRONTEND" = true ]; then
    minikube kubectl -- apply -f platform/dev/minikube/frontend
fi

if [ "$RUN_BACKEND" = true ]; then
    minikube kubectl -- apply -f platform/dev/minikube/backend
fi

if [ "$RUN_ENGINE" = true ]; then
    minikube kubectl -- apply -f platform/dev/minikube/engine
fi

minikube tunnel &

if [ "$CLEANUP_ENABLED" = false ]; then
    echo "Running... Press CTRL+C to stop."
    wait
else
    wait  # Keep the script running
fi