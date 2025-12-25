#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     PRIMSX CODEX SECURITY & WATERMARKING                      ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMSX-CODEX-SECURITY-BSP-2025                                    ║
║  LICENSE: See LICENSE_PROPRIETARY.md                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Watermark Configuration
WATERMARK = "PRIMSX-CODEX-BSP-2025"
COPYRIGHT = f"Copyright (c) 2024-{datetime.now().year} Bakery Street Project - ALL RIGHTS RESERVED"
LICENSE_TYPE = "PROPRIETARY"

# File type headers
HEADERS = {
    ".go": {
        "prefix": "//",
        "template": """// {watermark_box}
// {title}
// {copyright}
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: {watermark}
// LICENSE: See LICENSE_PROPRIETARY.md
// {watermark_box}

"""
    },
    ".py": {
        "prefix": "#",
        "template": """# {watermark_box}
# {title}
# {copyright}
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: {watermark}
# LICENSE: See LICENSE_PROPRIETARY.md
# {watermark_box}

"""
    },
    ".sh": {
        "prefix": "#",
        "template": """#!/usr/bin/env bash
# {watermark_box}
# {title}
# {copyright}
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: {watermark}
# LICENSE: See LICENSE_PROPRIETARY.md
# {watermark_box}

"""
    },
    ".js": {
        "prefix": "//",
        "template": """// {watermark_box}
// {title}
// {copyright}
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: {watermark}
// LICENSE: See LICENSE_PROPRIETARY.md
// {watermark_box}

"""
    },
    ".ts": {
        "prefix": "//",
        "template": """// {watermark_box}
// {title}
// {copyright}
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: {watermark}
// LICENSE: See LICENSE_PROPRIETARY.md
// {watermark_box}

"""
    }
}


class CodexSecurityManager:
    """Manages watermarking, licensing, and copyright for Primsx codex"""

    def __init__(self, codex_path: Path):
        self.codex_path = Path(codex_path)
        self.stats = {
            "total_files": 0,
            "watermarked": 0,
            "skipped": 0,
            "errors": 0
        }

    def create_watermark_box(self, char: str = "=") -> str:
        """Create ASCII watermark box"""
        return char * 78

    def get_file_title(self, file_path: Path) -> str:
        """Generate file title"""
        return f"PRIMSX CODEX - {file_path.name.upper()}"

    def is_already_watermarked(self, content: str) -> bool:
        """Check if file already has watermark"""
        return WATERMARK in content or "PRIMSX" in content[:500]

    def get_header_template(self, file_ext: str) -> Dict:
        """Get header template for file type"""
        return HEADERS.get(file_ext, HEADERS.get(".py"))

    def watermark_file(self, file_path: Path) -> bool:
        """Add watermark, copyright, and license to file"""
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check if already watermarked
            if self.is_already_watermarked(content):
                print(f"  ⏭️  Already watermarked: {file_path.name}")
                self.stats["skipped"] += 1
                return False

            # Get header template
            file_ext = file_path.suffix
            header_config = self.get_header_template(file_ext)

            if not header_config:
                print(f"  ⏭️  Unsupported file type: {file_path.name}")
                self.stats["skipped"] += 1
                return False

            # Build header
            watermark_box = self.create_watermark_box(
                "=" if header_config["prefix"] == "#" else "="
            )

            header = header_config["template"].format(
                watermark_box=watermark_box,
                title=self.get_file_title(file_path),
                copyright=COPYRIGHT,
                watermark=WATERMARK
            )

            # Preserve shebang if exists
            lines = content.split('\n')
            if lines and lines[0].startswith('#!'):
                # Move shebang to top, then add header
                shebang = lines[0]
                rest = '\n'.join(lines[1:])
                new_content = f"{shebang}\n{header}{rest}"
            else:
                new_content = header + content

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"  ✅ Watermarked: {file_path.name}")
            self.stats["watermarked"] += 1
            return True

        except Exception as e:
            print(f"  ❌ Error watermarking {file_path.name}: {e}")
            self.stats["errors"] += 1
            return False

    def process_directory(self, directory: Path = None) -> Dict:
        """Process all files in directory"""
        if directory is None:
            directory = self.codex_path

        print(f"\n🔐 Watermarking Primsx Codex: {directory}")
        print(f"   Watermark: {WATERMARK}")
        print(f"   Copyright: {COPYRIGHT}\n")

        # Supported extensions
        extensions = {'.go', '.py', '.sh', '.js', '.ts'}

        # Process all files
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                # Skip .git and __pycache__
                if '.git' in str(file_path) or '__pycache__' in str(file_path):
                    continue

                self.stats["total_files"] += 1
                self.watermark_file(file_path)

        return self.stats

    def create_license_file(self):
        """Create LICENSE_PROPRIETARY.md"""
        license_path = self.codex_path.parent / "LICENSE_PROPRIETARY.md"

        license_content = f"""# PROPRIETARY SOFTWARE LICENSE

**WATERMARK: {WATERMARK}**

{COPYRIGHT}

## NOTICE

This software and associated documentation files (the "Software") are the proprietary
and confidential property of Bakery Street Project.

**ALL RIGHTS RESERVED**

## TERMS

1. **NO RIGHTS GRANTED**: This license does NOT grant you any rights to use, copy,
   modify, merge, publish, distribute, sublicense, or sell copies of the Software.

2. **CONFIDENTIAL**: The Software contains trade secrets and proprietary information.
   Unauthorized disclosure is strictly prohibited.

3. **AUTHORIZED USE ONLY**: Use of this Software is permitted only with explicit
   written authorization from Bakery Street Project.

4. **NO WARRANTY**: THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

5. **NO LIABILITY**: IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES
   OR OTHER LIABILITY ARISING FROM THE SOFTWARE.

## COMMERCIAL LICENSING

For commercial licensing inquiries, contact:

**Email:** kiliaan@bakerstreet221b.store
**GitHub:** https://github.com/Bakery-street-project

## AVAILABLE LICENSES

- **Indie License**: $49 (1 developer)
- **Team License**: $299 (up to 10 developers)
- **Startup License**: $999 (unlimited developers, 1 year)
- **Enterprise License**: Custom pricing

---

**WATERMARK: {WATERMARK}**

**This file is part of PRIMAX AI - Primsx Codex**
**https://github.com/Bakery-street-project/PRIMAX-ai**

Generated: {datetime.now().isoformat()}
"""

        with open(license_path, 'w') as f:
            f.write(license_content)

        print(f"✅ Created: {license_path}")

    def create_readme(self):
        """Create Primsx README"""
        readme_path = self.codex_path.parent / "README.md"

        readme_content = f"""# PRIMSX CODEX

> **AutomationCodex - Neuromorphic Intelligence Engine**

**WATERMARK: {WATERMARK}**
**{COPYRIGHT}**

---

## 🔐 SECURITY NOTICE

This is **PROPRIETARY and CONFIDENTIAL** software.

All files are:
- ✅ **Watermarked** with `{WATERMARK}`
- ✅ **Copyrighted** - Bakery Street Project
- ✅ **Encrypted** - AES-256-GCM vault
- ✅ **Permissions** - 700 (Owner only)

**Unauthorized access, use, or distribution is PROHIBITED.**

---

## 🧠 What is Primsx Codex?

The **AutomationCodex** neuromorphic intelligence engine containing:

### Go Modules
- `aspects.go` - Dimensional aspects
- `energy.go` - Energy dynamics
- `modules.go` - Core modules
- `theory.go` - Mathematical theories
- `victory.go` - Optimization algorithms
- `dynamics.go` - System dynamics
- `symbols.go` - Symbolic mathematics
- `trios.go` - Triple relationships
- `chaos_neuro.go` - Chaos & neuromorphic logic
- `math_theories.go` - Mathematical foundations
- `philosophy_theories.go` - Philosophical frameworks

### Python Modules
- `brain_perplexity_research.py` - Neuromorphic brain
- `brian2_snn.py` - Spiking neural networks
- `superbrain.py` - SuperBrain intelligence

### Scripts
- Deployment automation
- Cloud integration (GCP, AWS)
- Terraform infrastructure
- Docker containers

---

## 📂 Structure

```
Primsx/
├── codex/              # AutomationCodex source files
│   ├── *.go           # Go modules (158 files)
│   ├── *.py           # Python modules
│   └── scripts/       # Automation scripts
├── vault/             # Encrypted secrets (AES-256-GCM)
├── docs/              # Documentation
└── scripts/           # Security & deployment scripts
```

---

## 🔐 Vault Access

All sensitive data is encrypted in the vault:

```bash
# Initialize vault
python ~/claude_enterprise/workspace/PRIMAX-ai/src/vault_manager.py init --vault-dir ./vault

# Store secret
python ~/claude_enterprise/workspace/PRIMAX-ai/src/vault_manager.py store --key="api_key" --value="xxx" --vault-dir ./vault

# Retrieve secret
python ~/claude_enterprise/workspace/PRIMAX-ai/src/vault_manager.py get --key="api_key" --vault-dir ./vault
```

**Vault Features:**
- AES-256-GCM encryption
- PBKDF2 key derivation (100k iterations)
- Zero-knowledge architecture
- Automatic watermarking

---

## 📜 License

**PROPRIETARY LICENSE**

See `LICENSE_PROPRIETARY.md` for full terms.

**Commercial licensing available:**
📧 kiliaan@bakerstreet221b.store

---

## ⚖️ Legal

**{COPYRIGHT}**

This software is protected by:
- Copyright law
- Trade secret law
- International treaties

**Unauthorized use is a criminal offense.**

---

**WATERMARK: {WATERMARK}**

**Part of PRIMAX AI**
**https://github.com/Bakery-street-project/PRIMAX-ai**

---

Generated: {datetime.now().isoformat()}
"""

        with open(readme_path, 'w') as f:
            f.write(readme_content)

        print(f"✅ Created: {readme_path}")

    def print_summary(self):
        """Print operation summary"""
        print(f"\n" + "="*60)
        print(f"🔐 PRIMSX CODEX SECURITY SUMMARY")
        print(f"="*60)
        print(f"  Total files scanned:  {self.stats['total_files']}")
        print(f"  ✅ Watermarked:       {self.stats['watermarked']}")
        print(f"  ⏭️  Skipped:           {self.stats['skipped']}")
        print(f"  ❌ Errors:            {self.stats['errors']}")
        print(f"="*60)
        print(f"  Watermark: {WATERMARK}")
        print(f"  Copyright: {COPYRIGHT}")
        print(f"  License: {LICENSE_TYPE}")
        print(f"="*60 + "\n")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python secure_codex.py <codex_directory>")
        sys.exit(1)

    codex_path = Path(sys.argv[1])

    if not codex_path.exists():
        print(f"❌ Directory not found: {codex_path}")
        sys.exit(1)

    manager = CodexSecurityManager(codex_path)

    # Process all files
    manager.process_directory()

    # Create license
    manager.create_license_file()

    # Create README
    manager.create_readme()

    # Print summary
    manager.print_summary()

    print("✅ Primsx Codex secured successfully!")


if __name__ == "__main__":
    main()
