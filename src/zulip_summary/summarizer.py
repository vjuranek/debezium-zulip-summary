"""Core summarization logic using LangChain."""

from typing import Optional, List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import SummaryConfig
from .file_handler import read_file, get_file_info

console = Console()

# Prompt templates for summarization
STUFF_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant that creates concise summaries of text."),
    ("user",
     "Please provide a concise summary of the following text:\n\n{text}\n\nSummary:")
])

MAP_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a consultant or customer support specialist, helping users to setup and debug Debezium, CDC platform."),
    ("user",
     "Please provide best practises guidelines for the Debezium customers using Postgres connector based the following text chunk:\n\n{text}\n\nSummary:")
])

REDUCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a consultant or customer support specialist, helping users to setup and debug Debezium, CDC platform."),
    ("user",
     "Please combine the following guidelines into a single cohesive guideline and troubleshooting guide:\n\n{text}\n\nFinal Summary:")
])


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

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )
    texts = text_splitter.split_text(text)

    if config.verbose:
        console.print(f"[cyan]Split into {len(texts)} chunk(s)[/cyan]")

    # Run summarization with progress indicator
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
    ) as progress:
        try:
            if strategy == "stuff":
                task = progress.add_task("Summarizing...", total=None)
                summary = _summarize_stuff(texts, llm, config)
            else:
                task = progress.add_task(
                    f"Summarizing chunks (0/{len(texts)})...", total=None)
                summary = _summarize_map_reduce(texts, llm, config, progress,
                                                task)
        finally:
            progress.stop()

    return summary.strip()


def _summarize_stuff(chunks: List[str], llm: Ollama,
                     config: SummaryConfig) -> str:
    """Summarize text using stuff strategy - combine all chunks and summarize at once."""
    # Combine all chunks into single text
    combined_text = "\n\n".join(chunks)

    # Create chain with prompt template
    chain = STUFF_PROMPT | llm

    # Invoke chain
    summary = chain.invoke({"text": combined_text})

    return summary


def _summarize_map_reduce(
        chunks: List[str],
        llm: Ollama,
        config: SummaryConfig,
        progress: Optional[Progress] = None,
        task_id=None
) -> str:
    """Summarize text using map-reduce strategy - summarize each chunk, then combine."""
    # Map phase: Summarize each chunk
    chunk_summaries = []
    map_chain = MAP_PROMPT | llm

    for i, chunk in enumerate(chunks):
        if progress and task_id:
            progress.update(task_id,
                            description=f"Summarizing chunks ({i + 1}/{len(chunks)})...")

        summary = map_chain.invoke({"text": chunk})
        chunk_summaries.append(summary)

    # Reduce phase: Combine summaries
    if progress and task_id:
        progress.update(task_id, description="Combining summaries...")

    combined_summaries = "\n\n".join(chunk_summaries)
    reduce_chain = REDUCE_PROMPT | llm
    final_summary = reduce_chain.invoke({"text": combined_summaries})

    return final_summary


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
        "compression_ratio": round(len(text) / len(summary), 2) if len(
            summary) > 0 else 0,
    }


def summarize_merged_files(file_paths: List[str], llm: Ollama,
                           config: SummaryConfig) -> dict:
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
            console.print(
                f"[dim]Reading: {file_info['name']} ({file_info['size_kb']} KB)[/dim]")

        try:
            text = read_file(file_path)
            # Add file separator with filename for context
            merged_text_parts.append(
                f"=== Content from {file_info['name']} ===\n{text}")
        except Exception as e:
            console.print(
                f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
            continue

    if not merged_text_parts:
        raise ValueError("No files could be read successfully")

    # Merge all text with separators
    merged_text = "\n\n".join(merged_text_parts)

    if config.verbose:
        console.print(
            f"[cyan]Total merged size: {len(merged_text)} characters[/cyan]")

    # Summarize merged content
    summary = summarize_text(merged_text, llm, config)

    return {
        "files": files_info,
        "file_count": len(files_info),
        "total_size_kb": round(total_size / 1024, 2),
        "summary": summary,
        "original_length": len(merged_text),
        "summary_length": len(summary),
        "compression_ratio": round(len(merged_text) / len(summary), 2) if len(
            summary) > 0 else 0,
    }
