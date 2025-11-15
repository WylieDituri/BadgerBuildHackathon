#!/bin/bash

# Script to commit the car intelligence demo

echo "🚗 Preparing to commit Centralized Car Intelligence Demo..."

# Add all relevant files
git add .gitignore
git add README.md

# Add frontend files (excluding .env.local)
git add frontend/.gitignore
git add frontend/package.json
git add frontend/next.config.mjs
git add frontend/tailwind.config.ts
git add frontend/tsconfig.json
git add frontend/postcss.config.js
git add frontend/.env.local.example
git add frontend/app/
git add frontend/components/
git add frontend/lib/

# Add backend files (excluding .env)
git add backend/.gitignore
git add backend/pyproject.toml
git add backend/requirements.txt
git add backend/.env.example
git add backend/app/

echo ""
echo "📝 Files staged for commit:"
git status --short

echo ""
echo "💡 To commit, run:"
echo "   git commit -m 'Add Centralized Car Intelligence demo with Next.js and FastAPI'"
echo ""
echo "💡 To push to remote, run:"
echo "   git push origin dev"
