"""File handling utilities for reading and chunking text files."""

import os
from pathlib import Path
from typing import List
from rich.console import Console

console = Console()


def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """Read text file with proper error handling."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not os.access(path, os.R_OK):
        raise PermissionError(f"No read permission: {file_path}")

    try:
        with open(path, "r", encoding=encoding) as f:
            content = f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1 if UTF-8 fails
        with open(path, "r", encoding="latin-1") as f:
            content = f.read()

    if not content.strip():
        raise ValueError(f"File is empty or contains only whitespace: {file_path}")

    return content


def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for processing large documents."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        # Move start position with overlap
        start = end - overlap
        if start >= len(text):
            break

    return chunks


def get_file_info(file_path: str) -> dict:
    """Get file metadata."""
    path = Path(file_path)
    return {
        "path": str(path.absolute()),
        "name": path.name,
        "size": path.stat().st_size,
        "size_kb": round(path.stat().st_size / 1024, 2),
    }
