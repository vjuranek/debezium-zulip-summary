# Quick Start Guide

## Installation Complete! ✓

The LangChain text summarization tool is now installed and ready to use.

## Verified Configuration

- **Ollama Server**: Running at 127.0.0.1:11434
- **Available Models**: gemma3:4b, all-minilm:latest
- **Virtual Environment**: `.venv/` (activated)
- **Package**: Installed in development mode

## Basic Usage

### 1. Activate Virtual Environment (if not already active)

```bash
source .venv/bin/activate
```

### 2. Run a Simple Summarization

```bash
python -m zulip_summary -f examples/sample_input.txt -m gemma3:4b
```

### 3. Save Output to File

```bash
python -m zulip_summary -f examples/sample_input.txt -m gemma3:4b -o summary.txt
```

### 4. Verbose Mode (see details)

```bash
python -m zulip_summary -f examples/sample_input.txt -m gemma3:4b -v
```

### 5. Using the Installed Command

```bash
zulip-summary -f examples/sample_input.txt -m gemma3:4b
```

## Common Commands

```bash
# Get help
python -m zulip_summary --help

# Summarize multiple files
python -m zulip_summary -f file1.txt -f file2.txt -m gemma3:4b

# Use environment variables (create .env file first)
cp .env.example .env
# Edit .env with your settings
python -m zulip_summary -f document.txt
```

## Tested & Working ✓

- ✅ Ollama connection (127.0.0.1:11434)
- ✅ Model validation (gemma3:4b)
- ✅ File summarization
- ✅ Output to stdout
- ✅ Output to file
- ✅ Error handling (file not found)
- ✅ Verbose mode
- ✅ Compression ratio reporting

## Example Output

```
Summary:
Artificial intelligence, particularly through machine learning and deep 
learning, is rapidly transforming industries and capabilities. Large language 
models like GPT are showcasing impressive advancements in text understanding and
generation. While offering immense potential, AI development raises ethical 
concerns regarding bias, privacy, and employment, necessitating responsible 
development and deployment to ensure societal benefit.
```

## Next Steps

1. Try summarizing your own text files
2. Experiment with different models (if you have others installed)
3. Adjust temperature (-t) for different summary styles
4. Check the full README.md for advanced features

## Troubleshooting

If you encounter issues:

1. Ensure Ollama is running: `curl http://127.0.0.1:11434/api/tags`
2. List available models: `ollama list`
3. Pull a new model if needed: `ollama pull llama2`
4. Use `-v` flag for detailed error messages

Enjoy summarizing! 🚀
