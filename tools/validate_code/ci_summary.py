"""Render the GitHub Actions validation overview without external dependencies."""

from __future__ import annotations

import argparse
import html
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


def _text(value: object) -> str:
    return html.escape(str(value)).replace("|", "&#124;").replace("\n", " ")


def _status(value: str) -> str:
    icon = {
        "success": "✅",
        "failure": "❌",
        "cancelled": "🚫",
        "skipped": "⏭️",
        "in_progress": "⏳",
        "queued": "⏳",
    }.get(value, "⚠️")
    return f"{icon} {_text(value)}"


def render_summary(
    needs: dict[str, Any], jobs: list[dict[str, Any]], run_url: str
) -> str:
    success = bool(needs) and all(
        category.get("result") == "success" for category in needs.values()
    )
    checks = [job for job in jobs if job["name"] != "code-analysis"]
    counts = Counter(job.get("conclusion") or "incomplete" for job in checks)
    lines = [
        "# Code analysis",
        "",
        "**✅ PASS - All validation categories succeeded.**"
        if success
        else "**⚠️ NOT PASSED - Validation requires attention.**",
        "",
        "Static analysis, Python tests and integrity, Terraform validation and tests.",
        "",
        f"[Workflow run]({run_url}) | [Logs and artifacts]({run_url}#artifacts)",
    ]
    failures = [job for job in checks if job.get("conclusion") != "success"]
    if failures:
        lines.extend(["", "## ⚠️ Attention required", ""])
        for job in failures:
            steps = [
                step["name"]
                for step in job.get("steps", [])
                if step.get("conclusion") == "failure"
            ]
            lines.append(
                f"- [{_text(job['name'])}]({job['html_url']}): "
                + (
                    _text("; ".join(steps))
                    if steps
                    else _text(job.get("conclusion") or "incomplete")
                )
            )
        lines.extend(
            [
                "",
                "> 💡 Open the failed job and start with the step listed above."
                if any(job.get("conclusion") == "failure" for job in failures)
                else "> 💡 Open the job logs to check why validation did not complete.",
            ]
        )
    lines.extend(
        [
            "",
            "## 🗂️ Categories",
            "",
            "| Category | Result |",
            "| --- | --- |",
        ]
    )
    category_labels = {
        "static": "🔎 Static analysis",
        "python": "🧪 Python tests & integrity",
        "terraform": "🏗️ Terraform",
    }
    for category, result in needs.items():
        label = category_labels.get(category, category)
        lines.append(f"| {_text(label)} | **{_status(result['result'])}** |")
    if not checks:
        lines.extend(
            [
                "",
                "> Job details are unavailable. Category results above remain authoritative.",
                "Use the workflow run link to inspect individual checks.",
            ]
        )
        return "\n".join(lines) + "\n"
    lines.extend(
        [
            "",
            "## 🔬 Checks",
            "",
            f"{len(checks)} checks: {counts['success']} passed, "
            f"{counts['failure']} failed, {counts['cancelled']} cancelled, "
            f"{len(checks) - counts['success'] - counts['failure'] - counts['cancelled']} other/not completed.",
            "",
            "| Check | Result | Duration | Logs |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for job in sorted(checks, key=lambda item: item["name"]):
        duration = "-"
        if job.get("started_at") and job.get("completed_at"):
            seconds = max(
                0,
                int(
                    (
                        datetime.fromisoformat(
                            job["completed_at"].replace("Z", "+00:00")
                        )
                        - datetime.fromisoformat(
                            job["started_at"].replace("Z", "+00:00")
                        )
                    ).total_seconds()
                ),
            )
            duration = f"{seconds // 60}m {seconds % 60:02d}s"
        status = job.get("conclusion") or job.get("status") or "incomplete"
        lines.append(
            f"| {_text(job['name'])} | **{_status(status)}** | {duration} | "
            f"[Open job]({job['html_url']}) |"
        )
    lines.extend(
        [
            "",
            "<details>",
            "<summary>📎 Evidence and local reproduction</summary>",
            "",
            "Artifacts named `validation-*` contain `result.json` and per-unit logs.",
            "If setup failed before validation started, inspect the failed step instead.",
            "Durations include job setup; parallel job durations are not added together.",
            "",
            "```bash",
            "./validate-code.sh",
            "```",
            "",
            "To isolate a check, use `static --leaf NAME`, `python --group NAME`, "
            "`python --integrity-only`, or `terraform --lane NAME`.",
            "",
            "</details>",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=Path, required=True)
    args = parser.parse_args()
    needs = json.loads(os.environ["VALIDATION_RESULTS"])
    try:
        pages = json.loads(args.jobs.read_text(encoding="utf-8"))
        jobs = [job for page in pages for job in page["jobs"]]
    except (OSError, ValueError, KeyError, TypeError):
        jobs = []
    run_url = (
        f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
        f"/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    )
    print(render_summary(needs, jobs, run_url), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
