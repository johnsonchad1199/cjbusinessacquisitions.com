#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds the static site into the repository root.

    python3 src/build.py

Outputs: every page in pages.py, the buying-process redirect stub,
sitemap.xml, robots.txt, and vercel.json (security headers, including a
Content-Security-Policy whose hashes match the inline <script>/<style>
blocks this build produced). Always upload vercel.json together with the
HTML files: if the inline CSS/JS changes and vercel.json does not, the
browser will block the old-hash blocks.
"""
import base64
import datetime
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import head, header, FOOTER, MAIN_JS, render_icons, SITE_URL  # noqa: E402
from pages import PAGES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()

REDIRECT_STUB = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Our Buying Process | CJ Business Acquisitions</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{site}/for-business-owners.html#buying-process">
<meta http-equiv="refresh" content="0; url=/for-business-owners.html#buying-process">
</head>
<body>
<p>This page has moved to <a href="/for-business-owners.html#buying-process">For Business Owners</a>.</p>
</body>
</html>
""".format(site=SITE_URL)


def sha256(text):
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode() + "'"


def build_pages():
    written = []
    for p in PAGES:
        html = (head(p["path"], p["title"], p["description"], p["path"],
                     noindex=p.get("noindex", False), jsonld=p.get("jsonld"))
                + header(p["path"]) + p["body"] + FOOTER.replace("__MAIN_JS__", MAIN_JS))
        html = render_icons(html)
        if "[[ICON:" in html:
            raise SystemExit("Unknown icon token in %s: %s" % (p["path"], re.findall(r"\[\[ICON:[^\]]+\]\]", html)))
        out = os.path.join(ROOT, p["path"].lstrip("/"))
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(html)
        written.append(out)
    with open(os.path.join(ROOT, "buying-process.html"), "w", encoding="utf-8") as fh:
        fh.write(REDIRECT_STUB)
    return written


def collect_hashes(files):
    """Hash every executable inline <script> and every <style> actually emitted."""
    scripts, styles = set(), set()
    for f in files:
        html = open(f, encoding="utf-8").read()
        for attrs, body in re.findall(r"<script([^>]*)>(.*?)</script>", html, re.S):
            if "application/ld+json" in attrs or "src=" in attrs:
                continue
            scripts.add(sha256(body))
        for body in re.findall(r"<style>(.*?)</style>", html, re.S):
            styles.add(sha256(body))
        if re.search(r'\sstyle="', html):
            raise SystemExit("Inline style attribute found in %s (blocked by CSP) - use a class instead." % f)
        if re.search(r"\son[a-z]+=\"", html):
            raise SystemExit("Inline event handler found in %s (blocked by CSP)." % f)
    return sorted(scripts), sorted(styles)


def build_vercel_json(script_hashes, style_hashes):
    hc = "https://hcaptcha.com https://*.hcaptcha.com"
    csp = "; ".join([
        "default-src 'none'",
        "script-src " + " ".join(script_hashes) + " https://js.hcaptcha.com " + hc,
        "style-src " + " ".join(style_hashes) + " " + hc,
        "img-src 'self' data: " + hc,
        "font-src 'self'",
        "connect-src https://api.web3forms.com " + hc,
        "frame-src " + hc,
        "form-action https://api.web3forms.com",
        "base-uri 'none'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "upgrade-insecure-requests",
    ])
    security = [
        {"key": "Content-Security-Policy", "value": csp},
        {"key": "Strict-Transport-Security", "value": "max-age=63072000"},
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "X-Frame-Options", "value": "DENY"},
        {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
        {"key": "Permissions-Policy", "value": "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"},
        {"key": "Cross-Origin-Opener-Policy", "value": "same-origin"},
        {"key": "Cross-Origin-Resource-Policy", "value": "same-origin"},
    ]
    config = {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        "trailingSlash": False,
        "redirects": [
            {"source": "/buying-process", "destination": "/for-business-owners.html#buying-process", "permanent": True},
            {"source": "/buying-process.html", "destination": "/for-business-owners.html#buying-process", "permanent": True},
        ],
        "headers": [
            {"source": "/(.*)", "headers": security},
            {"source": "/inter-var-latin.woff2", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/(favicon.svg|apple-touch-icon.png|og-image.jpg)", "headers": [{"key": "Cache-Control", "value": "public, max-age=604800"}]},
        ],
    }
    with open(os.path.join(ROOT, "vercel.json"), "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
        fh.write("\n")
    return csp


def build_sitemap():
    urls = [p["path"] for p in PAGES if not p.get("noindex")]
    items = []
    for u in urls:
        loc = SITE_URL + ("/" if u == "/index.html" else u)
        items.append("  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (loc, TODAY))
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                 + "\n".join(items) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL)


if __name__ == "__main__":
    files = build_pages()
    s, st = collect_hashes(files)
    csp = build_vercel_json(s, st)
    build_sitemap()
    print("Built %d pages + redirect stub" % len(files))
    print("Inline script hashes: %d, style hashes: %d" % (len(s), len(st)))
    print("CSP length: %d chars" % len(csp))
