# cjbusinessacquisitions.com

Static website for CJ Business Acquisitions. It is plain HTML with no framework and no npm dependencies. It is hosted on Vercel, and the DNS runs through Cloudflare.

## Layout

```
/                       Deployed site (generated; do not hand-edit HTML)
  index.html ...        Pages, each with inlined CSS and JS
  404.html              Custom not-found page (Vercel serves it automatically)
  buying-process.html   Redirect stub for the old URL
  privacy.html          Privacy policy
  vercel.json           Security headers (CSP hashes), caching, redirects: generated
  sitemap.xml, robots.txt   Generated
  inter-var-latin.woff2 Self-hosted Inter font (SIL OFL 1.1, see src/licenses)
  favicon.svg, apple-touch-icon.png, og-image.jpg
src/                    Source (excluded from deployment by .vercelignore)
  design.py             Design tokens, CSS, JS, icons, header/footer
  pages.py              All page content and forms
  build.py              Builds pages + vercel.json + sitemap
  make_images.py        Regenerates favicon / touch icon / social image
  dev_server.py         Local preview that applies vercel.json headers
  test_site.py          End-to-end test suite (Playwright)
OPERATIONS.md           Security, deployment, rollback, and backup runbook
```

## Editing content

1. Edit the text in `src/pages.py`. Styling lives in `src/design.py`.
2. Run `python3 src/build.py`.
3. Optional: run `python3 src/dev_server.py`, then open http://127.0.0.1:8080.
4. Optional: run `python3 src/test_site.py`. This requires `pip install playwright`.
5. Upload the changed root files **and `vercel.json`** to GitHub. Vercel then redeploys automatically.

Always upload `vercel.json` together with the HTML files. The Content-Security-Policy in `vercel.json` includes fingerprints (hashes) of the inline CSS and JS. If the CSS or JS changes and `vercel.json` does not, browsers will block the page's styling and scripts.

## Rules of the house

- Site copy says "we", never "I".
- Use root-relative links (`/about.html`). The 404 page can appear at any URL depth, so relative links would break there.
- Never add `style="..."` attributes or `onclick=` handlers. The CSP blocks them, and the build fails if it finds any.
- Never put private keys in this repository. The Web3Forms access key in `src/pages.py` is public by design: it can only send email to the account owner.
