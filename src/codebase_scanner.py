"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRIMAX AI - Codebase Scanner                               ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: PRIMAX-AI-SCANNER-BSP-2025                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
import json


@dataclass
class CodeFile:
    path: str
    language: str
    lines: int
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    complexity: int = 0
    hash: str = ""


@dataclass
class ScanResult:
    files: List[CodeFile] = field(default_factory=list)
    total_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    languages: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    dependencies: Dict[str, List[str]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def to_json(self) -> str:
        return json.dumps(
            {
                "files": [
                    {
                        "path": f.path,
                        "language": f.language,
                        "lines": f.lines,
                        "functions": f.functions,
                        "classes": f.classes,
                        "imports": f.imports,
                        "complexity": f.complexity,
                        "hash": f.hash,
                    }
                    for f in self.files
                ],
                "summary": {
                    "total_lines": self.total_lines,
                    "total_functions": self.total_functions,
                    "total_classes": self.total_classes,
                    "languages": dict(self.languages),
                },
            },
            indent=2,
        )


class CodebaseScanner:
    def __init__(self, root_path: str = "."):
        self.root = Path(root_path).resolve()
        self.result = ScanResult()

    def scan(self, recursive: bool = True, extensions: Optional[List[str]] = None) -> ScanResult:
        if extensions is None:
            extensions = [
                ".py",
                ".js",
                ".ts",
                ".go",
                ".rs",
                ".java",
                ".cpp",
                ".c",
                ".md",
            ]

        extensions = [e if e.startswith(".") else f".{e}" for e in extensions]

        for file_path in self._get_files(extensions):
            self._analyze_file(file_path)

        return self.result

    def _get_files(self, extensions: List[str]) -> List[Path]:
        if self.root.is_file():
            return [self.root] if self.root.suffix in extensions else []

        files = []
        for ext in extensions:
            files.extend(self.root.rglob(f"*{ext}"))
        return sorted(files)

    def _analyze_file(self, file_path: Path) -> None:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return

        lines = content.split("\n")
        language = self._detect_language(file_path)
        file_hash = hashlib.md5(content.encode()).hexdigest()

        code_file = CodeFile(
            path=str(file_path.relative_to(self.root)),
            language=language,
            lines=len(lines),
            hash=file_hash,
        )

        if language == "python":
            self._analyze_python_file(content, file_path, code_file)
        elif language == "javascript":
            self._analyze_javascript_file(content, file_path, code_file)
        elif language == "go":
            self._analyze_go_file(content, file_path, code_file)

        self.result.files.append(code_file)
        self.result.total_lines += code_file.lines
        self.result.total_functions += len(code_file.functions)
        self.result.total_classes += len(code_file.classes)
        self.result.languages[language] += 1

    def _detect_language(self, file_path: Path) -> str:
        suffix_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
        }
        return suffix_map.get(file_path.suffix.lower(), "unknown")

    def _analyze_python_file(
        self, content: str, file_path: Path, code_file: CodeFile
    ) -> None:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                code_file.functions.append(node.name)
                code_file.complexity += 1
            elif isinstance(node, ast.AsyncFunctionDef):
                code_file.functions.append(node.name)
                code_file.complexity += 1
            elif isinstance(node, ast.ClassDef):
                code_file.classes.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    code_file.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    code_file.imports.append(node.module)

    def _analyze_javascript_file(
        self, content: str, file_path: Path, code_file: CodeFile
    ) -> None:
        func_pattern = r"(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\(|(\w+)\s*:\s*(?:async\s*)?\()"
        for match in __import__("re").finditer(func_pattern, content):
            func_name = match.group(1) or match.group(2) or match.group(3)
            if func_name:
                code_file.functions.append(func_name)

    def _analyze_go_file(
        self, content: str, file_path: Path, code_file: CodeFile
    ) -> None:
        func_pattern = r"func(?:s\s+\w+)?\s+(\w+)\s*\("
        for match in __import__("re").finditer(func_pattern, content):
            code_file.functions.append(match.group(1))

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        return dict(self.result.dependencies)

    def to_json(self) -> str:
        return json.dumps(
            {
                "files": [
                    {
                        "path": f.path,
                        "language": f.language,
                        "lines": f.lines,
                        "functions": f.functions,
                        "classes": f.classes,
                        "imports": f.imports,
                        "complexity": f.complexity,
                        "hash": f.hash,
                    }
                    for f in self.result.files
                ],
                "summary": {
                    "total_lines": self.result.total_lines,
                    "total_functions": self.result.total_functions,
                    "total_classes": self.result.total_classes,
                    "languages": dict(self.result.languages),
                },
            },
            indent=2,
        )


def scan_repository(path: str = ".") -> ScanResult:
    scanner = CodebaseScanner(path)
    return scanner.scan()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PRIMAX Codebase Scanner")
    parser.add_argument("path", nargs="?", default=".", help="Path to scan")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = scan_repository(args.path)

    if args.json:
        print(result.to_json())
    else:
        print("=== PRIMAX Codebase Scan ===")
        print(f"Files: {len(result.files)}")
        print(f"Lines: {result.total_lines}")
        print(f"Functions: {result.total_functions}")
        print(f"Classes: {result.total_classes}")
        print(f"Languages: {dict(result.languages)}")
