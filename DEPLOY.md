# Deployment

**Repo:** `praxis-research/praxis-research.github.io` (public)
**Host:** GitHub Pages, built by `.github/workflows/deploy.yml`
**DNS:** Cloudflare (nameservers `ajay.ns.cloudflare.com`, `collins.ns.cloudflare.com`)

**Push to `main` and the site rebuilds and deploys.** A failed link check blocks
the deploy. There is nothing else to operate.

## Why the repo is named that

`<org>.github.io` is served at the root of `https://praxis-research.github.io/`,
so every path in the built site — which is root-relative — resolves both there
and on the custom domain. A repo under any other name is served at `/<repo>/`,
and the stylesheet 404s. The repo is public because GitHub Pages on a free-plan
org only serves public repos; it holds no secrets.

## Without Actions

`npm run deploy` builds and force-pushes `dist/` to a `gh-pages` branch from
your machine, needing no CI. If you ever want that instead, point Pages at the
branch:

```bash
gh api -X POST repos/praxis-research/praxis-research.github.io/pages \
  -f 'source[branch]=gh-pages' -f 'source[path]=/'
npm run deploy
```

The cost is that every content edit then needs a local checkout and a build.
With Actions you can edit a markdown file in the GitHub web editor and the site
updates itself.

## Previewing

`https://praxis-research.github.io/` redirects to `praxis-research.org`, because
the custom domain is set — that is how GitHub Pages behaves. Use `npm run serve`
to look at a build locally before pushing it.

To check what production is really serving, bypass your own DNS cache — a stale
local resolver will happily show you the wrong origin and cost you an hour:

```bash
curl -sI --resolve praxis-research.org:443:104.21.30.94 https://praxis-research.org/
```

## The domain (done — 2026-08-20)

`praxis-research.org` now serves this site. The path is:

    visitor -> Cloudflare edge (terminates TLS) -> GitHub Pages (origin)

Cloudflare's records for the apex and `www` are **proxied**, pointing at
GitHub's Pages addresses. `www` 301-redirects to the apex.

### Why proxied, and not DNS-only

The plan was DNS-only, letting GitHub issue its own certificate. That was wrong
for this domain: it sends **HSTS with a two-year max-age**. Between DNS moving
and GitHub issuing, HTTPS presents no valid certificate — and with HSTS cached,
browsers *refuse the connection* instead of offering a click-through. In
practice GitHub had not even begun provisioning after five minutes
(`https_certificate.state` stayed `none`), so the gap was not going to be brief.

Proxying removes the gap: Cloudflare's edge certificate already covers
`praxis-research.org` and `*.praxis-research.org`, so TLS never breaks.

Consequences of that choice, all of which are fine but none of which are
obvious later:

- **GitHub will never issue its own certificate** while the records are proxied,
  and `https_enforced` cannot be turned on. That is expected, not a fault.
- **Do not set the zone SSL mode to "Full (strict)".** GitHub serves Cloudflare
  a `*.github.io` certificate, which strict mode rejects with a 526.
- **HSTS is no longer being sent.** It came from the super.so origin; GitHub does
  not send it. Browsers that saw the old header still enforce it for two years,
  but new visitors get none. To restore it, turn on HSTS in Cloudflare under
  SSL/TLS → Edge Certificates. Do that only once you are confident you will not
  need to serve this domain over plain HTTP.
- **`robots.txt` is not served verbatim.** Cloudflare prepends a managed
  content-signals block that disallows `GPTBot` and `meta-externalagent`. Our
  own directives and the sitemap line survive underneath it. Toggle it in the
  Cloudflare dashboard if you want the file served as written.

### Going DNS-only later, if you want GitHub to hold the certificate

Only worth doing in a quiet window, because it reopens the HSTS gap:
set the apex and `www` records to DNS-only, wait for
`https_certificate.state` to become `authorized`, then

```bash
gh api -X PUT repos/praxis-research/praxis-research.github.io/pages -F https_enforced=true
```

If the certificate has not appeared within about fifteen minutes, remove and
re-add the custom domain in Settings → Pages to force a fresh request.

### URLs

`/`, `/people/` and `/blog/` carried over from the super.so site unchanged.
Four paths are deliberately gone and now return the 404 page: `/sprints/`,
`/sprints/unsupervised-elicitation/`, `/sprints/persona-elicitation/` and
`/blog/mitigating-collusive-self-preference/`. Add a Cloudflare redirect rule if
any of them turns out to have been shared.

Super.so can be cancelled — it is no longer in the path.

## Rolling back

`dns-backup-praxis-research.org.json` (written by `bin/cf-cutover.sh` before it
deleted anything) holds the two records that pointed at super.so:

    A     praxis-research.org      -> 76.76.21.21     proxied
    CNAME www.praxis-research.org  -> cname.super.so  proxied

Recreate those two, delete the GitHub A/AAAA/CNAME records, and the old site is
back. Nothing in this repo needs to change. Note that those targets are not
recoverable from public DNS, because the records were proxied — this backup is
the only copy.

To go back to serving on `praxis-research.github.io` as well, clear the custom
domain and delete `static/CNAME`.
