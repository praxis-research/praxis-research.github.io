# Deployment

**Repo:** `praxis-research/website` (rename to `praxis-research.github.io` — see below)
**Host:** GitHub Pages
**DNS:** Cloudflare (nameservers `ajay.ns.cloudflare.com`, `collins.ns.cloudflare.com`)

## One-time setup

GitHub Pages on a free-plan org only serves **public** repos, so the repo has to
be public. The site content is already public; the repo holds no secrets.

```bash
# 1. Make it public, and rename it so Pages serves from the domain root.
#    (GitHub redirects the old name, so nothing breaks.)
gh api -X PATCH repos/praxis-research/website -f private=false
gh api -X PATCH repos/praxis-research/website -f name=praxis-research.github.io
git remote set-url origin https://github.com/praxis-research/praxis-research.github.io.git

# 2. Turn on Pages, building from GitHub Actions.
gh api -X POST repos/praxis-research/praxis-research.github.io/pages \
  -f 'build_type=workflow'

# 3. Enable the deploy workflow (see ci/README.md).
gh auth refresh -h github.com -s workflow
mkdir -p .github/workflows
git mv ci/deploy.yml .github/workflows/deploy.yml
git commit -m "Enable Pages deploy workflow" && git push
```

The repo name matters: `<org>.github.io` is served at the root of
`https://praxis-research.github.io/`, so every path in the built site — which is
root-relative — resolves both there and on the custom domain. A repo under any
other name is served at `/<repo>/` and the stylesheet 404s.

After that, **push to `main` and the site rebuilds and deploys**. A failed link
check blocks the deploy. There is nothing else to operate.

### Without Actions

If you would rather not grant the `workflow` scope, `npm run deploy` builds and
force-pushes `dist/` to a `gh-pages` branch from your machine. Point Pages at
that branch instead:

```bash
gh api -X POST repos/praxis-research/praxis-research.github.io/pages \
  -f 'source[branch]=gh-pages' -f 'source[path]=/'
npm run deploy
```

The cost is that every content edit then needs a local checkout and a build;
with Actions you can edit a markdown file in the GitHub web editor and the site
updates itself.

## Staging

Before the domain moves, the site is live at
<https://praxis-research.github.io/>. That is byte-identical to what production
will serve.

## Cutting the domain over from Notion + super.so

Steps 1–2 are safe to do in advance; the live site stays on super.so until
step 3.

1. **Claim the domain.** Repo → Settings → Pages → Custom domain →
   `praxis-research.org` → Save. Or commit a file `static/CNAME` containing
   `praxis-research.org` (`static/` is copied to the site root at build time).
   Note that once this is set, `praxis-research.github.io` redirects to the
   custom domain, so do it when you are ready to point DNS.

2. **Verify the domain** (optional, recommended — it stops anyone else claiming
   it). Org → Settings → Pages → "Add a domain", then add the
   `_github-pages-challenge-praxis-research` TXT record it gives you in
   Cloudflare.

3. **Repoint DNS in Cloudflare.** Replace the current apex and `www` records
   with:

   | Type | Name | Value | Proxy |
   | --- | --- | --- | --- |
   | A | `@` | `185.199.108.153` | DNS only (grey cloud) |
   | A | `@` | `185.199.109.153` | DNS only |
   | A | `@` | `185.199.110.153` | DNS only |
   | A | `@` | `185.199.111.153` | DNS only |
   | CNAME | `www` | `praxis-research.github.io` | DNS only |

   Use **DNS only** at first — Cloudflare's orange-cloud proxy in front of
   GitHub Pages blocks GitHub's certificate issuance. Once GitHub shows a valid
   certificate you can re-enable the proxy with SSL mode "Full (strict)".

4. **Wait for the certificate**, then tick "Enforce HTTPS" in Settings → Pages.
   It usually takes a few minutes.

5. **Check the old URLs.** These paths are preserved exactly, so existing links
   and search results keep working:
   `/`, `/people/`, `/sprints/`, `/sprints/unsupervised-elicitation/`,
   `/sprints/persona-elicitation/`, `/blog/`,
   `/blog/mitigating-collusive-self-preference/`.

6. **Cancel super.so** once you are happy.

## Rolling back

Point the Cloudflare records back at super.so. Nothing in this repo changes.
