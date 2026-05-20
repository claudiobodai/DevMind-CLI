import cmd
import os
import hashlib
import threading
import pathspec
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from vector_db import add_document, collection, reset_database
from rag_core import ask_codebase
from visualize_db import create_3d_map

console = Console()


def chunk_text(text, max_chars=4000, overlap=400):
    """Split long text into chunks to avoid embedding context overflow."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start += (max_chars - overlap)
    return chunks


def load_gitignore_spec(folder_path):
    """Load .gitignore rules if present, otherwise use safe default ignores."""
    gitignore_path = os.path.join(folder_path, '.gitignore')
    default_ignores = [
        'node_modules/', '.git/', 'venv/', '__pycache__/',
        '.local_db/', '*.json', '.vscode/', '.idea/'
    ]

    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
                all_lines = default_ignores + [line for line in lines if line.strip() and not line.startswith('#')]
                return pathspec.PathSpec.from_lines('gitwildmatch', all_lines)
        except Exception as e:
            print(f"Warning loading .gitignore: {e}. Using default ignores.")

    return pathspec.PathSpec.from_lines('gitwildmatch', default_ignores)


def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')

    ascii_art = """
██████╗ ███████╗██╗   ██╗███╗   ███╗██╗███╗   ██╗██████╗      ██████╗██╗     ██╗
██╔══██╗██╔════╝██║   ██║████╗ ████║██║████╗  ██║██╔══██╗    ██╔════╝██║     ██║
██║  ██║█████╗  ██║   ██║██╔████╔██║██║██╔██╗ ██║██║  ██║    ██║     ██║     ██║
██║  ██║██╔══╝  ╚██╗ ██╔╝██║╚██╔╝██║██║██║╚██╗██║██║  ██║    ██║     ██║     ██║
██████╔╝███████╗ ╚████╔╝ ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝    ╚██████╗███████╗██║
    """

    title = Text(ascii_art, style="bold cyan")
    subtitle = Text("RAG Local Assistant - Codebase & Docs Search\n", style="italic cyan")
    subtitle.append("Type 'help' to see commands, 'exit' to quit.", style="white")

    panel = Panel(
        title + subtitle,
        border_style="blue",
        expand=False,
        padding=(1, 2)
    )

    console.print(panel)


class DevMindCLI(cmd.Cmd):
    prompt = 'DevMind> '

    def preloop(self):
        print_banner()

    def do_index(self, arg):
        """Index a folder in the vector database respecting .gitignore. Usage: index <path>"""
        if not arg:
            print("Error: provide a path. Example: index ./my_project")
            return

        folder_path = arg.strip()
        if not os.path.exists(folder_path):
            print(f"Error: folder '{folder_path}' does not exist.")
            return

        print("Loading exclusion filters (.gitignore)...")
        spec = load_gitignore_spec(folder_path)

        print(f"Smart scan started for folder: {folder_path}...")

        # Build MD5 cache from already-indexed documents
        print("Building MD5 cache from existing index...")
        existing = collection.get(include=["metadatas"])
        md5_cache = {}
        for meta in (existing["metadatas"] or []):
            if meta and "source" in meta and "md5" in meta:
                md5_cache[meta["source"]] = meta["md5"]

        # Collect all valid, non-ignored file paths
        valid_files = []
        for root, dirs, files in os.walk(folder_path):
            relative_root = os.path.relpath(root, folder_path)
            for file in files:
                relative_file_path = os.path.join(relative_root, file) if relative_root != "." else file
                git_style_path = relative_file_path.replace('\\', '/')

                if spec.match_file(git_style_path):
                    continue

                if file.endswith(('.txt', '.md', '.py', '.js', '.ts', '.java', '.cpp', '.vue', '.cs')):
                    valid_files.append(os.path.join(root, file))

        print(f"Found {len(valid_files)} candidate file(s). Processing with 4 workers...")

        files_updated = 0
        files_cached = 0
        counter_lock = threading.Lock()

        def process_file(file_path):
            nonlocal files_updated, files_cached
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if not content:
                    return

                current_md5 = hashlib.md5(content.encode('utf-8')).hexdigest()

                # Skip if MD5 matches — file is unchanged
                if md5_cache.get(file_path) == current_md5:
                    with counter_lock:
                        files_cached += 1
                    return

                text_chunks = chunk_text(content)
                for chunk_idx, chunk in enumerate(text_chunks):
                    doc_id = file_path if len(text_chunks) == 1 else f"{file_path}#chunk{chunk_idx}"
                    add_document(
                        doc_id=doc_id,
                        text=chunk,
                        metadata={
                            "source": file_path,
                            "ext": os.path.splitext(file_path)[1],
                            "chunk": chunk_idx,
                            "md5": current_md5
                        }
                    )
                with counter_lock:
                    files_updated += 1

            except Exception as e:
                print(f"Error reading file '{os.path.basename(file_path)}': {e}")

        try:
            with ThreadPoolExecutor(max_workers=4) as executor:
                executor.map(process_file, valid_files)
        except KeyboardInterrupt:
            print("\nIndexing interrupted by user.")
            print(f"  Files updated/added so far : {files_updated}")
            print(f"  Files skipped (cached) so far: {files_cached}")
            return

        print(f"\nIndexing completed.")
        print(f"  Files updated/added : {files_updated}")
        print(f"  Files skipped (cached): {files_cached}")

    def do_ask(self, arg):
        """Ask a question to the RAG. Usage: ask <your question>"""
        if not arg:
            print("Error: provide a question. Example: ask What are the main facts about jazz?")
            return
        
        print("Searching the database and generating the answer...")
        answer = ask_codebase(arg)
        print(f"\n{answer}\n")

    def do_map(self, arg):
        """Generate and open an interactive 3D semantic map."""
        print("Generating 3D semantic map...")
        create_3d_map()

    def do_resetdb(self, arg):
        """Delete all indexed vectors from the local database. Usage: resetdb [--yes]"""
        force = arg.strip() == "--yes"

        if not force:
            confirm = input("This will delete all indexed data. Continue? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Operation canceled.")
                return

        reset_database()
        print("Local index database cleared successfully.")

    def do_clear(self, arg):
        """Clear the terminal screen."""
        print_banner()

    def do_exit(self, arg):
        """Exit the CLI."""
        print("Goodbye.")
        return True

    def do_EOF(self, arg):
        """Exit with Ctrl+D / Ctrl+Z."""
        print()
        return True

if __name__ == '__main__':
    try:
        DevMindCLI().cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye.")