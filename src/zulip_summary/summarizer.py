"""Core summarization logic using LangChain."""

from typing import Optional, List
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import SummaryConfig
from .file_handler import read_file, get_file_info

console = Console()


def determine_strategy(text_length: int, chunk_size: int = 4000) -> str:
    """Determine the best summarization strategy based on text length."""
    if text_length < chunk_size:
        return "stuff"
    else:
        return "map_reduce"


def summarize_text(text: str, llm: Ollama, config: SummaryConfig) -> str:
    """Summarize text using appropriate LangChain strategy."""
    strategy = determine_strategy(len(text), config.chunk_size)

    if config.verbose:
        console.print(f"[cyan]Using summarization strategy:[/cyan] {strategy}")

    # Split text into documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )
    texts = text_splitter.split_text(text)
    docs = [Document(page_content=t) for t in texts]

    if config.verbose:
        console.print(f"[cyan]Split into {len(docs)} chunk(s)[/cyan]")

    # Load appropriate chain
    chain = load_summarize_chain(llm, chain_type=strategy, verbose=config.verbose)

    # Run summarization with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Summarizing...", total=None)
        try:
            if strategy == "stuff":
                summary = chain.run(docs)
            else:
                summary = chain.run(docs)
        finally:
            progress.stop()

    return summary.strip()


def summarize_file(file_path: str, llm: Ollama, config: SummaryConfig) -> dict:
    """Summarize a file and return result with metadata."""
    file_info = get_file_info(file_path)

    if config.verbose:
        console.print(f"\n[bold]Processing:[/bold] {file_info['name']}")
        console.print(f"[dim]Size: {file_info['size_kb']} KB[/dim]")

    # Read file
    text = read_file(file_path)

    # Summarize
    summary = summarize_text(text, llm, config)

    return {
        "file": file_info,
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
        "compression_ratio": round(len(text) / len(summary), 2) if len(summary) > 0 else 0,
    }


def summarize_merged_files(file_paths: List[str], llm: Ollama, config: SummaryConfig) -> dict:
    """Merge multiple files and return a single combined summary with metadata."""
    files_info = []
    merged_text_parts = []
    total_size = 0

    if config.verbose:
        console.print(f"\n[bold]Processing {len(file_paths)} file(s)[/bold]")

    # Read and merge all files
    for file_path in file_paths:
        file_info = get_file_info(file_path)
        files_info.append(file_info)
        total_size += file_info['size']

        if config.verbose:
            console.print(f"[dim]Reading: {file_info['name']} ({file_info['size_kb']} KB)[/dim]")

        try:
            text = read_file(file_path)
            # Add file separator with filename for context
            merged_text_parts.append(f"=== Content from {file_info['name']} ===\n{text}")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
            continue

    if not merged_text_parts:
        raise ValueError("No files could be read successfully")

    # Merge all text with separators
    merged_text = "\n\n".join(merged_text_parts)

    if config.verbose:
        console.print(f"[cyan]Total merged size: {len(merged_text)} characters[/cyan]")

    # Summarize merged content
    summary = summarize_text(merged_text, llm, config)

    return {
        "files": files_info,
        "file_count": len(files_info),
        "total_size_kb": round(total_size / 1024, 2),
        "summary": summary,
        "original_length": len(merged_text),
        "summary_length": len(summary),
        "compression_ratio": round(len(merged_text) / len(summary), 2) if len(summary) > 0 else 0,
    }
