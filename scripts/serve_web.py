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
import sys


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
        # CORS for file:// and other origins
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
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
            body = self._read_json()
            repo = _normalize_repo(body.get("repo"))
            res = {"repo": repo}
            res["cwd"] = repo or os.getcwd()
            res["branch"] = _run_capture_in(repo, ["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()
            res["status"] = _run_capture_in(repo, ["git", "status", "--porcelain=v1", "-b"])  # may be empty
            res["remote"] = _run_capture_in(repo, ["git", "remote", "-v"])  # may be empty
            return self._send_json(res)
        if parsed.path == "/api/git/add":
            body = self._read_json()
            paths = body.get("paths", [])
            added = []
            root = _normalize_repo(body.get("repo")) or os.getcwd()
            for p in paths:
                if not p:
                    continue
                # allow file:// URLs or absolute/relative paths under repo
                if p.startswith("file://"):
                    p = urllib.parse.urlparse(p).path
                ap = os.path.abspath(p if os.path.isabs(p) else os.path.join(root, p))
                if not ap.startswith(root):
                    continue
                if os.path.exists(ap):
                    _run_capture_in(root, ["git", "add", ap])
                    added.append(os.path.relpath(ap, root))
            return self._send_json({"added": added})
        if parsed.path == "/api/git/commit":
            body = self._read_json()
            msg = (body.get("message") or "").strip() or "chore: update"
            repo = _normalize_repo(body.get("repo"))
            out = _run_capture_in(repo, ["git", "commit", "-m", msg])
            return self._send_json({"output": out})
        if parsed.path == "/api/git/push":
            body = self._read_json()
            repo = _normalize_repo(body.get("repo"))
            remote = (body.get("remote") or "origin").strip()
            branch = (body.get("branch") or _run_capture_in(repo, ["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip() or "main")
            out = _run_capture_in(repo, ["git", "push", "-u", remote, branch])
            return self._send_json({"output": out, "remote": remote, "branch": branch})
        if parsed.path == "/api/handle_url":
            body = self._read_json()
            url = (body.get("url") or "").strip()
            repo = _normalize_repo(body.get("repo")) or os.getcwd()
            action = "noop"
            info = {}
            if url.startswith("file://") or os.path.exists(url):
                # Treat as local path; stage it
                p = url
                if url.startswith("file://"):
                    p = urllib.parse.urlparse(url).path
                ap = os.path.abspath(p if os.path.isabs(p) else os.path.join(repo, p))
                if os.path.exists(ap):
                    _run_capture_in(repo, ["git", "add", ap])
                    action = "staged"
                    info["path"] = ap
            else:
                # Unrecognized; return as external URL for user handling
                action = "external"
                info["url"] = url
            return self._send_json({"action": action, **info})

        if parsed.path == "/api/file/ensure_html":
            body = self._read_json()
            path = (body.get("path") or "").strip()
            title = (body.get("title") or "My Page").strip()
            do_open = bool(body.get("open"))
            if path.startswith("file://"):
                path = urllib.parse.urlparse(path).path
            ap = os.path.abspath(path)
            os.makedirs(os.path.dirname(ap), exist_ok=True)
            created = False
            if not os.path.exists(ap):
                with open(ap, "w", encoding="utf-8") as f:
                    f.write(_html_boilerplate(title))
                created = True
            if do_open:
                try:
                    webbrowser.open_new_tab("file://" + ap)
                except Exception:
                    pass
            return self._send_json({"path": ap, "file_url": "file://" + ap, "created": created})

        if parsed.path == "/api/open":
            body = self._read_json()
            target = (body.get("target") or "").strip()
            try:
                webbrowser.open_new_tab(target)
                return self._send_json({"ok": True})
            except Exception as e:
                return self._send_json({"ok": False, "error": str(e)}, code=500)

        return self._send_json({"error": "unknown route"}, code=404)

    def do_OPTIONS(self):  # noqa: N802
        # Preflight CORS support
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()


def _run_capture(cmd):
    try:
        res = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return res.stdout.decode("utf-8", errors="replace")
    except Exception as e:
        return f"<error: {e}>\n"


def _run_capture_in(repo: str | None, cmd):
    if not repo:
        return _run_capture(cmd)
    try:
        res = subprocess.run(cmd, cwd=repo, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return res.stdout.decode("utf-8", errors="replace")
    except Exception as e:
        return f"<error: {e}>\n"


def _normalize_repo(p: str | None) -> str | None:
    if not p:
        return None
    if p.startswith("file://"):
        p = urllib.parse.urlparse(p).path
    ap = os.path.abspath(p)
    return ap


def _html_boilerplate(title: str) -> str:
    return (
        "<!doctype html>\n"
        "<html lang=\"ja\">\n"
        "  <head>\n"
        "    <meta charset=\"utf-8\" />\n"
        "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n"
        f"    <title>{title}</title>\n"
        "    <style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:20px}</style>\n"
        "  </head>\n"
        "  <body>\n"
        f"    <h1>{title}</h1>\n"
        "    <p>初期化されたページです。編集を始めましょう。</p>\n"
        "  </body>\n"
        "</html>\n"
    )


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
    index = os.environ.get("OPEN_PATH")
    if not index and "--index" in sys.argv:
        try:
            idx = sys.argv.index("--index")
            index = sys.argv[idx + 1]
        except Exception:
            index = None
    serve(open_path=index)
