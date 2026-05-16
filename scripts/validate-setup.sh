#!/usr/bin/env bash
# =============================================================================
# validate-setup.sh — Verify all dependencies for the dc-muni workflow.
#
# Run this after cloning to confirm your environment is ready.
# Exits 0 if all required tools are found; non-zero otherwise.
# =============================================================================

set -uo pipefail

# ANSI colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

pass=0
warn=0
fail=0

echo ""
echo -e "${BOLD}Validating dc-muni workflow setup...${RESET}"
echo ""

check_required() {
    local name="$1"
    local cmd="$2"
    local install_url="$3"
    if command -v "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${RESET} $name found: $("$cmd" --version 2>&1 | head -n1)"
        pass=$((pass + 1))
    else
        echo -e "  ${RED}✗${RESET} $name NOT FOUND — install: ${install_url}"
        fail=$((fail + 1))
    fi
}

check_required_path() {
    # Variant for tools that don't live on PATH but at a known absolute path.
    local name="$1"
    local path="$2"
    local install_url="$3"
    if [ -x "$path" ]; then
        echo -e "  ${GREEN}✓${RESET} $name found at $path"
        pass=$((pass + 1))
    else
        echo -e "  ${RED}✗${RESET} $name NOT FOUND at $path — install: ${install_url}"
        fail=$((fail + 1))
    fi
}

check_optional() {
    local name="$1"
    local cmd="$2"
    local install_url="$3"
    if command -v "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${RESET} $name found: $("$cmd" --version 2>&1 | head -n1)"
        pass=$((pass + 1))
    else
        echo -e "  ${YELLOW}⚠${RESET} $name not found (optional) — install: ${install_url}"
        warn=$((warn + 1))
    fi
}

echo -e "${BOLD}Required tools:${RESET}"
check_required      "Claude Code"   "claude"   "https://claude.ai/install"
check_required      "XeLaTeX"       "xelatex"  "https://tug.org/texlive/ (or MacTeX: https://tug.org/mactex/)"
check_required      "git"           "git"      "https://git-scm.com/downloads"
check_required      "Python 3"      "python3"  "https://python.org (needed for hooks)"
check_required      "R"             "Rscript"  "https://www.r-project.org/"
check_required_path "Stata SE 19.0" "/Applications/Stata/StataSE.app/Contents/MacOS/StataSE" \
                    "Stata SE 19.0 (institutional license required); place at /Applications/Stata/"
echo ""

echo -e "${BOLD}Recommended tools:${RESET}"
check_optional "GitHub CLI"   "gh"       "https://cli.github.com/"
check_optional "pandoc"       "pandoc"   "https://pandoc.org/installing.html  (LaTeX → Word export)"
echo ""

echo -e "${BOLD}Git configuration:${RESET}"
if command -v git >/dev/null 2>&1; then
    git_name=$(git config user.name 2>/dev/null || true)
    git_email=$(git config user.email 2>/dev/null || true)
    if [ -n "$git_name" ] && [ -n "$git_email" ]; then
        echo -e "  ${GREEN}✓${RESET} git user: $git_name <$git_email>"
        pass=$((pass + 1))
    else
        echo -e "  ${YELLOW}⚠${RESET} git user.name / user.email not set"
        echo -e "    Run: git config --global user.name \"Your Name\""
        echo -e "    Run: git config --global user.email \"you@example.com\""
        warn=$((warn + 1))
    fi
else
    echo -e "  ${YELLOW}⚠${RESET} skipped — install git first (see required tools above)"
    warn=$((warn + 1))
fi
echo ""

echo -e "${BOLD}Claude Code hooks:${RESET}"
hook_dir="$(dirname "$0")/../.claude/hooks"
if [ -d "$hook_dir" ]; then
    non_exec=$(find "$hook_dir" -maxdepth 1 \( -name "*.py" -o -name "*.sh" \) ! -perm -u+x 2>/dev/null | wc -l | tr -d ' ')
    if [ "$non_exec" -eq 0 ]; then
        echo -e "  ${GREEN}✓${RESET} All hook scripts are executable"
        pass=$((pass + 1))
    else
        echo -e "  ${YELLOW}⚠${RESET} $non_exec hook script(s) not executable"
        echo -e "    Fix: chmod +x .claude/hooks/*.py .claude/hooks/*.sh"
        warn=$((warn + 1))
    fi
else
    echo -e "  ${YELLOW}⚠${RESET} .claude/hooks/ directory not found (are you in the project root?)"
    warn=$((warn + 1))
fi
echo ""

echo -e "${BOLD}Data symlink (data/raw):${RESET}"
data_raw="$(dirname "$0")/../data/raw"
if [ -L "$data_raw" ]; then
    if [ -d "$data_raw" ]; then
        target=$(readlink "$data_raw")
        echo -e "  ${GREEN}✓${RESET} data/raw symlink resolves to: $target"
        pass=$((pass + 1))
    else
        echo -e "  ${YELLOW}⚠${RESET} data/raw symlink exists but target is missing"
        echo -e "    Recreate: ln -sfn /Users/fangyu/claude/datacenter/raw data/raw"
        warn=$((warn + 1))
    fi
else
    echo -e "  ${YELLOW}⚠${RESET} data/raw symlink not present"
    echo -e "    Create:   ln -sfn /Users/fangyu/claude/datacenter/raw data/raw"
    echo -e "    (Each collaborator creates their own; not committed.)"
    warn=$((warn + 1))
fi
echo ""

echo -e "${BOLD}Summary:${RESET} ${GREEN}${pass} passed${RESET}, ${YELLOW}${warn} warnings${RESET}, ${RED}${fail} failed${RESET}"
echo ""

# Status flags for the next-steps section
has_claude="false";  command -v claude  >/dev/null 2>&1 && has_claude="true"
has_xelatex="false"; command -v xelatex >/dev/null 2>&1 && has_xelatex="true"
has_r="false";       command -v Rscript >/dev/null 2>&1 && has_r="true"
has_stata="false";   [ -x "/Applications/Stata/StataSE.app/Contents/MacOS/StataSE" ] && has_stata="true"

if [ "$fail" -gt 0 ]; then
    echo -e "${RED}Some required tools are missing.${RESET}"
    echo ""
    echo -e "${BOLD}What you CAN do right now:${RESET}"
    if [ "$has_claude" = "true" ]; then
        echo "  - Open Claude Code:                      claude"
        echo ""
        echo "  ${BOLD}Inside Claude Code${RESET} (slash-commands, NOT shell commands):"
        if [ "$has_xelatex" = "true" ]; then
            echo "    /compile-latex           # compile paper/main.tex"
        fi
        if [ "$has_r" = "true" ]; then
            echo "    /data-analysis           # supplementary R analysis"
        fi
        if [ "$has_stata" != "true" ]; then
            echo ""
            echo "  (Stata pipeline disabled until Stata SE 19.0 is installed at the standard path.)"
        fi
        if [ "$has_xelatex" != "true" ]; then
            echo "  (Paper compile disabled until XeLaTeX is installed.)"
        fi
    else
        echo "  - Install Claude Code first: https://claude.ai/install"
    fi
    echo ""
    echo -e "${BOLD}Next:${RESET} install the missing required tool(s) above, then re-run this script."
    exit 1
fi

echo -e "${GREEN}Setup looks good!${RESET} Next steps:"
echo "  1. Open Claude Code in this directory:  claude"
echo "  2. Create the data symlink (one-time):  ln -sfn /Users/fangyu/claude/datacenter/raw data/raw"
echo "  3. Run the Stata pipeline:              /Applications/Stata/StataSE.app/Contents/MacOS/StataSE -e do scripts/stata/00_run_all.do"
echo "  4. Compile the paper skeleton:          cd paper && xelatex main.tex && bibtex main && xelatex main.tex && xelatex main.tex"
echo ""
exit 0
