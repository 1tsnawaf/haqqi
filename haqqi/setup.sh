#!/usr/bin/env bash
# Haqqi -> GitHub, one shot.
# Usage:  bash setup.sh <your-github-username> [repo-name] [public|private]
set -e

USER="${1:?Usage: bash setup.sh <github-username> [repo-name] [public|private]}"
REPO="${2:-haqqi}"
VIS="${3:-private}"

echo "==> Initializing git"
git init -q 2>/dev/null || true
git add .
git commit -q -m "Haqqi: initial scaffold" 2>/dev/null || echo "   (nothing new to commit)"
git branch -M main

if command -v gh >/dev/null 2>&1; then
  echo "==> Found GitHub CLI — creating repo and pushing"
  gh repo create "$REPO" --"$VIS" --source=. --remote=origin --push
  echo "==> Done: https://github.com/$USER/$REPO"
else
  echo "==> GitHub CLI not found. Create an EMPTY repo named '$REPO' on github.com first,"
  echo "    then this script will connect and push:"
  read -p "    Press Enter once you've created https://github.com/$USER/$REPO ..." _
  git remote add origin "https://github.com/$USER/$REPO.git" 2>/dev/null || \
    git remote set-url origin "https://github.com/$USER/$REPO.git"
  git push -u origin main
  echo "==> Done: https://github.com/$USER/$REPO"
fi
