---
name: script-python
description: Guide for creating or modifying Python scripts in this repository. Use when asked to implement complex scripts and include tests when required.
---

# Create Python Script

## Context

I need to create a Python script for complex operations in Azure governance (policies, remediation).

## Discovery

Use `#codebase` to search for existing Python scripts in `src/scripts/`.

## Input Required

- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}

## Mandatory Template

```python
#!/usr/bin/env python3
"""
📋 {script_name}.py

🎯 Purpose: {purpose}
📖 Usage: python src/scripts/{script_name}.py [options]
"""

import argparse
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main() -> int:
    logger.info("🚀 Starting script")
    # Early return pattern
    # ... implementation ...
    logger.info("✅ Completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Test Suite

Also create `src/scripts/tests/test_{script_name}.py` with pytest.

## References

Follow conventions in `#file:.github/copilot-instructions.md`
