# OneOcean anonymous AAAI submission

This package contains the anonymous main manuscript and a separate supplementary appendix for Paper ID **6895**.

The main manuscript has seven content pages, followed by references beginning on page eight. The appendix contains the full task definitions, models, evaluation protocol, and supplementary experiments.

## Build

Requirements: Python 3 with PyMuPDF (`python3 -m pip install pymupdf`), PDFLaTeX, BibTeX, and latexmk. A TeX Live installation must provide the packages used by the supplied AAAI style, including `newtxtext`, and the manuscript packages.

```bash
python3 build.py
```

The script compiles the appendix first, then the main manuscript so that appendix cross-references resolve. It verifies the page boundary, checks for undefined references and overfull boxes, checks anonymous metadata and links, and produces:

- `OneOcean_AAAI_Anonymous.pdf`: main manuscript and references.
- `OneOcean_AAAI_Appendix.pdf`: separate supplementary appendix.
- `OneOcean_AAAI_source.zip`: self-contained source, used figures, bibliography files, and build instructions.
- `SOURCE_MANIFEST.json`: file hashes, page counts, entrypoints, and verification results.

To rebuild from the ZIP, extract it into an empty directory and run the same command. Generated logs and auxiliary files are excluded from the archive. The two `.bbl` files are included for reproducible bibliography typesetting.

For a manual build, run these commands from `source/`:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error appendix.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The manual commands produce `source/appendix.pdf` and `source/main.pdf`. Run `build.py` for verified deliverables and anonymous PDF metadata.

## Resources

- [Project](https://anonymous-2026.github.io/OneOcean/)
- [Code](https://github.com/anonymous-2026/OneOcean)
- [Interactive demo](https://anonymous-2026.github.io/OneOcean/demo/)
