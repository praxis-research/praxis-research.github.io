# ci/

`deploy.yml` is the GitHub Actions workflow that builds the site and publishes
it to GitHub Pages on every push to `main`. It lives here rather than in
`.github/workflows/` only because the token used to create this repo lacked the
`workflow` scope, and GitHub refuses such pushes.

To turn it on, either:

```bash
gh auth refresh -h github.com -s workflow      # grant the scope, once
git mv ci/deploy.yml .github/workflows/deploy.yml
git commit -m "Enable Pages deploy workflow" && git push
```

or paste the file into `.github/workflows/deploy.yml` through the GitHub web
editor, which is not subject to the scope check.

Until then, `npm run deploy` publishes the built site to the `gh-pages` branch
from your machine.
