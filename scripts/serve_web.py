from __future__ import annotations

import http.server
import os
import socketserver
import threading
import webbrowser


def open_browser(url: str) -> None:
    try:
        webbrowser.open_new_tab(url)
    except Exception:
        pass


def serve(port: int = 8000) -> None:
    root = os.path.abspath(os.getcwd())
    os.chdir(root)

    # Serve project root so we can access examples/ and picture_diary/
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/examples/psytrance_prompt_editor.html"
        threading.Timer(0.5, open_browser, args=(url,)).start()
        print(f"Serving {root} at {url}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    serve()
