"""Serve repository text artifacts locally with an explicit UTF-8 charset."""
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import base64
import tempfile


class Utf8Handler(SimpleHTTPRequestHandler):
    def _capture_page(self, message=""):
        body = f"<!doctype html><meta charset='utf-8'><p>{escape(message)}</p><form method='post' action='/capture'><textarea name='payload' rows='30' cols='120'></textarea><button type='submit'>save</button></form>".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        parsed = urlsplit(self.path)
        if parsed.path != "/capture":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        payload = form.get("payload", [""])[0]
        target = Path(tempfile.gettempdir()) / "llm_lab_capture.txt"
        target.write_text(payload, encoding="utf-8", newline="\n")
        self._capture_page(f"saved {target}")

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path == "/capture":
            self._capture_page()
            return
        if parsed.path.lower().endswith((".txt", ".json", ".md", ".patch")):
            target = self.translate_path(parsed.path)
            try:
                raw = Path(target).read_bytes()
            except (OSError, UnicodeError):
                self.send_error(404)
                return
            if "b64" in parse_qs(parsed.query):
                page = base64.b64encode(raw)
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=us-ascii")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)
                return
            body = raw.decode("utf-8")
            page = f"<!doctype html><meta charset='utf-8'><pre>{escape(body)}</pre>".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
            return
        super().do_GET()

    def guess_type(self, path):
        content_type = super().guess_type(path)
        if Path(path).suffix.lower() in {".txt", ".json", ".md", ".patch"}:
            return "text/plain; charset=utf-8"
        return content_type


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8765), Utf8Handler).serve_forever()
