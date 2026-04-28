"""Command-line interface for zulip-summary."""

import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel

from .config import SummaryConfig
from .ollama_client import create_ollama_llm
from .summarizer import summarize_merged_files
from .file_handler import find_text_files

console = Console()


@click.command()
@click.option(
    "--file",
    "-f",
    "files",
    multiple=True,
    type=click.Path(exists=True),
    help="Input file(s) to summarize. Can be specified multiple times.",
)
@click.option(
    "--directory",
    "-d",
    "directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory containing files to summarize.",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Recursively search subdirectories when using --directory.",
)
@click.option(
    "--extensions",
    default=None,
    help="Comma-separated file extensions to include (e.g., '.txt,.md,.log'). Defaults to common text formats.",
)
@click.option(
    "--model",
    "-m",
    default=None,
    help="Ollama model name (default: llama2 or OLLAMA_MODEL env var)",
)
@click.option(
    "--ollama-url",
    default=None,
    help="Ollama server URL (default: http://localhost:11434 or OLLAMA_BASE_URL env var)",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(),
    help="Output file path. If not specified, prints to stdout.",
)
@click.option(
    "--temperature",
    "-t",
    default=None,
    type=float,
    help="LLM temperature 0.0-1.0 (default: 0.3)",
)
@click.option(
    "--max-tokens",
    default=None,
    type=int,
    help="Maximum summary length in tokens (default: 500)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def main(
        files: tuple,
        directory: Optional[str],
        recursive: bool,
        extensions: Optional[str],
        model: Optional[str],
        ollama_url: Optional[str],
        output: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        verbose: bool,
):
    """Summarize text files using LangChain and local Ollama models.

    Examples:

      # Summarize a single file
      zulip-summary -f document.txt -m llama2

      # Summarize multiple files
      zulip-summary -f file1.txt -f file2.txt -m llama3

      # Summarize all files in a directory
      zulip-summary -d /path/to/directory -m llama2

      # Recursively summarize files in directory
      zulip-summary -d /path/to/directory -r -m llama3

      # Specify file extensions
      zulip-summary -d /path/to/directory --extensions .txt,.md -m llama2

      # Save output to file
      zulip-summary -f document.txt -o summary.txt

      # Use different model and settings
      zulip-summary -f doc.txt -m mistral -t 0.5 --max-tokens 1000
    """
    try:
        # Validate input: must provide either files or directory
        if not files and not directory:
            console.print(
                "[red]Error:[/red] Must specify either --file/-f or --directory/-d")
            sys.exit(1)

        if files and directory:
            console.print(
                "[red]Error:[/red] Cannot specify both --file/-f and --directory/-d at the same time")
            sys.exit(1)

        # Collect all files to process
        files_to_process = []

        if directory:
            # Parse extensions if provided
            ext_set = None
            if extensions:
                ext_set = set(ext.strip() if ext.strip().startswith(
                    '.') else f'.{ext.strip()}'
                              for ext in extensions.split(','))

            if verbose:
                console.print(
                    f"[cyan]Searching for files in:[/cyan] {directory}")
                if recursive:
                    console.print("[cyan]Mode:[/cyan] Recursive")
                if ext_set:
                    console.print(
                        f"[cyan]Extensions:[/cyan] {', '.join(sorted(ext_set))}")

            try:
                files_to_process = find_text_files(directory,
                                                   recursive=recursive,
                                                   extensions=ext_set)
            except Exception as e:
                console.print(f"[red]Error accessing directory:[/red] {e}")
                sys.exit(1)

            if not files_to_process:
                console.print(
                    f"[yellow]No text files found in:[/yellow] {directory}")
                sys.exit(1)

            if verbose:
                console.print(
                    f"[green]Found {len(files_to_process)} file(s)[/green]")
        else:
            files_to_process = list(files)
        # Create configuration
        config = SummaryConfig.from_args(
            ollama_url=ollama_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            verbose=verbose,
        )

        if verbose:
            console.print(Panel.fit(
                f"[bold]Configuration[/bold]\n"
                f"Ollama URL: {config.ollama_base_url}\n"
                f"Model: {config.model_name}\n"
                f"Temperature: {config.temperature}\n"
                f"Max Tokens: {config.max_tokens}",
                border_style="blue"
            ))

        # Initialize Ollama LLM
        llm = create_ollama_llm(
            config.ollama_base_url,
            config.model_name,
            config.temperature,
            config.verbose,
        )

        # Process all files as a merged document
        try:
            result = summarize_merged_files([str(f) for f in files_to_process],
                                            llm, config)
        except Exception as e:
            console.print(f"[red]Error processing files:[/red] {e}")
            if verbose:
                import traceback
                console.print(traceback.format_exc())
            sys.exit(1)

        # Output result
        output_text = format_result(result, verbose)

        if output:
            # Write to file
            output_path = Path(output)
            output_path.write_text(output_text)
            console.print(f"\n[green]✓[/green] Summary saved to: {output}")
        else:
            # Print to stdout
            console.print("\n" + output_text)

        if verbose:
            console.print(
                f"\n[green]✓[/green] Successfully summarized {result['file_count']} file(s)")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


def format_result(result: dict, verbose: bool = False) -> str:
    """Format merged summarization result for output."""
    output_lines = []

    output_lines.append(f"{'=' * 80}")
    output_lines.append(f"Combined Summary of {result['file_count']} File(s)")
    output_lines.append(f"{'=' * 80}")
    output_lines.append("")

    if verbose:
        output_lines.append("Files processed:")
        for i, file_info in enumerate(result["files"], 1):
            output_lines.append(
                f"  {i}. {file_info['name']} ({file_info['size_kb']} KB)")
        output_lines.append("")
        output_lines.append(
            f"Total size: {result['total_size_kb']} KB"
        )
        output_lines.append(
            f"Compression: {result['original_length']} → "
            f"{result['summary_length']} chars "
            f"({result['compression_ratio']}x)"
        )
        output_lines.append("")

    output_lines.append("Summary:")
    output_lines.append(result["summary"])
    output_lines.append("")

    return "\n".join(output_lines)


if __name__ == "__main__":
    main()
