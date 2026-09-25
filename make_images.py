#!/usr/bin/env python3
"""Regenerates favicon.svg, apple-touch-icon.png and og-image.jpg.
Only needed if branding changes. Requires: pip install playwright && playwright install chromium
"""
import base64
import os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = base64.b64encode(open(os.path.join(ROOT, "inter-var-latin.woff2"), "rb").read()).decode()

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#173e66"/><text x="32" y="41.5" font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif" font-size="25" font-weight="800" letter-spacing="0.5" fill="#ffffff" text-anchor="middle">CJ</text></svg>
"""

BASE_CSS = "@font-face{font-family:Inter;src:url(data:font/woff2;base64,%s) format('woff2');font-weight:100 900}*{margin:0;box-sizing:border-box}body{font-family:Inter,sans-serif}" % FONT

ICON_HTML = """<html><head><style>%s body{width:180px;height:180px;background:#173e66;display:grid;place-items:center;color:#fff;font-weight:800;font-size:70px;letter-spacing:1px}</style></head><body>CJ</body></html>""" % BASE_CSS

OG_HTML = """<html><head><style>%s
body{width:1200px;height:630px;background:linear-gradient(155deg,#0d1f33 0%%,#173e66 100%%);color:#fff;padding:72px 80px;position:relative;overflow:hidden}
body:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:56px 56px}
.brand{display:flex;align-items:center;gap:18px;position:relative}
.mark{width:64px;height:64px;border-radius:14px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);display:grid;place-items:center;font-weight:800;font-size:26px}
.name{font-size:30px;font-weight:700;letter-spacing:-.02em}
.sub{font-size:15px;letter-spacing:.16em;text-transform:uppercase;color:#c5d2df;font-weight:600;margin-top:2px}
h1{position:relative;font-size:64px;line-height:1.08;letter-spacing:-.035em;font-weight:750;margin-top:84px;max-width:980px}
.meta{position:relative;margin-top:36px;display:flex;gap:14px}
.pill{border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.07);border-radius:999px;padding:10px 20px;font-size:21px;color:#e3eaf2}
.rule{position:absolute;left:80px;bottom:64px;width:88px;height:4px;background:#dcc085;border-radius:2px}
.url{position:absolute;right:80px;bottom:56px;font-size:20px;color:#c5d2df}
</style></head><body>
<div class="brand"><div class="mark">CJ</div><div><div class="name">CJ Business Acquisitions</div><div class="sub">Engineering &amp; Manufacturing</div></div></div>
<h1>Acquiring established manufacturing &amp; engineering businesses in North Carolina</h1>
<div class="meta"><span class="pill">Operator-led</span><span class="pill">$500K&ndash;$1.5M adj. EBITDA</span><span class="pill">Confidential</span></div>
<div class="rule"></div><div class="url">cjbusinessacquisitions.com</div>
</body></html>""" % BASE_CSS

if __name__ == "__main__":
    with open(os.path.join(ROOT, "favicon.svg"), "w") as fh:
        fh.write(FAVICON)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 180, "height": 180})
        pg.set_content(ICON_HTML); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ROOT, "apple-touch-icon.png"))
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        pg.set_content(OG_HTML); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ROOT, "og-image.png"))
        from PIL import Image
        Image.open(os.path.join(ROOT, "og-image.png")).convert("RGB").save(os.path.join(ROOT, "og-image.jpg"), "JPEG", quality=86, optimize=True, progressive=True)
        os.remove(os.path.join(ROOT, "og-image.png"))
        b.close()
    print("images written")
