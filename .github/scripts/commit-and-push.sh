#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <commit-message> <path> [<path> ...]" >&2
  exit 2
fi

commit_message=$1
shift

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -- "$@"

if git diff --cached --quiet; then
  echo "No generated data changes to commit."
  exit 0
fi

# These jobs push to main with GITHUB_TOKEN, and such a push starts no
# workflow, so no later gate ever inspects what they wrote. This is the only
# place a source that briefly served a short listing can be stopped before it
# deletes retained records for good.
repo_root=$(git rev-parse --show-toplevel)
python "${repo_root}/scripts/check_sync_floor.py" --repo-root "${repo_root}" -- "$@"

git commit -m "$commit_message"

# Scheduled provider jobs intentionally run in parallel. If another provider
# publishes while this job is syncing, replay this narrow commit on the new
# main tip before retrying the push.
for attempt in 1 2 3 4 5; do
  if git push origin HEAD:main; then
    exit 0
  fi

  echo "Push attempt ${attempt} failed; rebasing on origin/main before retrying."
  if ! git fetch origin main; then
    echo "Fetch attempt ${attempt} failed; retrying." >&2
    sleep "$attempt"
    continue
  fi
  if ! git rebase origin/main; then
    git rebase --abort || true
    echo "Unable to rebase generated data on the latest main branch." >&2
    exit 1
  fi
  sleep "$attempt"
done

echo "Unable to publish generated data after ${attempt} push attempts." >&2
exit 1
