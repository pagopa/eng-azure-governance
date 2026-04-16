# Bash Anti-Patterns

Reference: `instructions/internal-bash.instructions.md`

## Critical
| ID | Anti-pattern | Why |
|---|---|---|
| SH-C01 | Hardcoded secrets, tokens, or passwords | Credential exposure risk |
| SH-C02 | `eval` on user-controlled input | Arbitrary command execution |
| SH-C03 | World-writable temp files without `mktemp` | Race condition / symlink attack |

## Major
| ID | Anti-pattern | Why |
|---|---|---|
| SH-M01 | Missing `set -euo pipefail` | Silent failures and undefined variables |
| SH-M02 | Unquoted variable expansion outside `[[ ]]` | Word splitting and globbing bugs |
| SH-M03 | `cd` without error handling (`cd dir \|\| exit 1`) | Silent directory change failure |
| SH-M04 | Missing `local` keyword for function variables | Pollutes global scope |
| SH-M05 | POSIX `#!/bin/sh` instead of `#!/usr/bin/env bash` | Repo mandates Bash |
| SH-M06 | Missing cleanup trap (`trap cleanup EXIT`) for temp files | Resource leak |
| SH-M07 | Function body longer than 30 lines | Complexity concern |

## Minor
| ID | Anti-pattern | Why |
|---|---|---|
| SH-m01 | `echo` for status messages instead of emoji logs (`ℹ️ ✅ ⚠️ ❌`) | Repo convention violation |
| SH-m02 | Hardcoded paths (e.g., `/usr/local/bin/tool`) | Portability concern |
| SH-m03 | Missing purpose header comment | Repo convention |
| SH-m04 | `grep \| awk` where a single `awk` suffices | Unnecessary pipe |
| SH-m05 | Missing `command -v` check before using external tools | Fails confusingly if tool missing |
| SH-m06 | Non-English log messages or comments | Language policy violation |

## Nit
| ID | Anti-pattern | Why |
|---|---|---|
| SH-N01 | `[ ... ]` instead of `[[ ... ]]` | Bash convention |
| SH-N02 | Backticks `` `cmd` `` instead of `$(cmd)` | Readability and nesting |
| SH-N03 | Missing blank line between function definitions | Visual structure |
| SH-N04 | Inconsistent indentation (mix of tabs and spaces) | Style consistency |
| SH-N05 | Missing trailing newline at end of file | POSIX convention |

## Good vs bad examples

```bash
# BAD (SH-M01, SH-M05): POSIX, no strict mode
#!/bin/sh
name=$1
cd /tmp
rm -rf $name

# GOOD: Bash, strict mode, safe patterns
#!/usr/bin/env bash
set -euo pipefail

local name="${1:?Missing required argument: name}"
cd /tmp || { echo "❌ Failed to cd /tmp"; exit 1; }
rm -rf "${name}"
```

```bash
# BAD (SH-M04): global variable in function
process_file() {
  result=$(cat "$1")
  count=${#result}
}

# GOOD: local variables
process_file() {
  local result
  local count
  result=$(cat "$1")
  count=${#result}
  echo "ℹ️ Processed ${count} bytes"
}
```
