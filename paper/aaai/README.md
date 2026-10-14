# OneOcean anonymous AAAI submission

This package contains the anonymous main manuscript and a separate supplementary appendix for Paper ID **6895**.

The main manuscript has seven content pages, followed by references beginning on page eight. The appendix contains the full task definitions, models, evaluation protocol, and supplementary experiments.

## Build

Requirements: Python 3 with PyMuPDF (`python3 -m pip install pymupdf`), PDFLaTeX, BibTeX, and latexmk. A TeX Live installation must provide the packages used by the supplied AAAI style, including `newtxtext`, and the manuscript packages.

```bash
python3 build.py
```

The script compiles the appendix first, then the main manuscript so that appendix cross-references resolve. It produces:

- `OneOcean_AAAI_Anonymous.pdf`: main manuscript and references.
- `OneOcean_AAAI_Appendix.pdf`: separate supplementary appendix.
- `OneOcean_AAAI_source.zip`: self-contained source, used figures, bibliography files, and build instructions.

To rebuild from the ZIP, extract it into an empty directory and run the same command.

For a manual build, run these commands from `source/`:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error appendix.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The manual commands produce `source/appendix.pdf` and `source/main.pdf`. Run `build.py` to produce the files listed above.

## Resources

- [Project](https://anonymous-2026.github.io/OneOcean/)
- [Code](https://github.com/anonymous-2026/OneOcean)
- [Interactive demo](https://anonymous-2026.github.io/OneOcean/demo/)
