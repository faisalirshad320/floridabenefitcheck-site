# floridabenefitcheck.com — deploy root

Static site served from the Cloudways app web root (`public_html`). Every file in this branch is public.

- `main` — the built site (this branch). Cloudways pulls this branch.
- `source` — the build scripts (`build/`). Run `python3 build/build_all.py` to regenerate `dist/`.

Single source of truth for freshness: `UPDATED_*` constants in `build/lib.py`. Benefit constants: `build/fbc.js` (engine) and `build/pages.py`.
