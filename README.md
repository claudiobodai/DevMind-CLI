<div align="center">

# DevMind CLI

<pre>
██████╗ ███████╗██╗   ██╗███╗   ███╗██╗███╗   ██╗██████╗      ██████╗██╗     ██╗
██╔══██╗██╔════╝██║   ██║████╗ ████║██║████╗  ██║██╔══██╗    ██╔════╝██║     ██║
██║  ██║█████╗  ██║   ██║██╔████╔██║██║██╔██╗ ██║██║  ██║    ██║     ██║     ██║
██║  ██║██╔══╝  ╚██╗ ██╔╝██║╚██╔╝██║██║██║╚██╗██║██║  ██║    ██║     ██║     ██║
██████╔╝███████╗ ╚████╔╝ ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝    ╚██████╗███████╗██║
</pre>

**A lightning-fast, privacy-first local RAG assistant for your codebase and documents.**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/TuoNomeUtente/DevMind-CLI/graphs/commit-activity)
[![Local AI](https://img.shields.io/badge/AI-100%25_Local-orange.svg)]()
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-blueviolet.svg)](https://www.trychroma.com/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black.svg)](https://ollama.ai/)

</div>

---

## What is DevMind?

DevMind is an interactive CLI designed to let you query your source code and documents in natural language directly from the terminal. Built on **RAG (Retrieval-Augmented Generation)**, ChromaDB, and locally-run LLMs via Ollama — no data ever leaves your machine.

## Features

| Feature | Description |
|---|---|
| **100% Local & Private** | Runs entirely on your hardware via Ollama and ChromaDB. Zero cloud calls. |
| **Smart Indexing** | Multithreaded indexing with MD5 semantic caching. Skips unchanged files and respects `.gitignore`. |
| **HyDE Search** | Uses Hypothetical Document Embeddings to bridge the semantic gap between natural language and source code. |
| **3D Semantic Map** | Visualize the entire vector space as an interactive 3D scatter plot in the browser. |
| **REPL Interface** | Interactive prompt built on `cmd` and `Rich` for a clean, colored terminal experience. |

---

## Prerequisites

1. **[Python 3.8+](https://www.python.org/downloads/)**
2. **[Ollama](https://ollama.ai/)** running in the background
3. Required local models:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2:1b
```

---

## Quick Start

```bash
git clone https://github.com/TuoNomeUtente/DevMind-CLI.git
cd DevMind-CLI
```

The wrapper scripts handle `venv` creation, dependency install, and startup automatically:

```bash
# Windows
devmind.bat

# macOS / Linux
chmod +x devmind.sh && ./devmind.sh
```

To install a global `devmind` command on Windows (user PATH), run once from the project folder:

```bat
devmind.bat --install
```

Then reopen your terminal and start DevMind from anywhere with:

```bat
devmind
```

Or manually:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Usage

| Command | Description | Example |
|---|---|---|
| `index <path>` | Scan and index a folder. Skips `.gitignore` patterns and MD5-cached unchanged files. | `index ./my_project` |
| `ask <question>` | Query your indexed codebase in natural language. | `ask How is authentication handled?` |
| `map` | Generate `semantic_map.html` and open an interactive 3D vector cluster view. | `map` |
| `clear` | Clear the terminal, keeping the ASCII header pinned at the top. | `clear` |
| `exit` | Exit the CLI. | `exit` |

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request with a clear description of the changes.

> **Ground rule:** Do not break the Rich-based UI. Verify indexing works end-to-end before opening a PR.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.