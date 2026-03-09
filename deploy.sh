#!/usr/bin/env bash
set -e

echo "🚀 Starting Render build..."

# --- Backend ---
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install pipenv
pipenv install --system --deploy

# --- Frontend ---
echo "🧩 Building frontend with Vite..."
cd front
npm install
npm run build
cd ..

# --- Migrations ---
echo "🗄️ Applying database migrations..."
pipenv run flask db upgrade

# --- Seed Data ---
echo "📚 Loading seed data..."
pipenv run python -m back.init.seed_data
pipenv run python -m back.init.seed_users

echo "✅ Deployment completed successfully."
