"""Report scheduled workflow health as GitHub issues.

Nothing in this repository used to react to a failed scheduled run, so
sync-incremental failed every week from 2026-07-13 to 2026-08-03 without
anyone learning of it while 86% of the published catalog went stale. This
script is the reaction: one open issue per unhealthy workflow, closed again
as soon as that workflow succeeds.

Requires the gh CLI with GH_TOKEN set.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).resolve().parents[1] / "workflows"
SELF_WORKFLOW = "workflow-health.yml"
HEALTH_LABEL = "workflow-health"
# "cancelled" is deliberately absent: deploy-pages cancels its own in-flight
# runs by design, so reporting it would bury the real failures. A workflow that
# only ever gets cancelled - as sync-hakka-cert did on 2026-07-08, 07-15 and
# 07-22 - is caught by the staleness pass instead.
UNHEALTHY_CONCLUSIONS = ("failure", "timed_out")


def _repository() -> str:
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if not repository:
        raise ValueError("GITHUB_REPOSITORY is not set")
    return repository


def _gh_api(path: str, *args: str) -> object:
    completed = subprocess.run(
        ["gh", "api", path, *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout or "null")


def _issue_title(workflow: str) -> str:
    return f"Workflow health: {workflow}"


def _ensure_label(repository: str) -> None:
    # A missing label makes issue creation fail outright, and a health report
    # that cannot be filed is worse than a noisy one.
    try:
        _gh_api(f"repos/{repository}/labels/{HEALTH_LABEL}")
    except subprocess.CalledProcessError:
        subprocess.run(
            [
                "gh", "api", f"repos/{repository}/labels",
                "-f", f"name={HEALTH_LABEL}",
                "-f", "color=B60205",
                "-f", "description=Automated scheduled-workflow health reports",
            ],
            check=False,
            capture_output=True,
            text=True,
        )


def _open_health_issue(repository: str, workflow: str) -> dict | None:
    issues = _gh_api(
        f"repos/{repository}/issues",
        "-X", "GET",
        "-f", "state=open",
        "-f", f"labels={HEALTH_LABEL}",
        "-f", "per_page=100",
    )
    title = _issue_title(workflow)
    for issue in issues or []:
        if issue.get("title") == title and "pull_request" not in issue:
            return issue
    return None


def _create_issue(repository: str, workflow: str, body: str) -> None:
    _ensure_label(repository)
    subprocess.run(
        [
            "gh", "api", f"repos/{repository}/issues",
            "-f", f"title={_issue_title(workflow)}",
            "-f", f"body={body}",
            "-f", f"labels[]={HEALTH_LABEL}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _comment(repository: str, number: int, body: str) -> None:
    subprocess.run(
        ["gh", "api", f"repos/{repository}/issues/{number}/comments", "-f", f"body={body}"],
        check=True,
        capture_output=True,
        text=True,
    )


def _close(repository: str, number: int, body: str) -> None:
    _comment(repository, number, body)
    subprocess.run(
        ["gh", "api", f"repos/{repository}/issues/{number}", "-X", "PATCH", "-f", "state=closed"],
        check=True,
        capture_output=True,
        text=True,
    )


def report(workflow: str, conclusion: str, run_url: str) -> int:
    repository = _repository()
    existing = _open_health_issue(repository, workflow)

    if conclusion in UNHEALTHY_CONCLUSIONS:
        body = f"`{workflow}` concluded **{conclusion}**.\n\nRun: {run_url}"
        if existing is None:
            _create_issue(repository, workflow, body)
            print(f"opened health issue for {workflow}")
        else:
            _comment(repository, existing["number"], body)
            print(f"updated health issue #{existing['number']} for {workflow}")
        return 0

    if conclusion == "success" and existing is not None:
        _close(repository, existing["number"], f"`{workflow}` succeeded again.\n\nRun: {run_url}")
        print(f"closed health issue #{existing['number']} for {workflow}")
        return 0

    print(f"no health action for {workflow} ({conclusion})")
    return 0


def _interval_days(text: str) -> int:
    # A cron's cadence decides how long silence is allowed to mean nothing. The
    # fields are `minute hour day-of-month month day-of-week`, so a restricted
    # day-of-month runs monthly, a restricted day-of-week runs weekly, and
    # anything else runs at least daily. A workflow with several crons is only
    # as quiet as its most frequent one.
    intervals = []
    for line in text.splitlines():
        _, _, expression = line.partition("cron:")
        fields = expression.strip().strip("\"'").split()
        if len(fields) != 5:
            continue
        day_of_month, day_of_week = fields[2], fields[4]
        if day_of_month != "*":
            intervals.append(31)
        elif day_of_week != "*":
            intervals.append(7)
        else:
            intervals.append(1)
    return min(intervals, default=1)


def _scheduled_workflow_paths() -> dict[str, int]:
    # Read the checked-out workflow files rather than guessing from the API:
    # only a `schedule:` trigger makes a staleness window meaningful, and this
    # is the same source the workflow_run list is generated from. The value is
    # the workflow's cadence in days, which sets its staleness window.
    paths = {}
    for path in sorted(WORKFLOWS_DIR.glob("*.yml")):
        # This workflow is excluded for the same reason it is absent from its
        # own workflow_run list. Its staleness pass runs before that same run
        # can succeed, so it would report itself as never having succeeded, and
        # nothing would ever close the issue: recovery is only detected through
        # workflow_run, which it does not receive for itself.
        if path.name == SELF_WORKFLOW:
            continue
        text = path.read_text(encoding="utf-8")
        if "\n  schedule:\n" in text:
            paths[f".github/workflows/{path.name}"] = _interval_days(text)
    return paths


def _scheduled_workflows(repository: str) -> list[dict]:
    # -X GET is load-bearing: gh turns a bare -f into a request body and posts it.
    payload = _gh_api(f"repos/{repository}/actions/workflows", "-X", "GET", "-f", "per_page=100")
    workflows = (payload or {}).get("workflows", [])
    scheduled = _scheduled_workflow_paths()
    return [
        {**w, "interval_days": scheduled[w["path"]]}
        for w in workflows
        if w.get("state") == "active" and w.get("path") in scheduled
    ]


def _last_success(repository: str, workflow_id: int) -> datetime | None:
    payload = _gh_api(
        f"repos/{repository}/actions/workflows/{workflow_id}/runs",
        "-X", "GET",
        "-f", "status=success",
        "-f", "event=schedule",
        "-f", "per_page=1",
    )
    runs = (payload or {}).get("workflow_runs", [])
    if not runs:
        return None
    return datetime.fromisoformat(runs[0]["created_at"].replace("Z", "+00:00"))


def stale(max_age_days: int) -> int:
    repository = _repository()
    now = datetime.now(timezone.utc)
    unhealthy = 0

    for workflow in _scheduled_workflows(repository):
        name = workflow["name"]
        # A flat window cannot judge every cadence: audit-recent runs on the 1st
        # of the month, so a fixed 14 days marked it stale from the 15th onwards
        # every month no matter how healthy it was. Allow two missed runs, which
        # is exactly what 14 days already meant for the weekly syncs that make up
        # every other scheduled workflow here. Losing tightness on the monthly
        # one costs nothing: an outright failure is reported the moment it
        # happens by the workflow_run pass, and this pass only exists to catch a
        # schedule that silently stopped firing at all.
        window = max(max_age_days, 2 * workflow["interval_days"])
        last = _last_success(repository, workflow["id"])
        if last is not None and last >= now - timedelta(days=window):
            continue

        age = "never" if last is None else f"{(now - last).days} days ago"
        body = (
            f"`{name}` has no successful scheduled run within the last {window} days "
            f"(last success: {age}).\n\n"
            "A scheduled sync that stops succeeding silently leaves the published catalog stale."
        )
        existing = _open_health_issue(repository, name)
        if existing is None:
            _create_issue(repository, name, body)
            print(f"opened staleness issue for {name}")
        else:
            print(f"staleness already tracked in #{existing['number']} for {name}")
        unhealthy += 1

    print(f"{unhealthy} workflow(s) without a recent successful scheduled run")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    report_parser = sub.add_parser("report", help="File or resolve a health issue for one run")
    report_parser.add_argument("--workflow", required=True)
    report_parser.add_argument("--conclusion", required=True)
    report_parser.add_argument("--run-url", required=True)

    stale_parser = sub.add_parser("stale", help="Report workflows with no recent successful scheduled run")
    stale_parser.add_argument("--max-age-days", type=int, default=14)

    args = parser.parse_args(argv)
    if args.command == "report":
        return report(args.workflow, args.conclusion, args.run_url)
    return stale(args.max_age_days)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
