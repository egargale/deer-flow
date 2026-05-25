#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────────────────────────────────────
# Sync & Deploy — pulls upstream changes, rebases local commits, pushes to fork,
#                  (optionally) redeploys Docker production containers.
#
# Usage:
#   ./scripts/sync-and-deploy.sh             # sync + push only
#   ./scripts/sync-and-deploy.sh --deploy    # sync + push + docker redeploy
#   ./scripts/sync-and-deploy.sh --help      # show this message
# ──────────────────────────────────────────────────────────────────────────────

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== DeerFlow Sync & Deploy ==="
echo "  Repo:     $(pwd)"
echo "  Upstream: $(git remote get-url upstream 2>/dev/null || echo '(not set)')"
echo "  Origin:   $(git remote get-url origin 2>/dev/null || echo '(not set)')"
echo "  Branch:   $(git branch --show-current)"
echo ""

# ── 1. Stash any uncommitted changes ────────────────────────────────────────
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "📦 Stashing uncommitted changes..."
    git stash push -m "auto-stash before sync $(date +%Y-%m-%d_%H:%M:%S)"
    STASHED=true
else
    STASHED=false
fi

# ── 2. Fetch upstream ────────────────────────────────────────────────────────
echo "⬇️  Fetching upstream..."
UPSTREAM_REMOTE=$(git remote get-url upstream 2>/dev/null && echo "upstream" || echo "origin")
git fetch "$UPSTREAM_REMOTE" main

# ── 3. Rebase local commits on upstream/main ─────────────────────────────────
if [ "$(git rev-list --count HEAD.."$UPSTREAM_REMOTE"/main)" -gt 0 ]; then
    echo "🔄 Rebasing local commits on $UPSTREAM_REMOTE/main..."
    git rebase "$UPSTREAM_REMOTE"/main
    echo "✅ Rebase complete."
else
    echo "✅ Local branch is already up to date with $UPSTREAM_REMOTE/main."
fi

# ── 4. Push to origin (your fork) ────────────────────────────────────────────
echo "⬆️  Pushing to origin/main..."
git push origin main

# ── 5. Restore stash ─────────────────────────────────────────────────────────
if [ "$STASHED" = true ]; then
    echo "📂 Restoring stashed changes..."
    git stash pop
fi

echo ""
echo "✅ Sync complete! $(git rev-list --count HEAD.."$UPSTREAM_REMOTE"/main) commits behind upstream, $(git rev-list --count "$UPSTREAM_REMOTE"/main..HEAD) local commits ahead."

# ── 6. Optional Docker redeploy ──────────────────────────────────────────────
if [ "${1:-}" = "--deploy" ]; then
    echo ""
    echo "🐳 Redeploying Docker production containers..."
    make down 2>/dev/null || true
    make up
    echo "✅ Deployment complete."
fi
