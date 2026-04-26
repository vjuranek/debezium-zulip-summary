"""Configuration management for zulip-summary."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SummaryConfig:
    """Configuration for text summarization."""

    ollama_base_url: str = "http://localhost:11434"
    model_name: str = "llama2"
    temperature: float = 0.3
    max_tokens: int = 500
    chunk_size: int = 4000
    chunk_overlap: int = 200
    verbose: bool = False

    @classmethod
    def from_args(
        cls,
        ollama_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        verbose: bool = False,
    ) -> "SummaryConfig":
        """Create config from CLI arguments with environment variable fallback."""
        return cls(
            ollama_base_url=ollama_url
            or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model_name=model or os.getenv("OLLAMA_MODEL", "llama2"),
            temperature=temperature
            if temperature is not None
            else float(os.getenv("SUMMARY_TEMPERATURE", "0.3")),
            max_tokens=max_tokens
            if max_tokens is not None
            else int(os.getenv("SUMMARY_MAX_TOKENS", "500")),
            chunk_size=int(os.getenv("SUMMARY_CHUNK_SIZE", "4000")),
            chunk_overlap=int(os.getenv("SUMMARY_CHUNK_OVERLAP", "200")),
            verbose=verbose,
        )
