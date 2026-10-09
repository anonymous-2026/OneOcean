#!/usr/bin/env python3
"""Build and verify the anonymous AAAI paper and separate appendix."""

from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile

import fitz


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
BUILD = ROOT / ".build"
ANONYMOUS_URLS = {
    "project": "https://anonymous-2026.github.io/OneOcean/",
    "code": "https://github.com/anonymous-2026/OneOcean",
    "demo": "https://anonymous-2026.github.io/OneOcean/demo/",
}
# These patterns reject author metadata and machine paths in distributable files.
# Bibliographic authors and third-party project links remain valid citations.
PRIVATE_PATTERNS = (
    r"https?://(?!anonymous-2026\.)[^/\s]+\.github\.io/OneOcean",
    r"https?://github\.com/(?!anonymous-2026/)[^/\s]+/OneOcean",
    r"(?<![:/\w])/(?:data|Users)/(?:[^\s/]+/){2}",
    r"/home/[^\s/]+/",
    r"https?://anonymous-2026\.github\.io/demo(?:/|\b)",
)
BAD_LOG = re.compile(
    r"^.*(?:Overfull \\[hv]box|Float too large|undefined references|"
    r"undefined citations|Citation .* undefined|Reference .* undefined|"
    r"multiply defined|destination with the same identifier|LaTeX Error|"
    r"Emergency stop|Fatal error).*$",
    re.MULTILINE,
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_anonymous(text, label):
    for pattern in PRIVATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raise RuntimeError(f"Identity or local-path leak in {label}: {match.group(0)!r}")


def compile_document(stem):
    command = [
        "latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
        f"{stem}.tex",
    ]
    result = subprocess.run(command, cwd=SOURCE, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    (BUILD / f"{stem}-build.log").write_text(result.stdout)
    if result.returncode:
        raise RuntimeError(f"Compilation failed for {stem}; see .build/{stem}-build.log")
    log = (SOURCE / f"{stem}.log").read_text(errors="replace")
    problems = BAD_LOG.findall(log)
    if problems:
        raise RuntimeError(f"Unresolved typesetting problems in {stem}:\n" + "\n".join(problems))


def source_files():
    """Follow the two entrypoints so unused template material stays out of the ZIP."""
    selected = set()
    pending = [SOURCE / "main.tex", SOURCE / "appendix.tex"]
    while pending:
        path = pending.pop()
        if path in selected:
            continue
        if not path.is_file():
            raise RuntimeError(f"Missing source: {path.relative_to(SOURCE)}")
        selected.add(path)
        text = path.read_text()
        for name in re.findall(r"\\(?:input|include)\{([^}]+)\}", text):
            include = SOURCE / name
            if not include.suffix:
                include = include.with_suffix(".tex")
            pending.append(include)
        for name in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
            image = SOURCE / name
            if not image.suffix:
                image = next((image.with_suffix(ext) for ext in (".pdf", ".png", ".jpg")
                              if image.with_suffix(ext).is_file()), image)
            if not image.is_file():
                raise RuntimeError(f"Missing figure: {name}")
            selected.add(image)
    for name in ("references.bib", "aaai2027.sty", "aaai2027.bst", "main.bbl", "appendix.bbl"):
        selected.add(SOURCE / name)
    return sorted(selected)


def check_source_files(files):
    for path in files:
        if path.suffix == ".pdf":
            check_pdf_identity(path)
        elif path.suffix in {".tex", ".bib", ".bbl", ".sty", ".bst"}:
            require_anonymous(path.read_text(errors="replace"), path.relative_to(SOURCE))
    frontmatter = (SOURCE / "main.tex").read_text()
    if "6895" not in frontmatter or "Anonymous submission" not in frontmatter:
        raise RuntimeError("Main front matter must retain anonymous authors and Paper ID 6895")
    for url in ANONYMOUS_URLS.values():
        if url not in frontmatter:
            raise RuntimeError(f"Missing anonymous resource URL: {url}")
    with fitz.open(SOURCE / "figures/abstract.pdf") as doc:
        links = [link.get("uri") for page in doc for link in page.get_links()]
        if ANONYMOUS_URLS["demo"] not in links:
            raise RuntimeError("Figure 1 must link to the integrated anonymous demo")


def check_pdf_identity(path):
    with fitz.open(path) as doc:
        author = doc.metadata.get("author", "").strip().lower()
        if author not in {"", "anonymous submission"}:
            raise RuntimeError(f"Non-anonymous author metadata in {path.name}")
        require_anonymous(json.dumps(doc.metadata), path.name + " metadata")
        require_anonymous(doc.get_xml_metadata(), path.name + " XML metadata")
        for page in doc:
            require_anonymous(page.get_text(), path.name + " text")
            for link in page.get_links():
                require_anonymous(link.get("uri", ""), path.name + " link")


def check_pagination():
    with fitz.open(SOURCE / "main.pdf") as doc:
        texts = [page.get_text() for page in doc]
        reference_pages = [i + 1 for i, text in enumerate(texts)
                           if any(line.strip() == "References" for line in text.splitlines())]
        if reference_pages != [8]:
            raise RuntimeError(f"References must start on page 8; found {reference_pages}")
        if len(doc) not in (8, 9):
            raise RuntimeError(f"Main paper must have 8 or 9 total pages; found {len(doc)}")
        if "Conclusion" not in "\n".join(texts[:7]):
            raise RuntimeError("The conclusion must finish within the seven content pages")
        content_headings = ("Introduction", "Related Work", "OneOcean Suite", "Experiments",
                            "Discussion", "Conclusion")
        for index, page in enumerate(doc):
            if len(texts[index].strip()) < 100:
                raise RuntimeError(f"Near-empty page {index + 1} is not permitted")
            if "??" in texts[index]:
                raise RuntimeError(f"Unresolved cross-reference marker on page {index + 1}")
            if index >= 7:
                if page.get_image_info() or page.get_drawings():
                    raise RuntimeError(f"Non-bibliography graphic on reference page {index + 1}")
                if any(line.strip() in content_headings for line in texts[index].splitlines()):
                    raise RuntimeError(f"Content heading on reference page {index + 1}")
                if re.search(r"(?m)^(?:Figure|Table)\s+\d+\s*:", texts[index]):
                    raise RuntimeError(f"Content float on reference page {index + 1}")
        main_pages = len(doc)
    with fitz.open(SOURCE / "appendix.pdf") as doc:
        text = "\n".join(page.get_text() for page in doc)
        if "??" in text:
            raise RuntimeError("Unresolved appendix cross-reference marker")
        for heading in ("Ocean Dataset and Validation", "Task Definitions",
                        "Implementation Defaults, Pollution, and ROS 2",
                        "Metrics and Reproducibility Protocol",
                        "Additional Core-Backend Diagnostics", "Additional External-Backend Diagnostics"):
            if re.sub(r"\s+", " ", heading) not in re.sub(r"\s+", " ", text):
                raise RuntimeError(f"Missing appendix section: {heading}")
        appendix_pages = len(doc)
    return {"content_pages": 7, "references_start_page": 8,
            "main_total_pages": main_pages, "appendix_pages": appendix_pages}


def write_anonymous_pdf(stem, destination, title):
    with fitz.open(SOURCE / f"{stem}.pdf") as doc:
        doc.set_metadata({"title": title, "author": "Anonymous submission",
                          "subject": "AAAI-27 Paper 6895", "keywords": "marine robotics, benchmark",
                          "creator": "LaTeX", "producer": "pdfTeX",
                          "creationDate": "", "modDate": "", "trapped": ""})
        doc.del_xml_metadata()
        doc.save(destination, garbage=4, deflate=True)
    check_pdf_identity(destination)


def main():
    BUILD.mkdir(exist_ok=True)
    # Appendix labels must exist before xr imports them into the main manuscript.
    compile_document("appendix")
    compile_document("main")
    pages = check_pagination()
    files = source_files()
    check_source_files(files)
    main_pdf = ROOT / "OneOcean_AAAI_Anonymous.pdf"
    appendix_pdf = ROOT / "OneOcean_AAAI_Appendix.pdf"
    write_anonymous_pdf("main", main_pdf, "One Ocean, Many Tasks: Anonymous AAAI Submission")
    write_anonymous_pdf("appendix", appendix_pdf, "One Ocean, Many Tasks: Supplementary Appendix")
    archive = ROOT / "OneOcean_AAAI_source.zip"
    package_files = [ROOT / "build.py", ROOT / "README.md", *files]
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in package_files:
            bundle.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as bundle:
        for name in bundle.namelist():
            if name.endswith((".log", ".aux", ".fls", ".fdb_latexmk", ".blg")):
                raise RuntimeError(f"Build artifact entered source archive: {name}")
            if Path(name).name in {"main.pdf", "appendix.pdf", "BASELINE.json"}:
                raise RuntimeError(f"Excluded file entered source archive: {name}")
    manifest = {
        "schema_version": 1,
        "paper_id": "6895",
        "entrypoints": {"main": "source/main.tex", "appendix": "source/appendix.tex"},
        "compile_order": ["appendix", "main"],
        "compiler": "pdflatex",
        "anonymous_urls": ANONYMOUS_URLS,
        "pagination": pages,
        "verification": {"typesetting_log_clean": True, "cross_references_resolved": True,
                         "reference_pages_exclusive": True, "anonymous_identity_check": True},
        "source_files": {path.relative_to(ROOT).as_posix(): sha256(path) for path in package_files},
        "deliverables": {path.name: sha256(path) for path in (main_pdf, appendix_pdf, archive)},
    }
    (ROOT / "SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Verified {pages['main_total_pages']}-page main paper: 7 content pages, references from page 8.")
    print(f"Verified separate {pages['appendix_pages']}-page appendix and anonymous source archive.")


if __name__ == "__main__":
    main()
