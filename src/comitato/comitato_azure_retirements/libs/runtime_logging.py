"""Operator-facing runtime logging for the Azure retirements exporter."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from .arm_client import ArmRequestTrace


class ExecutionReporter:
    def __init__(self, *, verbose: bool, console: Console | None = None) -> None:
        self._verbose = verbose
        self._console = console or Console(soft_wrap=True)
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
        self._console.print(Panel.fit(summary, title="🚀 Azure Retirements Export", border_style="cyan"))

    def section(self, emoji: str, title: str, description: str = "") -> None:
        self._console.print()
        self._console.rule(f"[bold cyan]{emoji} {escape(title)}[/bold cyan]")
        if description:
            self._console.print(f"[dim]{escape(description)}[/dim]")

    def step(self, message: str) -> None:
        self._console.print(f"• {escape(message)}")

    def detail(self, label: str, value: str, *, always: bool = False) -> None:
        if not always and not self._verbose:
            return
        self._console.print(f"  [dim]{escape(label)}:[/] {escape(value)}")

    def mapping(self, title: str, values: dict[str, object], *, always: bool = False) -> None:
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

    def success(self, message: str) -> None:
        self._console.print(f"✅ {escape(message)}", style="green")

    def warning(self, message: str) -> None:
        self._console.print(f"⚠️  {escape(message)}", style="yellow")

    def error(self, message: str) -> None:
        self._console.print(f"❌ {escape(message)}", style="red")

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
            diagnostics_table.add_row(severity, str(diagnostic_summary.get(severity, 0)))
        self._console.print(diagnostics_table)
