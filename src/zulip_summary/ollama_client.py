"""Ollama client wrapper for health checks and LLM initialization."""

import requests
from typing import Optional
from langchain_community.llms import Ollama
from rich.console import Console

console = Console()


def check_ollama_health(base_url: str, timeout: int = 5) -> bool:
    """Check if Ollama server is running and accessible."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        raise ConnectionError(
            f"Cannot connect to Ollama at {base_url}.\n"
            f"Please ensure Ollama is running with: ollama serve\n"
            f"Error: {e}"
        )


def get_available_models(base_url: str) -> list[str]:
    """Get list of available models from Ollama."""
    try:
        response = requests.get(f"{base_url}/api/tags")
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except Exception:
        return []


def create_ollama_llm(
        base_url: str, model_name: str, temperature: float = 0.3,
        verbose: bool = False
) -> Ollama:
    """Create and configure Ollama LLM instance."""
    # Health check first
    check_ollama_health(base_url)

    # Check if model is available
    available_models = get_available_models(base_url)
    if available_models and model_name not in available_models:
        raise ValueError(
            f"Model '{model_name}' not found in Ollama.\n"
            f"Available models: {', '.join(available_models)}\n"
            f"Pull it with: ollama pull {model_name}\n"
            f"List all models: ollama list"
        )

    if verbose:
        console.print(f"[green]✓[/green] Connecting to Ollama at {base_url}")
        console.print(f"[green]✓[/green] Using model: {model_name}")

    return Ollama(
        base_url=base_url,
        model=model_name,
        temperature=temperature,
    )
