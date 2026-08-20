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

## Staging

`https://praxis-research.github.io/` now **redirects to praxis-research.org**,
because the custom domain is set — that is how GitHub Pages behaves, and it is
expected. To look at the built site before DNS moves, either run it locally with
`npm run serve`, or ask GitHub for it directly:

```bash
curl -sk --resolve praxis-research.org:443:185.199.108.153 https://praxis-research.org/
```

## Cutting the domain over from Notion + super.so

**Done already:** the repo publishes `CNAME`, and GitHub Pages has the custom
domain set to `praxis-research.org`. GitHub already serves this site for that
hostname — verified by forcing a request to a Pages IP with the right `Host`:

```bash
curl -sk --resolve praxis-research.org:443:185.199.108.153 https://praxis-research.org/
```

So the only thing left is DNS. Until it moves, the domain still resolves to
Cloudflare and super.so keeps serving; nothing is broken in the meantime, except
that `praxis-research.github.io` now redirects to `praxis-research.org`, so
staging is no longer separately viewable.

**Remaining: the DNS change.** Either run

```bash
export CLOUDFLARE_API_TOKEN=...   # Zone:DNS:Edit on praxis-research.org
bin/cf-cutover.sh                 # dry run — prints exactly what it will do
bin/cf-cutover.sh --apply
```

or make the same change by hand in the Cloudflare dashboard:

| Action | Type | Name | Value | Proxy |
| --- | --- | --- | --- | --- |
| delete | A / AAAA | `@` | the current Cloudflare-proxied records | |
| delete | A / AAAA | `www` | the current Cloudflare-proxied records | |
| add | A | `@` | `185.199.108.153` | DNS only (grey cloud) |
| add | A | `@` | `185.199.109.153` | DNS only |
| add | A | `@` | `185.199.110.153` | DNS only |
| add | A | `@` | `185.199.111.153` | DNS only |
| add | AAAA | `@` | `2606:50c0:8000::153` | DNS only |
| add | AAAA | `@` | `2606:50c0:8001::153` | DNS only |
| add | AAAA | `@` | `2606:50c0:8002::153` | DNS only |
| add | AAAA | `@` | `2606:50c0:8003::153` | DNS only |
| add | CNAME | `www` | `praxis-research.github.io` | DNS only |

Three things that will bite if missed:

- **The AAAA records matter.** The apex currently has IPv6 records pointing at
  Cloudflare. Replace the A records but leave those, and every IPv6 visitor
  still lands on super.so while IPv4 visitors see the new site.
- **Proxy off, at first.** Cloudflare's orange cloud in front of GitHub Pages
  blocks GitHub's certificate issuance. Once the certificate is valid you can
  turn the proxy back on with SSL mode "Full (strict)".
- **Do not touch MX or TXT.** Google Workspace mail runs on this domain
  (`aspmx.l.google.com` and friends), and the TXT records carry SPF and a
  Google site verification. The cutover only concerns A, AAAA and CNAME.

**After DNS moves**, wait for the certificate — usually a few minutes — then:

```bash
gh api repos/praxis-research/praxis-research.github.io/pages \
  --jq '{cname,cert:.https_certificate.state}'
gh api -X PUT repos/praxis-research/praxis-research.github.io/pages -F https_enforced=true
```

**Then check the URLs.** `/`, `/people/` and `/blog/` are preserved exactly.
Four paths from the super.so site are deliberately gone and will return the 404
page: `/sprints/`, `/sprints/unsupervised-elicitation/`,
`/sprints/persona-elicitation/` and `/blog/mitigating-collusive-self-preference/`.
If any was shared widely, add a Cloudflare redirect rule.

Finally, cancel super.so once you are happy.

## Rolling back

Restore the apex and `www` records from `dns-backup-praxis-research.org.json`,
which `bin/cf-cutover.sh` writes before it deletes anything. Those records are
Cloudflare-proxied, so their real targets are not visible in public DNS — the
backup is the only copy. Nothing in this repo needs to change.

To go back to serving on `praxis-research.github.io` as well, clear the custom
domain and delete `static/CNAME`.
