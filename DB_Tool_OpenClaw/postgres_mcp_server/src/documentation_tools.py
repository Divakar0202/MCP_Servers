"""Tools for searching and reading external documentation files."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from utils import MCPToolError, ensure_file_in_directory, success_response


class DocumentationService:
    def __init__(self, documentation_path: str):
        self.docs_dir = Path(documentation_path)

    def validate_docs_dir(self) -> None:
        if not self.docs_dir.exists() or not self.docs_dir.is_dir():
            raise MCPToolError(
                code="documentation_directory_missing",
                message=f"Documentation directory does not exist: {self.docs_dir}",
            )

    def _iter_docs(self):
        for path in self.docs_dir.glob("**/*"):
            if path.is_file() and path.suffix.lower() in {".md", ".txt", ".rst"}:
                yield path

    def search_documentation(self, keyword: str) -> Dict:
        keyword = (keyword or "").strip()
        if not keyword:
            raise MCPToolError(code="invalid_keyword", message="keyword cannot be empty.")

        hits: List[Dict] = []
        low_keyword = keyword.lower()
        for file_path in self._iter_docs():
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            matched_sections = []
            for idx, line in enumerate(lines, start=1):
                if low_keyword in line.lower():
                    start = max(1, idx - 2)
                    end = min(len(lines), idx + 2)
                    snippet = "\n".join(lines[start - 1 : end])
                    matched_sections.append(
                        {
                            "line": idx,
                            "snippet": snippet,
                        }
                    )
            if matched_sections:
                hits.append(
                    {
                        "file_name": file_path.name,
                        "relative_path": str(file_path.relative_to(self.docs_dir)),
                        "matches": matched_sections,
                    }
                )

        return success_response({"keyword": keyword, "results": hits})

    def read_documentation_file(self, file_name: str) -> Dict:
        if not file_name or file_name.strip() == "":
            raise MCPToolError(code="invalid_file_name", message="file_name cannot be empty.")

        safe_file = ensure_file_in_directory(self.docs_dir / file_name, self.docs_dir)
        if not safe_file.exists() or not safe_file.is_file():
            raise MCPToolError(
                code="documentation_file_missing",
                message=f"Documentation file not found: {file_name}",
            )

        content = safe_file.read_text(encoding="utf-8", errors="ignore")
        return success_response(
            {
                "file_name": file_name,
                "relative_path": str(safe_file.relative_to(self.docs_dir.resolve())),
                "content": content,
            }
        )
