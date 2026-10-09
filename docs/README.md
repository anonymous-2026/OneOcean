# Web Documentation

`docs/` contains the public website sources served by GitHub Pages. The platform explorer loads a pre-exported static dataset sample and filters it in the browser.

- `index.html`: primary project website for the paper and public release.
- `platform/index.html`: platform/data usage page with a static GitHub-Pages explorer for a lightweight current-field subset.
- `demo/`: integrated interactive demo, task demos, and six-task overview.
- `oneocean_appendix.pdf`: standalone copy of the appendix, retained for existing links.
- `oneocean_paper.pdf`: anonymous AAAI manuscript with seven content pages and references beginning on page eight.
- `OneOcean_AAAI_source.zip`: source and build script for the anonymous manuscript and separate appendix.
- `static/`: website assets (logo, copied paper figures, demo media, CSS, JavaScript, and the exported web-data subset under `static/data/`).

Local preview:

```bash
cd docs
python -m http.server 8000
```

To rebuild the platform explorer dataset from a local `combined_environment.nc`:

```bash
python tools/export_platform_web_data.py \
  --input /path/to/combined_environment.nc
```

## Deployment

The repository is published at https://anonymous-2026.github.io/OneOcean/.
The project page, platform guide (`platform/`), and demo (`demo/`) are deployed together from `docs/` by GitHub Pages on pushes to `main`.
In repository Settings → Pages, select **Deploy from a branch**, branch **main**, folder **/docs**.
The paper PDF contains the anonymous AAAI manuscript. The separate appendix includes the full task definitions, models, evaluation protocol, and supplementary experiments. Maintained source and build instructions are in `paper/aaai/`.

Published entry points:

- [Project website](https://anonymous-2026.github.io/OneOcean/)
- [Platform guide](https://anonymous-2026.github.io/OneOcean/platform/)
- [Interactive demo](https://anonymous-2026.github.io/OneOcean/demo/)
- [Task demos](https://anonymous-2026.github.io/OneOcean/demo/tasks.html)
- [Paper](https://anonymous-2026.github.io/OneOcean/oneocean_paper.pdf)
- [Supplementary appendix](https://anonymous-2026.github.io/OneOcean/oneocean_appendix.pdf)

The demo, screenshots, and task pages are maintained directly in `docs/demo/` as part of this repository.
