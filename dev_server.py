#!/usr/bin/env python3
"""Local preview that mimics Vercel: applies vercel.json headers and redirects,
and serves 404.html with a 404 status.   python3 src/dev_server.py [port]
"""
import http.server
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "vercel.json")))


def pattern(src):
    return re.compile("^" + src + "$")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        path = self.path.split("?")[0].split("#")[0]
        for rule in CFG.get("headers", []):
            if pattern(rule["source"]).match(path):
                for h in rule["headers"]:
                    v = h["value"]
                    if h["key"] == "Content-Security-Policy":
                        v = v.replace("; upgrade-insecure-requests", "")  # plain-http localhost
                    if h["key"] == "Strict-Transport-Security":
                        continue
                    self.send_header(h["key"], v)
        super().end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        for r in CFG.get("redirects", []):
            if path == r["source"]:
                self.send_response(308 if r.get("permanent") else 307)
                self.send_header("Location", r["destination"])
                self.end_headers()
                return
        if path.startswith("/src/") or path.endswith((".md", ".py")) or "/." in path:
            return self.send_404()
        full = os.path.join(ROOT, path.lstrip("/"))
        if path == "/" or os.path.isfile(full):
            return super().do_GET()
        return self.send_404()

    def send_404(self):
        body = open(os.path.join(ROOT, "404.html"), "rb").read()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
