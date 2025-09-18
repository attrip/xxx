from __future__ import annotations

import http.server
import os
import socketserver
import threading
import webbrowser
import sys


def open_browser(url: str) -> None:
    try:
        webbrowser.open_new_tab(url)
    except Exception:
        pass


Handler = http.server.SimpleHTTPRequestHandler


"""Static-only server. All git APIs removed for safety."""


def serve(port: int = 8000, open_path: str | None = None) -> None:
    root = os.path.abspath(os.getcwd())
    os.chdir(root)

    handler = Handler
    with socketserver.TCPServer(("", port), handler) as httpd:
        # Default to partner site if specified, else psytrance editor
        index = open_path or "/examples/psytrance_prompt_editor.html"
        url = f"http://localhost:{port}{index}"
        threading.Timer(0.5, open_browser, args=(url,)).start()
        print(f"Serving {root} at {url}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    index = os.environ.get("OPEN_PATH")
    if not index and "--index" in sys.argv:
        try:
            idx = sys.argv.index("--index")
            index = sys.argv[idx + 1]
        except Exception:
            index = None
    serve(open_path=index)
