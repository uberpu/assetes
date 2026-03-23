#!/bin/bash
set -e

# We need to fetch the past training logs and manifest from the gh-pages branch
# so that the current run can append to them instead of overwriting.
# If gh-pages doesn't exist yet, we just silently continue.

echo "Attempting to fetch historical logs from gh-pages..."
mkdir -p /tmp/gh-pages
git clone --branch gh-pages --single-branch https://${GITHUB_ACTOR}:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git /tmp/gh-pages 2>/dev/null || echo "No gh-pages branch found. Starting fresh."

if [ -d "/tmp/gh-pages" ]; then
    echo "Found historical data. Copying to docs/"
    cp -r /tmp/gh-pages/models docs/ 2>/dev/null || true
    cp /tmp/gh-pages/*_log.md docs/ 2>/dev/null || true
fi
