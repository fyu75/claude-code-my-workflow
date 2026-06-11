---
name: compile-latex
description: Compile the dc-muni paper with XeLaTeX (3 passes + bibtex). Use when user says "compile", "build the paper", "rebuild the PDF", "run latex", "render the tex", or asks why `paper/main.tex` isn't producing a PDF. Operates on `paper/main.tex`.
argument-hint: "[optional: filename without .tex extension; defaults to main]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Compile LaTeX Paper

Compile the project paper using XeLaTeX with full citation resolution.

## Steps

1. **Default to `paper/main.tex`** (the project paper). If `$ARGUMENTS` is supplied, treat it as the filename without `.tex` (e.g., `main`).

2. **Compile with 3-pass sequence** from the repo root:

```bash
cd paper && \
  xelatex -interaction=nonstopmode ${ARGUMENTS:-main}.tex && \
  bibtex ${ARGUMENTS:-main} && \
  xelatex -interaction=nonstopmode ${ARGUMENTS:-main}.tex && \
  xelatex -interaction=nonstopmode ${ARGUMENTS:-main}.tex
```

**Alternative (latexmk):**

```bash
cd paper && latexmk -xelatex -interaction=nonstopmode ${ARGUMENTS:-main}.tex
```

3. **Check for warnings:**
   - Grep output for `Overfull \\hbox` warnings
   - Grep for `undefined citations` or `Label(s) may have changed`
   - Grep for `LaTeX Warning: Citation .* undefined`
   - Report any issues found

4. **Open the PDF** for visual verification:

```bash
open paper/${ARGUMENTS:-main}.pdf          # macOS
# xdg-open paper/${ARGUMENTS:-main}.pdf    # Linux
```

5. **Report results:**
   - Compilation success/failure
   - Number of overfull hbox warnings
   - Any undefined citations
   - PDF page count

## Why 3 passes?

1. First xelatex: Creates `.aux` file with citation keys
2. bibtex: Reads `.aux`, generates `.bbl` with formatted references from `paper/refs.bib`
3. Second xelatex: Incorporates bibliography
4. Third xelatex: Resolves all cross-references with final page numbers

## Important

- **Always use XeLaTeX**, never pdflatex (the paper uses Unicode characters and modern font handling).
- **No `TEXINPUTS=../Preambles`** — that was the Beamer-template pattern; `paper/main.tex` is self-contained and uses standard `article` class.
- **`paper/refs.bib`** is the authoritative bibliography (INV-5). All `\cite{}` keys must resolve there.
- **Tables and figures** referenced in `main.tex` come from `../output/` via `\input{}` and `\includegraphics{}`. If a `\input{}` fails, run the upstream Stata script first.
