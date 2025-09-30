#!/bin/bash

declare -A HOOKS_DIRS=(
    ["frontend"]="scripts/git-hooks/frontend"
    ["backend"]="scripts/git-hooks/backend"
    ["engine"]="scripts/git-hooks/engine"
)

for MODULE in "${!HOOKS_DIRS[@]}"; do
    HOOKS_DIR=".git/modules/$MODULE/hooks"
    REPO_HOOKS_DIR="${HOOKS_DIRS[$MODULE]}"
    
    mkdir -p "$HOOKS_DIR"
    cp -r "$REPO_HOOKS_DIR"/* "$HOOKS_DIR/"
    chmod +x "$HOOKS_DIR"/*
    echo "Git hooks installed successfully in $HOOKS_DIR."
done
