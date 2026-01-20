#!/bin/bash
# Setup script for local development (outside Docker)
# Run this once when setting up your local environment

set -e

echo "🔧 Setting up local development environment..."
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies with uv..."
uv sync

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

echo ""
echo "✅ Local setup complete!"
echo ""
echo "You can now run:"
echo "  - Jupyter notebooks locally"
echo "  - Python scripts that use crawl4ai"
echo "  - Tests locally"
