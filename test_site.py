#!/usr/bin/env python3
"""End-to-end checks against the local dev server with the real CSP applied.

    pip install playwright && playwright install chromium
    python3 src/test_site.py [--axe path/to/axe.min.js] [--shots out_dir]

Covers: every page x 4 widths x light/dark/system, console errors, CSP
violations, horizontal overflow, theme persistence and no-flash, skip link,
mobile menu keyboard behavior, internal links/anchors, the 404 page, the old
buying-process redirect, and the form flows (validation, timing trap,
captcha missing/blocked, success, server error, 429, network failure) with
Web3Forms and hCaptcha mocked. Optional: axe-core WCAG 2.2 AA scan.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8765
BASE = "http://127.0.0.1:%d" % PORT
PAGES = ["/", "/about.html", "/investment-criteria.html", "/for-business-owners.html",
         "/submit-a-business.html", "/contact.html", "/privacy.html", "/this-page-does-not-exist"]
WIDTHS = [1440, 1024, 768, 390]

INIT = """
window.__csp=[];window.__themeAtDCL=null;
document.addEventListener('securitypolicyviolation',function(e){window.__csp.push(e.violatedDirective+' '+e.blockedURI)});
document.addEventListener('DOMContentLoaded',function(){window.__themeAtDCL=document.documentElement.getAttribute('data-theme')});
"""

HCAPTCHA_STUB = """
window.hcaptcha={_r:{},render:function(el,o){var id='w'+Math.random();var t=document.createElement('textarea');t.name='h-captcha-response';t.hidden=true;t.value=window.__capToken||'';el.appendChild(t);this._r[id]=t;return id;},
getResponse:function(id){return this._r[id]?this._r[id].value:'';},reset:function(id){},remove:function(id){delete this._r[id];}};
setTimeout(function(){window.cjbaCaptchaReady&&window.cjbaCaptchaReady();},10);
"""

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("  FAIL:", msg)


def wait_text(pg, sel, needle, timeout=6.0):
    end = time.time() + timeout
    while time.time() < end:
        try:
            if needle in pg.inner_text(sel):
                return True
        except Exception:
            pass
        time.sleep(0.1)
    check(False, "timed out waiting for %r in %s" % (needle, sel))
    return False


def fill_valid_submit(pg):
    pg.fill("#contact_name", "Test Seller")
    pg.fill("#email", "seller@example.com")
    pg.fill("#phone", "(336) 555-0100")
    pg.fill("#company", "Acme Precision")
    pg.fill("#industry", "Precision machining")
    pg.fill("#location", "Greensboro, NC")
    pg.fill("#description", "Family-owned machine shop, 22 years, 35 employees, aerospace customers.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axe")
    ap.add_argument("--shots")
    args = ap.parse_args()

    srv = subprocess.Popen([sys.executable, os.path.join(ROOT, "src", "dev_server.py"), str(PORT)])
    for _ in range(50):
        try:
            urllib.request.urlopen(BASE + "/robots.txt"); break
        except Exception:
            time.sleep(0.1)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()

            # ---------- 1. Pages x widths x themes ----------
            print("1. Render matrix (CSP enforced)")
            for pref, scheme in [("light", "light"), ("dark", "light"), ("system", "dark"), ("system", "light")]:
                for w in WIDTHS:
                    ctx = b.new_context(viewport={"width": w, "height": 900}, color_scheme=scheme)
                    ctx.add_init_script(INIT + ("try{localStorage.setItem('theme','%s')}catch(e){}" % pref))
                    pg = ctx.new_page()
                    errs = []
                    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                    pg.on("pageerror", lambda e: errs.append(str(e)))
                    for path in PAGES:
                        errs.clear()
                        resp = pg.goto(BASE + path, wait_until="networkidle")
                        exp_status = 404 if "does-not-exist" in path else 200
                        check(resp.status == exp_status, "%s status %s" % (path, resp.status))
                        want = "dark" if (pref == "dark" or (pref == "system" and scheme == "dark")) else "light"
                        got = pg.evaluate("document.documentElement.getAttribute('data-theme')")
                        dcl = pg.evaluate("window.__themeAtDCL")
                        check(got == want and dcl == want, "%s %s/%s w%d theme=%s at-DCL=%s want %s" % (path, pref, scheme, w, got, dcl, want))
                        csp = pg.evaluate("window.__csp")
                        check(not csp, "%s CSP violations: %s" % (path, csp))
                        errs2 = [e for e in errs if not ("does-not-exist" in path and "404" in e)]
                        check(not errs2, "%s console errors: %s" % (path, errs2))
                        ov = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                        check(ov <= 0, "%s w%d horizontal overflow %dpx" % (path, w, ov))
                        font_ok = pg.evaluate("document.fonts.check('16px Inter')")
                        check(font_ok, "%s Inter font not loaded" % path)
                        if args.shots and w in (1440, 390) and path in ("/", "/for-business-owners.html", "/submit-a-business.html", "/this-page-does-not-exist"):
                            name = "%s-%s-%s-%d.png" % (path.strip("/").replace(".html", "") or "home", pref, scheme, w)
                            pg.screenshot(path=os.path.join(args.shots, name), full_page=True)
                    ctx.close()

            # ---------- 2. Theme switch + persistence ----------
            print("2. Theme switch")
            ctx = b.new_context(viewport={"width": 1280, "height": 900}, color_scheme="light")
            ctx.add_init_script(INIT)
            pg = ctx.new_page()
            pg.goto(BASE + "/")
            check(pg.get_attribute("[data-theme-set=system]", "aria-pressed") == "true", "system pressed by default")
            pg.click("[data-theme-set=dark]")
            check(pg.evaluate("document.documentElement.dataset.theme") == "dark", "dark applied on click")
            check(pg.evaluate("localStorage.getItem('theme')") == "dark", "dark persisted")
            pg.goto(BASE + "/about.html")
            check(pg.evaluate("window.__themeAtDCL") == "dark", "dark persists across pages, no flash")
            check(pg.get_attribute("[data-theme-set=dark]", "aria-pressed") == "true", "dark pressed after reload")
            pg.click("[data-theme-set=system]")
            pg.emulate_media(color_scheme="dark")
            pg.wait_for_timeout(100)
            check(pg.evaluate("document.documentElement.dataset.theme") == "dark", "system follows OS change live")
            ctx.close()

            # ---------- 3. Keyboard + mobile nav ----------
            print("3. Keyboard and mobile navigation")
            ctx = b.new_context(viewport={"width": 390, "height": 844})
            pg = ctx.new_page()
            pg.goto(BASE + "/about.html")
            pg.keyboard.press("Tab")
            check(pg.evaluate("document.activeElement.className") == "skip-link", "first Tab focuses skip link")
            pg.keyboard.press("Enter")
            check(pg.evaluate("location.hash") == "#main", "skip link targets #main")
            pg.click(".nav-toggle")
            check(pg.get_attribute(".nav-toggle", "aria-expanded") == "true", "menu opens")
            check(pg.is_visible("#site-nav a[href='/contact.html']"), "menu links visible when open")
            check(pg.evaluate("document.activeElement.closest('#site-nav')!==null"), "focus moves into menu")
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(300)
            check(pg.get_attribute(".nav-toggle", "aria-expanded") == "false", "Escape closes menu")
            check(pg.evaluate("document.activeElement.classList.contains('nav-toggle')"), "focus returns to toggle")
            check(not pg.is_visible("#site-nav a[href='/contact.html']"), "menu hidden when closed")
            ctx.close()

            # ---------- 4. Links, anchors, redirect ----------
            print("4. Links and anchors")
            ctx = b.new_context()
            pg = ctx.new_page()
            seen = set()
            for path in PAGES[:-1]:
                pg.goto(BASE + path)
                for href in pg.eval_on_selector_all("a[href]", "els=>els.map(e=>e.getAttribute('href'))"):
                    if href.startswith(("mailto:", "tel:", "https://www.linkedin.com")):
                        continue
                    check(href.startswith(("/", "#", "https://www.cjbusinessacquisitions.com")), "%s non-root-relative link %s" % (path, href))
                    if href.startswith("/"):
                        seen.add(href)
                    if href.startswith("#"):
                        check(pg.query_selector(href) is not None, "%s missing anchor %s" % (path, href))
            for href in sorted(seen):
                url, _, frag = href.partition("#")
                r = pg.goto(BASE + url)
                check(r.status == 200, "link %s -> %s" % (href, r.status))
                if frag:
                    check(pg.query_selector("#" + frag) is not None, "anchor %s missing" % href)
            r = pg.goto(BASE + "/buying-process.html")
            check(pg.url.endswith("/for-business-owners.html#buying-process"), "old buying-process URL redirects (%s)" % pg.url)
            for asset in ["/favicon.svg", "/apple-touch-icon.png", "/og-image.jpg", "/inter-var-latin.woff2", "/robots.txt", "/sitemap.xml"]:
                check(ctx.request.get(BASE + asset).status == 200, "asset %s" % asset)
            ctx.close()

            # ---------- 5. Forms ----------
            print("5. Form flows (Web3Forms + hCaptcha mocked)")
            for page_path in ["/submit-a-business.html", "/contact.html"]:
                ctx = b.new_context(viewport={"width": 1280, "height": 900})
                ctx.add_init_script(INIT)
                state = {"mode": "success", "posts": []}

                def api(route, req, state=state):
                    state["posts"].append(req.post_data_buffer)
                    m = state["mode"]
                    if m == "success":
                        route.fulfill(status=200, content_type="application/json", body=json.dumps({"success": True, "message": "ok"}))
                    elif m == "error":
                        route.fulfill(status=400, content_type="application/json", body=json.dumps({"success": False, "message": "Invalid access key: internal detail"}))
                    elif m == "429":
                        route.fulfill(status=429, content_type="text/plain", body="rate limited")
                    else:
                        route.abort()
                ctx.route("https://api.web3forms.com/**", api)
                cap = {"block": False}
                ctx.route("https://js.hcaptcha.com/**", lambda route, req: route.abort() if cap["block"] else route.fulfill(status=200, content_type="application/javascript", body=HCAPTCHA_STUB))
                pg = ctx.new_page()
                errs = []
                pg.on("pageerror", lambda e: errs.append(str(e)))
                pg.goto(BASE + page_path)
                pg.evaluate("window.__capToken='test-token'")
                # empty submit
                pg.click("button[type=submit]")
                check(pg.is_visible("#form-alert"), "%s empty submit shows error summary" % page_path)
                check(pg.evaluate("document.activeElement.id") == "form-alert", "%s focus moves to error summary" % page_path)
                n_invalid = pg.evaluate("document.querySelectorAll('[aria-invalid=true]').length")
                check(n_invalid >= 3, "%s required fields flagged (%d)" % (page_path, n_invalid))
                check(not state["posts"], "%s nothing sent when invalid" % page_path)
                # summary links jump to fields
                first = pg.eval_on_selector("#form-alert a", "a=>a.getAttribute('href')")
                check(first and pg.query_selector(first) is not None, "%s summary links to field" % page_path)
                if page_path == "/submit-a-business.html":
                    fill_valid_submit(pg)
                    pg.fill("#email", "not-an-email")
                    pg.click("button[type=submit]")
                    check(pg.get_attribute("#email", "aria-invalid") == "true", "invalid email flagged")
                    check("valid email" in pg.inner_text("#email-error"), "email error text")
                    pg.fill("#email", "seller@example.com")
                    pg.fill("#phone", "call me maybe")
                    pg.click("button[type=submit]")
                    check(pg.get_attribute("#phone", "aria-invalid") == "true", "bad phone flagged")
                    pg.fill("#phone", "336-555-0100 ext 12")
                else:
                    pg.fill("#cname", "Test Broker")
                    pg.fill("#cemail", "broker@example.com")
                    pg.select_option("#cinterest", "Representing a Business Owner")
                    pg.fill("#cmessage", "I represent a seller of a fabrication shop in Charlotte.")
                check(not state["posts"], "%s nothing sent before timing window" % page_path)
                pg.wait_for_timeout(4200)
                # captcha not completed
                pg.evaluate("window.__capToken=''")
                pg.evaluate("document.querySelector('[name=h-captcha-response]') && (document.querySelector('[name=h-captcha-response]').value='')")
                pg.click("button[type=submit]")
                check("verification" in pg.inner_text("#form-alert").lower(), "%s captcha required message" % page_path)
                check(not state["posts"], "%s nothing sent without captcha" % page_path)
                pg.evaluate("document.querySelector('[name=h-captcha-response]').value='test-token'")
                # server error: generic message, no internal detail
                state["mode"] = "error"
                pg.click("button[type=submit]")
                pg.wait_for_selector("#form-alert.alert-error")
                txt = pg.inner_text("#form-alert")
                check("internal detail" not in txt and "cjohnson@" in txt, "%s server error handled without leaking detail" % page_path)
                check(pg.is_visible("form[data-form]"), "%s form kept after error" % page_path)
                check(pg.is_enabled("button[type=submit]"), "%s button re-enabled after error" % page_path)
                # 429
                pg.evaluate("document.querySelector('[name=h-captcha-response]').value='test-token'")
                state["mode"] = "429"
                pg.click("button[type=submit]")
                wait_text(pg, "#form-alert", "Too many")
                # network failure
                state["mode"] = "abort"
                pg.click("button[type=submit]")
                wait_text(pg, "#form-alert", "could not reach")
                # success
                state["mode"] = "success"
                n_before = len(state["posts"])
                pg.click("button[type=submit]")
                pg.wait_for_selector("#form-success:not([hidden])")
                check(not pg.is_visible("form[data-form]"), "%s form hidden after success" % page_path)
                check(pg.evaluate("document.activeElement.tagName") == "H2", "%s focus moves to success heading" % page_path)
                body = state["posts"][n_before].decode("utf-8", "replace")
                check("34ee8b9a-8fc9-46f6-b3f2-9fcbcecbf226" in body, "%s access key posted" % page_path)
                check("test-token" in body, "%s captcha token posted" % page_path)
                check('name="botcheck"' not in body, "%s honeypot unchecked not sent" % page_path)
                check(not errs, "%s page errors: %s" % (page_path, errs))
                csp = pg.evaluate("window.__csp")
                check(not csp, "%s CSP violations during form flow: %s" % (page_path, csp))
                ctx.close()

                # captcha blocked by content blocker
                ctx = b.new_context()
                ctx.route("https://js.hcaptcha.com/**", lambda route, req: route.abort())
                pg = ctx.new_page()
                pg.goto(BASE + page_path)
                pg.focus("input:not([type=hidden]):not([tabindex='-1'])")
                wait_text(pg, "#captcha-note", "could not load")
                ctx.close()

            # ---------- 6. axe-core ----------
            if args.axe:
                print("6. axe-core WCAG 2.2 AA")
                axe_src = open(args.axe).read()
                for theme in ["light", "dark"]:
                    for w in [1280, 390]:
                        ctx = b.new_context(viewport={"width": w, "height": 900}, bypass_csp=True)
                        ctx.add_init_script("try{localStorage.setItem('theme','%s')}catch(e){}" % theme)
                        pg = ctx.new_page()
                        for path in PAGES:
                            pg.goto(BASE + path, wait_until="networkidle")
                            pg.add_script_tag(content=axe_src)
                            res = pg.evaluate("""async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});
                              return r.violations.map(v=>({id:v.id,impact:v.impact,n:v.nodes.length,t:v.nodes.slice(0,3).map(n=>n.target.join(' ')+' :: '+(n.failureSummary||'').split('\\n').slice(1,2).join(''))}))}""")
                            for v in res:
                                check(False, "axe %s %s w%d: %s (%s) x%d %s" % (path, theme, w, v["id"], v["impact"], v["n"], v["t"]))
                        ctx.close()
            b.close()
    finally:
        srv.terminate()

    print("\n%d failure(s)" % len(failures))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
