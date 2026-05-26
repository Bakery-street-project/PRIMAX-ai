"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: enhanced_project_scanner.py                                           ║
║  Generated: 2025-12-26T10:00:42.044610                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

#!/usr/bin/env python3
# ==============================================================================
# PRIMSX CODEX - ENHANCED_PROJECT_SCANNER.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

import os
import glob
import json


def scan_project_potential(base_path="."):
    """Scan folders for unfinished projects and recognize potential"""
    results = {}

    for root, dirs, files in os.walk(base_path):
        if any(
            x in files
            for x in ["go.mod", "package.json", "requirements.txt", "Cargo.toml"]
        ):
            lang = None
            if "go.mod" in files:
                lang = "go"
            elif "package.json" in files:
                lang = "javascript"
            elif "requirements.txt" in files:
                lang = "python"
            elif "Cargo.toml" in files:
                lang = "rust"

            results[root] = {
                "language": lang,
                "files": len(files),
                "potential": "high" if len(files) > 5 else "medium",
                "deployable": "Dockerfile" in files or "main.tf" in files,
            }

    return results


if __name__ == "__main__":
    projects = scan_project_potential(".")
    print(json.dumps(projects, indent=2))

    print("\n=== Deployment Recommendations ===")
    for path, info in projects.items():
        if info["deployable"]:
            print(f"✓ {path}: Ready to deploy with Terraform!")
        else:
            print(f"⚠ {path}: Add Dockerfile or main.tf for auto-deploy")
