#!/bin/bash
# Build and deploy Sendell Dashboard
# Usage: ./build-dashboard.sh

set -e  # Exit on any error

echo "========================================="
echo "  Building Sendell Dashboard"
echo "========================================="

# 1. Navigate to dashboard directory
cd sendell-dashboard

# 2. Build the Angular app
echo "Building Angular app..."
npm run build

# 3. Copy to static directory
echo "Copying to static directory..."
rm -rf ../src/sendell/web/static/browser/*
cp -r dist/sendell-dashboard/browser/* ../src/sendell/web/static/browser/

# 4. Verify files copied
echo "Verifying files..."
ls -lah ../src/sendell/web/static/browser/

echo "========================================="
echo "  Build complete!"
echo "  Files deployed to: src/sendell/web/static/browser/"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Restart the server (uv run python -m sendell chat)"
echo "2. Open browser and do HARD REFRESH (Ctrl+Shift+R)"
echo "3. Test clicking on a red project card"
