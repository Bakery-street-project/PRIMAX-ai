#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        PRIMAX AI - WATERMARK SYSTEM                           ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-WATERMARK-BSP-2025                                      ║
║  LICENSE: See LICENSE_PROPRIETARY.md                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import hashlib
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional


class PrimaxWatermark:
    """
    Code watermarking and licensing system for PRIMAX AI

    Ensures all generated code is properly attributed and licensed
    """

    WATERMARK_ID = "PRIMAX-AI-BSP-2025"
    COPYRIGHT = "Copyright © 2024-2025 Bakery Street Project"

    HEADER_TEMPLATE = '''"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              {title:^60}                              ║
║                                                                               ║
║  {copyright:^76}║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: {watermark:^64}║
║  LICENSE: See LICENSE_PROPRIETARY.md                                          ║
║  GENERATED: {timestamp:^64}║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
'''

    @classmethod
    def generate_header(cls, title: str = "PRIMAX AI Component") -> str:
        """Generate watermarked header for source files"""
        return cls.HEADER_TEMPLATE.format(
            title=title.upper(),
            copyright=cls.COPYRIGHT,
            watermark=cls.WATERMARK_ID,
            timestamp=datetime.now().isoformat()
        )

    @classmethod
    def generate_file_hash(cls, content: str) -> str:
        """Generate unique hash for file content"""
        hash_obj = hashlib.sha256(content.encode())
        return base64.b64encode(hash_obj.digest()).decode()[:16]

    @classmethod
    def watermark_file(cls, filepath: Path, title: Optional[str] = None):
        """Add watermark to existing file"""
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return

        content = filepath.read_text()

        # Skip if already watermarked
        if cls.WATERMARK_ID in content:
            print(f"⏭️  Already watermarked: {filepath.name}")
            return

        # Generate header
        if not title:
            title = filepath.stem.replace('_', ' ').title()

        header = cls.generate_header(title)

        # Add shebang if Python file
        if filepath.suffix == '.py':
            if content.startswith('#!'):
                lines = content.split('\n', 1)
                content = f"{lines[0]}\n{header}\n{lines[1] if len(lines) > 1 else ''}"
            else:
                content = f"#!/usr/bin/env python3\n{header}\n{content}"
        else:
            content = f"{header}\n{content}"

        # Write back
        filepath.write_text(content)
        print(f"✅ Watermarked: {filepath.name}")

    @classmethod
    def watermark_directory(cls, directory: Path, recursive: bool = True):
        """Watermark all files in directory"""
        print(f"🔖 Watermarking files in {directory}")

        pattern = "**/*" if recursive else "*"

        for filepath in directory.glob(pattern):
            if not filepath.is_file():
                continue

            # Only watermark source files
            if filepath.suffix in ['.py', '.js', '.ts', '.c', '.h', '.cpp']:
                cls.watermark_file(filepath)

    @classmethod
    def verify_watermark(cls, filepath: Path) -> bool:
        """Verify file has valid watermark"""
        if not filepath.exists():
            return False

        content = filepath.read_text()
        return cls.WATERMARK_ID in content


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="PRIMAX AI Watermark System")
    parser.add_argument("command", choices=["add", "verify", "batch"])
    parser.add_argument("path", help="File or directory path")
    parser.add_argument("--title", help="Custom title for header")
    parser.add_argument("--recursive", action="store_true", help="Process directories recursively")

    args = parser.parse_args()

    path = Path(args.path)

    if args.command == "add":
        if path.is_file():
            PrimaxWatermark.watermark_file(path, args.title)
        else:
            PrimaxWatermark.watermark_directory(path, args.recursive)

    elif args.command == "verify":
        if PrimaxWatermark.verify_watermark(path):
            print(f"✅ Valid watermark: {path.name}")
        else:
            print(f"❌ No watermark: {path.name}")

    elif args.command == "batch":
        if not path.is_dir():
            print("❌ Path must be a directory")
            return
        PrimaxWatermark.watermark_directory(path, args.recursive)


if __name__ == "__main__":
    main()
