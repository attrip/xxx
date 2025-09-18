from __future__ import annotations

import http.server
import json
import os
import shlex
import socketserver
import subprocess
import threading
import urllib.parse
import webbrowser


def open_browser(url: str) -> None:
    try:
        webbrowser.open_new_tab(url)
    except Exception:
        pass


class DevHandler(http.server.SimpleHTTPRequestHandler):
    server_version = "DevServer/0.1"

    def _send_json(self, obj, code=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_POST(self):  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/git/status":
            res = {}
            res["cwd"] = os.getcwd()
            res["branch"] = _run_capture(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()
            res["status"] = _run_capture(["git", "status", "--porcelain=v1", "-b"])  # may be empty
            res["remote"] = _run_capture(["git", "remote", "-v"])  # may be empty
            return self._send_json(res)
        if parsed.path == "/api/git/add":
            body = self._read_json()
            paths = body.get("paths", [])
            added = []
            root = os.getcwd()
            for p in paths:
                if not p:
                    continue
                # allow file:// URLs or absolute/relative paths under repo
                if p.startswith("file://"):
                    p = urllib.parse.urlparse(p).path
                ap = os.path.abspath(p)
                if not ap.startswith(root):
                    continue
                if os.path.exists(ap):
                    _run_capture(["git", "add", ap])
                    added.append(os.path.relpath(ap, root))
            return self._send_json({"added": added})
        if parsed.path == "/api/git/commit":
            body = self._read_json()
            msg = (body.get("message") or "").strip() or "chore: update"
            out = _run_capture(["git", "commit", "-m", msg])
            return self._send_json({"output": out})
        if parsed.path == "/api/git/push":
            body = self._read_json()
            remote = (body.get("remote") or "origin").strip()
            branch = (body.get("branch") or _run_capture(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip() or "main")
            out = _run_capture(["git", "push", "-u", remote, branch])
            return self._send_json({"output": out, "remote": remote, "branch": branch})
        if parsed.path == "/api/handle_url":
            body = self._read_json()
            url = (body.get("url") or "").strip()
            action = "noop"
            info = {}
            if url.startswith("file://") or os.path.exists(url):
                # Treat as local path; stage it
                p = url
                if url.startswith("file://"):
                    p = urllib.parse.urlparse(url).path
                ap = os.path.abspath(p)
                if os.path.exists(ap):
                    _run_capture(["git", "add", ap])
                    action = "staged"
                    info["path"] = ap
            else:
                # Unrecognized; return as external URL for user handling
                action = "external"
                info["url"] = url
            return self._send_json({"action": action, **info})

        return self._send_json({"error": "unknown route"}, code=404)


def _run_capture(cmd):
    try:
        res = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return res.stdout.decode("utf-8", errors="replace")
    except Exception as e:
        return f"<error: {e}>\n"


def serve(port: int = 8000, open_path: str | None = None) -> None:
    root = os.path.abspath(os.getcwd())
    os.chdir(root)

    handler = DevHandler
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
    serve()
