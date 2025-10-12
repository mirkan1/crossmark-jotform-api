#!/bin/bash
# Script to run tests with coverage

echo "Running tests with coverage..."

# Navigate to project directory
cd "$(dirname "$0")"

# Run tests with coverage
python -m pytest \
    --cov=src/crossmark_jotform_api \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-branch \
    -v \
    tests/

echo ""
echo "Coverage report generated:"
echo "- HTML: htmlcov/index.html"
echo "- XML: coverage.xml"
echo "- Terminal output above"