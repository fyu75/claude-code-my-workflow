---
name: proofread
description: Read-only proofreading pass over the manuscript (`paper/main.tex` and `paper/sections/*.tex`). Checks grammar, typos, overflow, terminology consistency, and academic writing quality; produces a report without editing. Use when user says "proofread", "check for typos", "look for grammar issues", "copy-edit this", "any writing errors?", or before sharing the paper with co-authors.
argument-hint: "[filename or 'all']"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Proofread Manuscript Files

Run the mandatory proofreading protocol on manuscript files. This produces a report of all issues found WITHOUT editing any source files.

## Steps

1. **Identify files to review:**
   - If `$ARGUMENTS` is a specific filename: review that file only
   - If `$ARGUMENTS` is "all": review `paper/main.tex` and every file in `paper/sections/*.tex`

2. **For each file, launch the proofreader agent** that checks for:

   **GRAMMAR:** Subject-verb agreement, articles (a/an/the), prepositions, tense consistency
   **TYPOS:** Misspellings, search-and-replace artifacts, duplicated words
   **OVERFLOW:** Overfull hbox warnings from the latest `paper/main.log`
   **CONSISTENCY:** Citation format (`\citet` vs `\citep`), notation, terminology (e.g., "data center" vs "DC")
   **ACADEMIC QUALITY:** Informal language, hedging without commitment, missing antecedents, awkward constructions

3. **Produce a detailed report** for each file listing every finding with:
   - Location (line number or `\label{}`)
   - Current text (what's wrong)
   - Proposed fix (what it should be)
   - Category and severity

4. **Save each report** to `quality_reports/`:
   - `quality_reports/[FILENAME]_report.md` (e.g., `quality_reports/main_report.md`, `quality_reports/intro_report.md`)

5. **IMPORTANT: Do NOT edit any source files.**
   Only produce the report. Fixes are applied separately after user review.

6. **Present summary** to the user:
   - Total issues found per file
   - Breakdown by category
   - Most critical issues highlighted
