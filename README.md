# Zulip Summary

A LangChain-based text summarization tool using local Ollama models.

## Features

- 📝 Summarize text files using local LLM models via Ollama
- 🚀 Support for multiple Ollama models (llama2, llama3, mistral, etc.)
- 📊 Automatic chunking for large documents with map-reduce strategy
- 🎨 Beautiful CLI with progress indicators
- ⚙️ Flexible configuration via CLI args or environment variables
- 📁 Batch processing of multiple files

## Prerequisites

- Python 3.9 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- At least one Ollama model pulled (e.g., `ollama pull llama2`)

## Installation

1. Clone or navigate to the project directory:
```bash
cd /home/vjuranek/debezium/zulip/zulip-summary
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Install the package:
```bash
pip install -e .
```

## Quick Start

### Ensure Ollama is running

```bash
# Check if Ollama is accessible
curl http://127.0.0.1:11434/api/tags

# If not running, start it
ollama serve
```

### Pull a model (if you haven't already)

```bash
ollama pull llama2
# or
ollama pull llama3
```

### Summarize a file

```bash
# Using the installed command
zulip-summary -f document.txt -m llama2

# Or using python -m
python -m zulip_summary -f document.txt -m llama2
```

## Usage

### Basic Usage

```bash
# Summarize a single file
zulip-summary -f document.txt

# Specify a model
zulip-summary -f document.txt -m llama3

# Save output to file
zulip-summary -f document.txt -o summary.txt
```

### Multiple Files

```bash
zulip-summary -f file1.txt -f file2.txt -f file3.txt -o summaries.txt
```

### Advanced Options

```bash
zulip-summary \
  --file document.txt \
  --model mistral \
  --temperature 0.5 \
  --max-tokens 1000 \
  --ollama-url http://127.0.0.1:11434 \
  --verbose
```

### Environment Variables

Create a `.env` file (see `.env.example`):

```bash
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3
SUMMARY_TEMPERATURE=0.3
SUMMARY_MAX_TOKENS=500
```

Then run without specifying options:

```bash
zulip-summary -f document.txt
```

## CLI Options

```
Options:
  -f, --file PATH         Input file(s) to summarize (required, multiple allowed)
  -m, --model TEXT        Ollama model name (default: llama2)
  --ollama-url TEXT       Ollama server URL (default: http://localhost:11434)
  -o, --output PATH       Output file path (default: stdout)
  -t, --temperature FLOAT LLM temperature 0.0-1.0 (default: 0.3)
  --max-tokens INTEGER    Maximum summary length (default: 500)
  -v, --verbose           Enable verbose output
  --help                  Show this message and exit
```

## How It Works

1. **Ollama Health Check**: Verifies the Ollama server is running
2. **Model Validation**: Checks if the specified model is available
3. **File Reading**: Reads text files with proper encoding detection
4. **Strategy Selection**: 
   - Short texts (< 4000 chars): Uses "stuff" strategy
   - Long texts: Uses "map_reduce" strategy with chunking
5. **Summarization**: Processes text through LangChain + Ollama
6. **Output**: Displays or saves the summary

## Examples

### Example 1: Simple Summarization

```bash
echo "This is a long document about artificial intelligence. It discusses various topics including machine learning, neural networks, and natural language processing. The field has seen tremendous growth in recent years..." > ai_doc.txt

zulip-summary -f ai_doc.txt -m llama2
```

### Example 2: Batch Processing

```bash
zulip-summary -f report1.txt -f report2.txt -f report3.txt -o all_summaries.txt -v
```

### Example 3: Different Model Settings

```bash
# More creative summaries (higher temperature)
zulip-summary -f story.txt -m llama3 -t 0.8

# More deterministic summaries (lower temperature)
zulip-summary -f technical_doc.txt -m mistral -t 0.1
```

## Troubleshooting

### Error: "Cannot connect to Ollama"

```bash
# Start Ollama
ollama serve

# Verify it's running
curl http://127.0.0.1:11434/api/tags
```

### Error: "Model not found"

```bash
# List available models
ollama list

# Pull the model you need
ollama pull llama2
```

### Large Files Processing Slowly

- This is normal for very large files
- The tool automatically uses map-reduce strategy
- Consider using a faster model or reducing chunk size

## Project Structure

```
zulip-summary/
├── src/zulip_summary/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point
│   ├── cli.py               # CLI interface
│   ├── config.py            # Configuration management
│   ├── ollama_client.py     # Ollama integration
│   ├── file_handler.py      # File utilities
│   └── summarizer.py        # Summarization logic
├── tests/                   # Test files
├── examples/                # Example files
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests (when implemented)
pytest tests/ -v

# Format code
black src/ tests/

# Lint
ruff check src/ tests/
```

## License

This project is provided as-is for personal and educational use.

## Contributing

This is a personal project, but suggestions and improvements are welcome.
