# Deployment

**Host:** GitHub Pages, built by GitHub Actions from `main`.
**Repo:** `praxis-research/praxis-research.github.io`
**DNS:** Cloudflare (nameservers `ajay.ns.cloudflare.com`, `collins.ns.cloudflare.com`).

Push to `main` → Actions runs `npm ci && npm run check` → `dist/` is published.
A failed link check blocks the deploy. Nothing else to operate.

## Staging vs production

Until the domain is cut over, the site is live at
<https://praxis-research.github.io/>. That URL is byte-identical to what
production will serve, because the repo is named `<org>.github.io` and every
path is root-relative.

## Cutting the domain over from Notion + super.so

Do these in order. Steps 1–2 are safe to do in advance; the site stays on
super.so until step 3.

1. **Tell GitHub the domain is ours.** Repo → Settings → Pages → Custom domain
   → `praxis-research.org` → Save. GitHub writes a `CNAME` file; keep it, or
   commit `static/CNAME` containing `praxis-research.org` (`static/` is copied
   to the site root at build time).

2. **Verify the domain** (optional but recommended — it stops anyone else
   claiming it). Org → Settings → Pages → "Add a domain", then add the
   `_github-pages-challenge-praxis-research` TXT record it gives you in
   Cloudflare.

3. **Repoint DNS in Cloudflare.** Replace the existing records for the apex and
   `www` with:

   | Type | Name | Value | Proxy |
   | --- | --- | --- | --- |
   | A | `@` | `185.199.108.153` | DNS only (grey cloud) |
   | A | `@` | `185.199.109.153` | DNS only |
   | A | `@` | `185.199.110.153` | DNS only |
   | A | `@` | `185.199.111.153` | DNS only |
   | CNAME | `www` | `praxis-research.github.io` | DNS only |

   Set the proxy to **DNS only** at first. Cloudflare's orange-cloud proxy in
   front of GitHub Pages breaks GitHub's certificate issuance. Once GitHub shows
   a valid certificate you can turn the proxy back on with SSL mode "Full
   (strict)".

4. **Wait for the certificate.** Settings → Pages will say "Enforce HTTPS" once
   Let's Encrypt has issued. It usually takes a few minutes. Then tick it.

5. **Check the old URLs still resolve.** These paths are preserved exactly, so
   existing links and any search index keep working:
   `/`, `/people/`, `/sprints/`, `/sprints/unsupervised-elicitation/`,
   `/sprints/persona-elicitation/`, `/blog/`,
   `/blog/mitigating-collusive-self-preference/`.

6. **Cancel super.so** once you are happy. Notion can stay as a scratchpad; it
   is no longer load-bearing for the site.

## Rolling back

Point the Cloudflare records back at super.so. Nothing in this repo needs to
change.
