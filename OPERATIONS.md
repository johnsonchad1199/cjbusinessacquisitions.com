# Operations and Security Runbook

Last reviewed: 2026-09-25

## 1. Architecture

| Layer | Provider | Notes |
|---|---|---|
| Hosting / CDN / TLS | Vercel (project under `johnsonchad1199-3949`) | Static files only. No server functions, database, or login. |
| DNS | Cloudflare | Records for Vercel should be **DNS only (grey cloud)**. |
| Source | GitHub repo `cjbusinessacquisitions.com` | Pushing to the production branch deploys automatically. |
| Forms | Web3Forms (free plan) | The browser posts directly to `api.web3forms.com`. Submissions are emailed to cjohnson@cjbusinessacquisitions.com. |
| Bot protection | hCaptcha via Web3Forms | Loads only after a visitor starts filling in a form. |
| Email | Google Workspace | |

Because the site has no server code, it has no database or shell commands to inject into and no sessions or cookies to hijack. That rules out SQL injection, command injection, CSRF, and authentication bypass on our side. The main remaining risks are spam submissions, a compromised third-party script, and account takeover of GitHub, Vercel, Cloudflare, or Web3Forms.

## 2. Security controls in place

- **HTTP security headers** are generated into `vercel.json` by `src/build.py`:
  - Content-Security-Policy with `default-src 'none'`. Inline script and style are allowed only by SHA-256 hash, and third-party access is limited to hCaptcha and Web3Forms.
  - `frame-ancestors 'none'` and `X-Frame-Options: DENY` prevent clickjacking.
  - `form-action` is limited to Web3Forms, and `base-uri 'none'` and `object-src 'none'` are set.
  - HSTS is set to 2 years. `includeSubDomains` and `preload` are intentionally not set until every subdomain is confirmed to serve HTTPS.
  - `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, a restrictive `Permissions-Policy`, `Cross-Origin-Opener-Policy: same-origin`, and `Cross-Origin-Resource-Policy: same-origin`.
- **No `innerHTML` with dynamic data.** Status and error messages are built with `textContent`. The site never displays visitor input back on a page.
- **Forms:**
  - Required fields, length limits, and email and phone formats are checked in the browser. Errors appear per field and in a summary box.
  - A honeypot checkbox (`botcheck`) catches simple bots; Web3Forms rejects submissions where it is checked.
  - Submissions made less than 4 seconds after the page loads are refused.
  - An hCaptcha token is required before sending.
  - Requests time out after 20 seconds.
  - Error messages are generic and never echo server responses. HTTP 429 (rate limited) and offline states have their own friendly messages.
- **Secrets:** there are no private keys in the code. `.gitignore` blocks `.env*`, `*.pem`, and `*.key`. `.vercelignore` keeps `src/` and `*.md` out of the public deployment.

## 3. Manual actions (in priority order)

1. **Turn on hCaptcha enforcement in Web3Forms.** In the Web3Forms dashboard, open your form's settings, enable hCaptcha, and save. Until you do this, Web3Forms accepts submissions without a captcha token, so a bot can skip it.
2. **Deploy the files**, then check the live site as described in section 5.
3. **Turn on 2-factor authentication** on GitHub, Vercel, Cloudflare, Web3Forms, and Google Workspace. Account takeover is the biggest realistic risk to this site.
4. **Vercel plan.** Vercel's Hobby plan allows non-commercial use only. Because this is a business site, either upgrade to Pro or move hosting later (Cloudflare Pages is free for commercial use). The code works unchanged on Pro.
5. **GitHub.** Make the repository **private** (Vercel works with private repos). Then protect the production branch (Settings → Branches → add a rule: block force-pushes and deletion).
6. **Vercel Firewall.** Leave the default protections on. You can also add the one custom rate-limit rule the Hobby plan allows, for example on `/*` with a limit of 300 requests per 60 seconds per IP. Note this does not cover form posts, because those go straight to Web3Forms.
7. **Vercel preview deployments.** Under Settings → Deployment Protection, keep Vercel Authentication on for Preview deployments so unfinished versions are not public.
8. **Cloudflare DNS.** Keep the Vercel records set to DNS only. Enable DNSSEC (Cloudflare: DNS → Settings → DNSSEC). Confirm that SPF, DKIM, and DMARC exist for Google Workspace, since they protect your domain from email spoofing.
9. **Legal review.** Have an attorney review `privacy.html`, which was drafted as a starting point.

## 4. Deploying a change

1. Edit `src/`, then run `python3 src/build.py`.
2. On GitHub, open the repository, choose **Add file → Upload files**, and upload the changed root files plus `vercel.json` and `sitemap.xml`. Commit to the production branch.
3. Vercel builds in about 1 minute. Then run the check in section 5.

## 5. Post-deploy check (about 2 minutes)

- Open the home page and one inner page in light and dark mode, and confirm they are styled.
- Visit `/nope` and confirm the branded 404 page appears.
- Visit `/buying-process.html` and confirm it lands on For Business Owners.
- Open the browser DevTools console on the Submit page and start typing in a form. There should be no red "Content Security Policy" errors, and the hCaptcha box should appear.
- Send one test submission and confirm the email arrives.

## 6. Rollback (fastest first)

1. **Vercel Instant Rollback.** In Vercel, open Project → Deployments, choose the last good deployment, then **⋯ → Promote to Production**. This takes seconds, needs no code change, and is the safest option.
2. **Git revert.** On GitHub, open the bad commit and revert it. Vercel then redeploys the previous state.
3. **Re-upload a saved release zip.** Each release is also saved in your local folder under `Claude outputs`.

Do not delete deployments in Vercel. They are your rollback points.

## 7. Backups

| What | Where it lives | Backup |
|---|---|---|
| Site source and build scripts | GitHub repo | Keep the release zips in your local folder. You can also download the repo as a ZIP (Code → Download ZIP) after each release. |
| Deployed versions | Vercel deployment history | Kept automatically. Do not delete them. |
| DNS records | Cloudflare | Export a zone file: DNS → Records → Export. Keep it with the release zips. |
| Form submissions | Your inbox (Web3Forms keeps them 30 days on the free plan) | File or label submission emails in Google Workspace. |
| Account access | Password manager + 2FA recovery codes | Store the recovery codes for GitHub, Vercel, Cloudflare, and Google offline. |

## 8. Known limitations

- **No server-side validation or rate limiting of our own.** The forms post directly to Web3Forms, so field rules are enforced only in the browser. Server-side protection comes from Web3Forms (hCaptcha verification once enabled, their spam filtering, and their limits). Closing this gap requires a server function, such as a Vercel Function with Cloudflare Turnstile and an email API.
- **The Web3Forms access key is visible in the page source.** This is by design: it can only send email to your inbox. The residual risk is spam, which hCaptcha enforcement mitigates. If abuse ever occurs, rotate the key in the Web3Forms dashboard, update `WEB3FORMS_KEY` in `src/pages.py`, and rebuild.
- **The CSP allows hCaptcha's domains.** hCaptcha is a trusted, widely used third party, but it still runs its code on the form pages.
- **Web3Forms free-plan limits:** 250 submissions per month and 30-day storage.
