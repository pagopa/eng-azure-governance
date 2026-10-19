import json
import os
import signal
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "src"
    / "azure-policy"
    / "tools"
    / "prod-sec-remove-security-locks.sh"
)
SUBSCRIPTION = "0da48c97-355f-4050-a520-f11a18b8be90"
ROOT = f"/subscriptions/{SUBSCRIPTION}"
RESOURCES = [
    f"{ROOT}/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs",
    f"{ROOT}/resourceGroups/sec-p-rg-nit/providers/Microsoft.Storage/storageAccounts/ppseclogsitn",
    f"{ROOT}/resourceGroups/sec-p-rg-neu/providers/Microsoft.Storage/storageAccounts/ppseclogsneu",
    f"{ROOT}/resourceGroups/sec-p-sentinel/providers/Microsoft.OperationalInsights/workspaces/sec-p-law",
]


def lock(scope: str, name: str = "policy-lock") -> dict[str, str]:
    return {
        "id": f"{scope}/providers/Microsoft.Authorization/locks/{name}",
        "name": name,
        "level": "CanNotDelete",
    }


@pytest.fixture
def cli(tmp_path: Path):
    state = tmp_path / "state.json"
    trace = tmp_path / "trace.jsonl"
    state.write_text(json.dumps({"locks": [lock(item) for item in RESOURCES]}))
    fake_az = tmp_path / "az"
    fake_az.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "state_path = Path(os.environ['FAKE_STATE'])\n"
        "state = json.loads(state_path.read_text())\n"
        "with open(os.environ['FAKE_TRACE'], 'a') as stream:\n"
        "    stream.write(json.dumps(args) + '\\n')\n"
        "if args[:2] == ['account', 'show']:\n"
        f"    print(json.dumps({{'id': state.get('account_id', '{SUBSCRIPTION}'), 'name': 'PROD-SEC', 'state': 'Enabled'}}))\n"
        "elif args[:2] == ['lock', 'list']:\n"
        "    if state.get('list_error') or (state.get('verify_error') and state.get('deleted')):\n"
        "        print('AuthorizationFailed: cannot read locks', file=sys.stderr)\n"
        "        sys.exit(1)\n"
        "    payload = state.get('payload', state['locks'])\n"
        "    if state.get('deleted'):\n"
        "        payload = state.get('after_locks', payload)\n"
        "    print(json.dumps(payload))\n"
        "elif args[:2] == ['lock', 'delete']:\n"
        "    if state.get('interrupt_signal'):\n"
        "        os.kill(os.getppid(), state['interrupt_signal'])\n"
        "        sys.exit(1)\n"
        "    if state.get('consume_stdin'):\n"
        "        sys.stdin.read()\n"
        "    target = args[args.index('--ids') + 1]\n"
        "    if target == state.get('fail_id'):\n"
        "        if state.get('fail_after_delete'):\n"
        "            state['deleted'] = True\n"
        "            state['locks'] = [item for item in state['locks'] if item['id'] != target]\n"
        "            state_path.write_text(json.dumps(state))\n"
        "            print('Timeout: response lost after deletion', file=sys.stderr)\n"
        "            sys.exit(1)\n"
        "        print('AuthorizationFailed: cannot delete lock', file=sys.stderr)\n"
        "        sys.exit(1)\n"
        "    state['deleted'] = True\n"
        "    if not state.get('reappear'):\n"
        "        state['locks'] = [item for item in state['locks'] if item['id'] != target]\n"
        "    state_path.write_text(json.dumps(state))\n"
        "else:\n"
        "    print('Unexpected Azure operation', file=sys.stderr)\n"
        "    sys.exit(90)\n",
        encoding="utf-8",
    )
    fake_az.chmod(0o755)
    environment = dict(
        os.environ,
        PATH=f"{tmp_path}{os.pathsep}{os.environ['PATH']}",
        FAKE_STATE=str(state),
        FAKE_TRACE=str(trace),
        TMPDIR=str(tmp_path),
        NO_COLOR="1",
    )

    def run(
        *arguments: str,
        confirmation: str = "",
        interpreter: str | None = None,
        **updates,
    ):
        current = json.loads(state.read_text())
        current.update(updates)
        state.write_text(json.dumps(current))
        assert SCRIPT.exists(), "Missing security lock removal entrypoint"
        command = [str(SCRIPT), *arguments]
        if interpreter is not None:
            command.insert(0, interpreter)
        result = subprocess.run(
            command,
            input=confirmation,
            text=True,
            capture_output=True,
            env=environment,
            cwd=tmp_path,
            timeout=15,
            check=False,
        )
        calls = (
            [json.loads(line) for line in trace.read_text().splitlines()]
            if trace.exists()
            else []
        )
        return result, calls, json.loads(state.read_text())

    return run


def deletions(calls: list[list[str]]) -> list[str]:
    return [
        args[args.index("--ids") + 1]
        for args in calls
        if args[:2] == ["lock", "delete"]
    ]


def test_explicit_dry_run_never_prompts_or_deletes_and_lists_all_resources(cli):
    result, calls, _ = cli("--dry-run", confirmation="yes\n")
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert "Azure display name: PROD-SEC" in result.stdout
    assert not deletions(calls)
    assert all(item.rsplit("/", 1)[-1] in result.stdout for item in RESOURCES)
    assert ROOT not in result.stdout
    assert "CanNotDelete" in result.stdout
    assert "DRY RUN" in result.stdout
    assert f"PROD-SEC ({SUBSCRIPTION})" in result.stdout
    assert "📋 PREVIEW" in result.stdout
    assert "No locks removed." in result.stdout
    assert "REMOVAL RESULTS" not in result.stdout
    assert "Resource group" in result.stdout
    assert "[yes/no]" not in result.stdout


def test_default_run_offers_apply_after_plan_and_yes_deletes(cli):
    result, calls, state = cli(confirmation="yes\n")
    assert result.returncode == 0, result.stderr
    assert len(deletions(calls)) == 4
    assert state["locks"] == []
    assert "Removed: 4" in result.stdout
    assert result.stdout.index("📋 PREVIEW") < result.stdout.index("[yes/no]")
    assert result.stdout.index("[yes/no]") < result.stdout.index("🔄 REMOVAL")
    for args in calls:
        assert args[2:] == (
            ["--ids", args[3]] if args[:2] == ["lock", "delete"] else []
        ) + ["--subscription", SUBSCRIPTION] + (
            [] if args[:2] == ["lock", "delete"] else ["--output", "json"]
        ) + ["--only-show-errors"]


@pytest.mark.parametrize("confirmation", ["", "\n", "no\n"])
def test_default_run_cancels_without_affirmative_answer(cli, confirmation):
    result, calls, _ = cli(confirmation=confirmation)
    assert result.returncode == 3
    assert not deletions(calls)
    assert "CANCELLED" in result.stdout


def test_confirmed_apply_deletes_only_direct_allowlisted_locks(cli):
    extras = [
        lock(ROOT),
        lock(f"{ROOT}/resourceGroups/sec-p-sentinel"),
        lock(RESOURCES[0] + "-other"),
    ]
    result, calls, state = cli(
        "--apply",
        confirmation="yes\n",
        locks=[lock(item) for item in RESOURCES] + extras,
    )
    assert result.returncode == 1, result.stdout
    assert set(deletions(calls)) == {lock(item)["id"] for item in RESOURCES}
    assert state["locks"] == extras
    assert "INHERITED" in result.stdout
    assert "Removed: 4" in result.stdout
    assert "Inherited locks: 2" in result.stdout
    assert all(SUBSCRIPTION in args for args in calls)


@pytest.mark.parametrize(
    "confirmation", ["", "\n", "no\n", "y\n", "REMOVE wrong-subscription\n"]
)
def test_apply_refuses_missing_or_wrong_confirmation(cli, confirmation):
    result, calls, _ = cli("--apply", confirmation=confirmation)
    assert result.returncode == 3
    assert not deletions(calls)
    assert "CANCELLED" in result.stdout


def test_partial_delete_failure_continues_and_reports_error(cli):
    result, calls, state = cli(
        "--apply",
        confirmation="yes\n",
        fail_id=lock(RESOURCES[0])["id"],
    )
    assert result.returncode == 1
    assert len(deletions(calls)) == 4
    assert state["locks"] == [lock(RESOURCES[0])]
    assert "AuthorizationFailed" in result.stdout + result.stderr
    assert "Planned: 4 | Removed: 3 | Still present: 1" in result.stdout
    assert "Request errors: 1" in result.stdout
    assert "✅ REMOVED AND VERIFIED" in result.stdout
    assert "⚠️ REQUEST ERRORS" in result.stdout
    assert "FAILED REMOVALS" not in result.stdout
    assert "PARTIALLY COMPLETED" in result.stdout
    preview = result.stdout.index("📋 PREVIEW")
    removal = result.stdout.index("🔄 REMOVAL")
    summary = result.stdout.index("📊 REMOVAL RESULTS")
    assert preview < removal < summary
    assert "AuthorizationFailed" in result.stdout[summary:]
    assert "AuthorizationFailed" not in result.stdout[:summary]
    assert "[yes/no]" in result.stdout


def test_reappearing_locks_are_not_reported_removed(cli):
    result, _, _ = cli("--apply", confirmation="yes\n", reappear=True)
    assert result.returncode == 1
    assert "Planned: 4 | Removed: 0 | Still present: 4" in result.stdout
    assert "Request errors: 0" in result.stdout
    assert "STILL PRESENT" in result.stdout


def test_failed_request_with_lock_verified_absent_is_counted_removed(cli):
    result, calls, state = cli(
        confirmation="yes\n",
        fail_id=lock(RESOURCES[0])["id"],
        fail_after_delete=True,
    )
    assert result.returncode == 0, result.stderr
    assert len(deletions(calls)) == 4
    assert state["locks"] == []
    assert "Planned: 4 | Removed: 4 | Still present: 0" in result.stdout
    assert "Request errors: 1" in result.stdout
    assert "Timeout: response lost after deletion" in result.stdout
    assert "COMPLETED WITH REQUEST WARNINGS" in result.stdout
    assert "PARTIALLY COMPLETED" not in result.stdout


def test_new_lock_after_plan_is_reported_separately_without_deletion(cli):
    new_lock = lock(RESOURCES[0], "new-policy-lock")
    result, calls, _ = cli(confirmation="yes\n", after_locks=[new_lock])
    assert result.returncode == 1
    assert new_lock["id"] not in deletions(calls)
    assert len(deletions(calls)) == 4
    assert "Planned: 4 | Removed: 4 | Still present: 0" in result.stdout
    assert "New/unplanned locks: 1" in result.stdout
    assert "NEW / UNPLANNED LOCKS" in result.stdout
    assert "new-policy-lock" in result.stdout


def test_azure_command_cannot_consume_remaining_planned_lock_ids(cli):
    result, calls, state = cli(confirmation="yes\n", consume_stdin=True)
    assert result.returncode == 0, result.stderr
    assert len(deletions(calls)) == 4
    assert state["locks"] == []
    assert "Planned: 4 | Removed: 4 | Still present: 0" in result.stdout


@pytest.mark.parametrize("level", ["NotSpecified", "FutureLevel", None])
def test_unrelated_lock_level_does_not_block_target_removals(cli, level):
    unrelated = dict(lock(f"{ROOT}/resourceGroups/unrelated-rg"), level=level)
    result, calls, state = cli(
        confirmation="yes\n", locks=[lock(item) for item in RESOURCES] + [unrelated]
    )
    assert result.returncode == 0, result.stderr
    assert len(deletions(calls)) == 4
    assert unrelated["id"] not in deletions(calls)
    assert state["locks"] == [unrelated]


@pytest.mark.parametrize(
    "scope", [RESOURCES[0], ROOT, f"{ROOT}/resourceGroups/sec-p-sentinel"]
)
def test_unknown_level_on_target_or_inherited_lock_prevents_mutation(cli, scope):
    unsupported = dict(lock(scope), level="NotSpecified")
    result, calls, _ = cli(
        confirmation="yes\n", locks=[lock(item) for item in RESOURCES] + [unsupported]
    )
    assert result.returncode == 1
    assert not deletions(calls)
    assert "Malformed Azure lock response" in result.stderr


def test_no_locks_is_safe_to_rerun_without_confirmation(cli):
    result, calls, _ = cli("--apply", locks=[])
    assert result.returncode == 0, result.stderr
    assert not deletions(calls)
    assert "Absent at start (resources): 4" in result.stdout


@pytest.mark.parametrize(
    "updates", [{"list_error": True}, {"payload": {}}, {"payload": [{"id": "bad"}]}]
)
def test_failed_or_malformed_discovery_prevents_mutation(cli, updates):
    result, calls, _ = cli("--apply", confirmation="yes\n", **updates)
    assert result.returncode == 1
    assert not deletions(calls)
    assert "FAILED [DISCOVERY]" in result.stderr


def test_wrong_account_is_rejected(cli):
    result, calls, _ = cli("--apply", account_id="another-subscription")
    assert result.returncode == 1
    assert not deletions(calls)
    assert "FAILED [PREFLIGHT]" in result.stderr


@pytest.mark.parametrize(
    ("interrupt_signal", "expected_code"), [(signal.SIGINT, 130), (signal.SIGTERM, 143)]
)
def test_interruption_stops_deletion_and_cleans_temporary_files(
    cli, tmp_path, interrupt_signal, expected_code
):
    result, calls, state = cli(confirmation="yes\n", interrupt_signal=interrupt_signal)
    assert result.returncode == expected_code
    assert len(deletions(calls)) == 1
    assert len(state["locks"]) == 4
    assert "INTERRUPTED" in result.stdout + result.stderr
    assert "All planned removals verified" not in result.stdout
    assert not any(item.is_dir() for item in tmp_path.iterdir())


def test_verification_failure_reports_unknown_outcome(cli):
    result, calls, _ = cli("--apply", confirmation="yes\n", verify_error=True)
    assert result.returncode == 1
    assert len(deletions(calls)) == 4
    assert "UNVERIFIED" in result.stdout + result.stderr
    assert "Removed: 4" not in result.stdout


@pytest.mark.parametrize("interpreter", [None, "/bin/bash"])
def test_case_insensitive_scope_and_multiple_locks(cli, interpreter):
    items = [lock(RESOURCES[0].upper(), "first"), lock(RESOURCES[0], "second")]
    result, calls, _ = cli(
        "--apply",
        confirmation="yes\n",
        locks=items,
        interpreter=interpreter,
    )
    assert result.returncode == 0, result.stderr
    assert set(deletions(calls)) == {item["id"] for item in items}
    assert "Removed: 2" in result.stdout


def test_second_apply_does_not_delete_again(cli):
    first, calls, _ = cli("--apply", confirmation="yes\n")
    assert first.returncode == 0, first.stderr
    assert len(deletions(calls)) == 4
    second, calls, state = cli("--apply")
    assert second.returncode == 0, second.stderr
    assert len(deletions(calls)) == 4
    assert state["locks"] == []
    assert "Absent at start (resources): 4" in second.stdout


def test_help_does_not_contact_azure(cli):
    result, calls, _ = cli("--help")
    assert result.returncode == 0
    assert not calls
    assert "--apply" in result.stdout
    assert "--dry-run" in result.stdout
    assert "yes/no" in result.stdout
    assert "./prod-sec-remove-security-locks.sh" in result.stdout
    assert f"PROD-SEC ({SUBSCRIPTION})" in result.stdout


@pytest.mark.parametrize("arguments", [("--yes",), ("--apply", "--dry-run")])
def test_invalid_or_conflicting_options_never_contact_azure(cli, arguments):
    result, calls, _ = cli(*arguments)
    assert result.returncode == 2
    assert not calls
