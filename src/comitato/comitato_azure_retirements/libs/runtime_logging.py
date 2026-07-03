"""Operator-facing runtime logging for the Azure retirements exporter."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from .arm_client import ArmRequestTrace
from .debug_log import DebugRunLogger

SubscriptionProgressCallback = Callable[[str, int, int, str, str | None], None]


class ExecutionReporter:
    def __init__(
        self,
        *,
        verbose: bool,
        console: Console | None = None,
        debug_logger: DebugRunLogger | None = None,
    ) -> None:
        self._verbose = verbose
        self._console = console or Console(soft_wrap=True)
        self._debug_logger = debug_logger
        self._reported_retries: set[str] = set()

    def banner(
        self,
        *,
        run_id: str,
        mode: str,
        scope_mode: str,
        output_dir: Path,
        subscriptions: list[str],
        management_groups: list[str],
        write_raw_jsonl: bool,
    ) -> None:
        summary = Table.grid(padding=(0, 2))
        summary.add_row("Run ID", run_id)
        summary.add_row("Mode", mode)
        summary.add_row("Scope", scope_mode)
        summary.add_row("Subscriptions", str(len(subscriptions)))
        summary.add_row("Management Groups", str(len(management_groups)))
        summary.add_row("Raw JSONL", "enabled" if write_raw_jsonl else "disabled")
        summary.add_row("Output", str(output_dir))
        self._console.print(
            Panel.fit(summary, title="🚀 Azure Retirements Export", border_style="cyan")
        )
        if self._debug_logger is not None:
            self._debug_logger.info(
                "run_banner",
                "Runtime banner emitted",
                mode=mode,
                scope_mode=scope_mode,
                output_dir=str(output_dir),
                subscriptions_count=len(subscriptions),
                management_groups_count=len(management_groups),
                write_raw_jsonl=write_raw_jsonl,
            )

    def section(self, emoji: str, title: str, description: str = "") -> None:
        self._console.print()
        self._console.rule(f"[bold cyan]{emoji} {escape(title)}[/bold cyan]")
        if description:
            self._console.print(f"[dim]{escape(description)}[/dim]")
        if self._debug_logger is not None:
            self._debug_logger.info(
                "section",
                "Runtime section started",
                section_title=title,
                section_description=description,
            )

    def step(self, message: str) -> None:
        self._console.print(f"• {escape(message)}")
        if self._debug_logger is not None:
            self._debug_logger.info("step", message)

    def detail(self, label: str, value: str, *, always: bool = False) -> None:
        if not always and not self._verbose:
            return
        self._console.print(f"  [dim]{escape(label)}:[/] {escape(value)}")
        if self._debug_logger is not None:
            self._debug_logger.info(
                "detail", "Runtime detail", label=label, value=value
            )

    def mapping(
        self, title: str, values: Mapping[str, object], *, always: bool = False
    ) -> None:
        if not values:
            return
        if not always and not self._verbose:
            return

        table = Table(title=f"📋 {title}", header_style="bold blue")
        table.add_column("Key")
        table.add_column("Value")
        for key, value in values.items():
            table.add_row(str(key), str(value))
        self._console.print(table)
        if self._debug_logger is not None:
            self._debug_logger.info(
                "mapping", "Runtime mapping emitted", title=title, values=values
            )

    @contextmanager
    def subscription_progress(
        self, title: str, total: int
    ) -> Iterator[SubscriptionProgressCallback]:
        if total <= 0:
            yield lambda *_args, **_kwargs: None
            return

        progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(bar_width=28),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self._console,
            transient=False,
        )

        with progress:
            task_id = progress.add_task(f"{escape(title)} · starting", total=total)

            def _update(
                subscription_id: str,
                completed: int,
                overall_total: int,
                status: str,
                error: str | None,
            ) -> None:
                total_units = max(overall_total, 1)
                completed_units = max(0, min(completed, total_units))
                percent = int((completed_units / total_units) * 100)
                short_subscription = (
                    subscription_id
                    if len(subscription_id) <= 12
                    else f"…{subscription_id[-12:]}"
                )
                status_icon = {
                    "ok": "✅",
                    "warning": "⚠️",
                    "error": "❌",
                }.get(status, "•")
                description = (
                    f"{escape(title)} · {status_icon} {escape(status)} · "
                    f"{escape(short_subscription)} · {percent}%"
                )
                progress.update(
                    task_id,
                    total=total_units,
                    completed=completed_units,
                    description=description,
                )
                if self._debug_logger is not None:
                    self._debug_logger.info(
                        "subscription_progress",
                        "Subscription progress update",
                        collector=title,
                        subscription_id=subscription_id,
                        completed=completed_units,
                        total=total_units,
                        status=status,
                        error=error,
                    )

                if error and status in {"warning", "error"} and self._verbose:
                    self.detail(
                        "Subscription issue",
                        f"{subscription_id}: {error}",
                        always=True,
                    )

            yield _update
            progress.update(
                task_id,
                completed=total,
                description=f"{escape(title)} · ✅ completed · 100%",
            )

    def problem_determination_report(
        self, title: str, rows: list[dict[str, str]]
    ) -> None:
        if not rows:
            return

        table = Table(title=title, header_style="bold yellow")
        table.add_column("Collector")
        table.add_column("Subscription")
        table.add_column("Severity")
        table.add_column("Detail")

        for row in rows:
            detail = row.get("detail", "")
            if len(detail) > 140:
                detail = f"{detail[:137]}..."
            table.add_row(
                row.get("collector", ""),
                row.get("subscription", ""),
                row.get("severity", ""),
                detail,
            )

        self._console.print(table)
        if self._debug_logger is not None:
            self._debug_logger.warning(
                "problem_determination",
                "Problem determination table emitted",
                title=title,
                rows=rows,
            )

    def success(self, message: str) -> None:
        self._console.print(f"✅ {escape(message)}", style="green")
        if self._debug_logger is not None:
            self._debug_logger.info("success", message)

    def warning(self, message: str) -> None:
        self._console.print(f"⚠️  {escape(message)}", style="yellow")
        if self._debug_logger is not None:
            self._debug_logger.warning("warning", message)

    def error(self, message: str) -> None:
        self._console.print(f"❌ {escape(message)}", style="red")
        if self._debug_logger is not None:
            self._debug_logger.error("error", message)

    def observe_request(self, trace: ArmRequestTrace) -> None:
        if trace.retry_count < 1:
            return

        parsed = urlparse(trace.url)
        path = parsed.path or trace.url
        dedupe_key = f"{trace.method}:{path}:{trace.status_code}"
        if dedupe_key in self._reported_retries and not self._verbose:
            return

        self.warning(
            f"HTTP retry applied {trace.retry_count} time(s) before {trace.status_code} on {path}"
        )
        if self._debug_logger is not None:
            self._debug_logger.warning(
                "http_retry",
                "HTTP retry applied",
                method=trace.method,
                url=trace.url,
                status_code=trace.status_code,
                retry_count=trace.retry_count,
            )
        if not self._verbose:
            self._reported_retries.add(dedupe_key)

    def summary(
        self,
        *,
        output_dir: Path,
        counts_by_file: dict[str, int],
        counts_by_source: dict[str, int],
        diagnostic_summary: dict[str, int],
    ) -> None:
        self.section("✅", "Run Summary", "Export completed with the counts below")
        self.step(f"Output directory: {output_dir}")

        file_table = Table(title="📝 Output Files", header_style="bold green")
        file_table.add_column("File")
        file_table.add_column("Rows", justify="right")
        for name, count in counts_by_file.items():
            file_table.add_row(name, str(count))
        self._console.print(file_table)

        source_table = Table(title="📦 Source Totals", header_style="bold magenta")
        source_table.add_column("Source")
        source_table.add_column("Items", justify="right")
        for name, count in counts_by_source.items():
            source_table.add_row(name, str(count))
        self._console.print(source_table)

        diagnostics_table = Table(title="🩺 Diagnostics", header_style="bold yellow")
        diagnostics_table.add_column("Severity")
        diagnostics_table.add_column("Count", justify="right")
        for severity in ("info", "warning", "error"):
            diagnostics_table.add_row(
                severity, str(diagnostic_summary.get(severity, 0))
            )
        self._console.print(diagnostics_table)
        if self._debug_logger is not None:
            self._debug_logger.info(
                "run_summary",
                "Run summary emitted",
                output_dir=str(output_dir),
                counts_by_file=counts_by_file,
                counts_by_source=counts_by_source,
                diagnostic_summary=diagnostic_summary,
            )
