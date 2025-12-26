#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   PRIMAX-AI WATERMARK & COPYRIGHT TOOL                        ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-WATERMARK-BSP-2025                                         ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
from pathlib import Path
from datetime import datetime

WATERMARK = "PRIMAX-AI-BSP-2025"
OWNER = "Kiliaan Vanvoorden (@BoozeLee)"
COPYRIGHT = "Copyright © 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED"

PYTHON_HEADER = '''"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: {watermark}                                            ║
║  Owner: {owner}                                      ║
║  File: {filename:<69} ║
║  Generated: {timestamp:<61} ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

'''

JS_HEADER = '''/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: {watermark}                                            ║
║  Owner: {owner}                                      ║
║  File: {filename:<69} ║
║  Generated: {timestamp:<61} ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

'''

MD_HEADER = '''<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY DOCUMENTATION                 ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: {watermark}                                            ║
║  Owner: {owner}                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
-->

'''

def has_watermark(content: str) -> bool:
    """Check if file already has watermark"""
    return WATERMARK in content or "PRIMAX-AI-BSP" in content

def add_watermark_to_file(file_path: Path):
    """Add watermark and copyright to file"""

    # Skip if file is in excluded directories
    excluded = ['.git', 'node_modules', '__pycache__', '.vault', 'venv']
    if any(exc in str(file_path) for exc in excluded):
        return False

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False  # Skip binary files

    # Check if already watermarked
    if has_watermark(content):
        return False

    # Select header based on file type
    suffix = file_path.suffix.lower()
    header = None

    if suffix == '.py':
        header = PYTHON_HEADER
    elif suffix in ['.js', '.ts', '.jsx', '.tsx', '.go', '.c', '.cpp', '.h']:
        header = JS_HEADER
    elif suffix == '.md':
        header = MD_HEADER
    else:
        return False  # Skip unsupported file types

    # Format header
    formatted_header = header.format(
        watermark=WATERMARK,
        owner=OWNER,
        filename=file_path.name,
        timestamp=datetime.now().isoformat()
    )

    # Add header to content
    watermarked_content = formatted_header + content

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(watermarked_content)

    return True

def watermark_directory(directory: Path):
    """Watermark all files in directory"""
    print(f"🔏 Watermarking directory: {directory}")
    print(f"   Watermark: {WATERMARK}")
    print(f"   Owner: {OWNER}")
    print(f"   {COPYRIGHT}\n")

    watermarked = []
    skipped = []

    for file_path in directory.rglob('*'):
        if file_path.is_file():
            if add_watermark_to_file(file_path):
                watermarked.append(file_path)
                print(f"  ✓ Watermarked: {file_path.relative_to(directory)}")
            else:
                skipped.append(file_path)

    print(f"\n📊 Summary:")
    print(f"   ✓ Watermarked: {len(watermarked)} files")
    print(f"   ⊘ Skipped: {len(skipped)} files")
    print(f"\n🔒 All files now include:")
    print(f"   • Copyright notice")
    print(f"   • Watermark: {WATERMARK}")
    print(f"   • Owner: {OWNER}")
    print(f"   • Proprietary license")

def set_strict_permissions(directory: Path):
    """Set strict permissions (700) on all folders"""
    print(f"\n🔐 Setting strict permissions (700 - owner only)")

    count = 0
    for path in directory.rglob('*'):
        if path.is_dir():
            os.chmod(path, 0o700)
            count += 1

    # Set on root directory too
    os.chmod(directory, 0o700)
    count += 1

    print(f"  ✓ Set permissions on {count} directories")
    print(f"  ✓ Mode: 700 (drwx------) - Owner read/write/execute only")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python watermark_all.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])

    if not directory.exists():
        print(f"✗ Directory not found: {directory}")
        sys.exit(1)

    # Watermark all files
    watermark_directory(directory)

    # Set strict permissions
    set_strict_permissions(directory)

    print(f"\n✅ COMPLETE - Directory secured and watermarked!")
    print(f"   Location: {directory}")
    print(f"   Watermark: {WATERMARK}")
    print(f"   Permissions: 700 (owner only)")
