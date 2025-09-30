#!/bin/bash
# Function: Generate English/Chinese (en/zh_CN) documentation under docs/source/build
# Output Paths:
#   - Translation templates: source/build/gettext
#   - English documentation: source/build/html/en
#   - Chinese documentation: source/build/html/zh_CN

# ========================== 1. Core Path Configuration ===========================
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
SOURCE_DIR="$SCRIPT_DIR/source"  # Source directory: docs/source
BUILDDIR="$SOURCE_DIR/build"     # Output root: docs/source/build
POT_DIR="$BUILDDIR/gettext"      # Translation templates
HTML_ROOT="$BUILDDIR/html"       # HTML output root
LOCALE_DIR="$SOURCE_DIR/locale"  # Translation files (.po)
TRANSLATOR_SCRIPT="$SOURCE_DIR/translator.py"  # Translation script path
LANGUAGES=("zh_CN" "en")         # Supported languages

# ========================== 2. Utility Functions ===========================
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ Error: Command '$1' not found. Install via: pip3 install sphinx sphinx-intl"
        exit 1
    fi
}

check_path() {
    if [ ! -e "$1" ]; then
        echo "❌ Error: Path '$1' does not exist. Check project structure!"
        exit 1
    fi
}

clean_old_doc() {
    local lang=$1
    local doc_path="${HTML_ROOT}/${lang}"
    if [ -d "$doc_path" ]; then
        echo "🗑️ Cleaning old ${lang} documentation: ${doc_path}"
        rm -rf "$doc_path"
    fi
}

# ========================== 3. Pre-checks (Optimized I/O) ===========================
echo "🔍 Checking environment and dependencies..."
# Check core commands
check_command "sphinx-build"
check_command "sphinx-intl"
check_command "python3"

# Batch check required paths (reduce I/O)
REQUIRED_PATHS=("$SOURCE_DIR" "$SOURCE_DIR/conf.py" "$TRANSLATOR_SCRIPT")
for path in "${REQUIRED_PATHS[@]}"; do
    check_path "$path"
done

# Merge directory creation (reduce I/O)
mkdir -p "$POT_DIR" "$HTML_ROOT" || { echo "❌ Error: Failed to create output directories"; exit 1; }
echo "✅ Environment checks passed! Output root: ${BUILDDIR}"

# ========================== 4. Extract Translation Templates ===========================
echo -e "\n📝 Extracting translation templates (output to ${POT_DIR})..."
sphinx-build -b gettext "$SOURCE_DIR" "$POT_DIR"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to extract translation templates. Check .rst syntax!"
    exit 1
fi
echo "✅ Translation templates extracted: ${POT_DIR}"

# ========================== 5. Generate Translations (Optimized for Speed) ===========================
echo -e "\n🏗️ Starting translation generation (output to ${HTML_ROOT})..."
for lang in "${LANGUAGES[@]}"; do
    lang_name=$( [ "$lang" = "en" ] && echo "English" || echo "Chinese" )
    current_doc_path="${HTML_ROOT}/${lang}"

    echo -e "\n====================================================================="
    echo "🌐 Processing [${lang_name}] (Final path: ${current_doc_path})"
    echo "====================================================================="

    echo -e "\n1/4 🗑️ Cleaning old documentation"
    clean_old_doc "$lang"

    echo -e "\n2/4 🔄 Updating ${lang_name} translation files"
    sphinx-intl update -p "$POT_DIR" -l "$lang" -d "$LOCALE_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to update ${lang_name} translation files!"
        exit 1
    fi
    echo "✅ ${lang_name} translation files updated: ${LOCALE_DIR}/${lang}/LC_MESSAGES/"

    echo -e "\n3/4 🤖 Auto-translating ${lang_name} content"
    # RTD-specific optimizations: larger batches, no backups, minimal logs
    if [ "$READTHEDOCS" = "True" ]; then
        python3 "$TRANSLATOR_SCRIPT" \
            --locale-dir "$LOCALE_DIR" \
            --target-langs "$lang" \
            --batch-size 50 \
            --max-chars 12000 \
            --sleep 0.3 \
            --no-verbose \
            --no-backup
    else
        # Local mode: smaller batches, backups, detailed logs
        python3 "$TRANSLATOR_SCRIPT" \
            --locale-dir "$LOCALE_DIR" \
            --target-langs "$lang" \
            --batch-size 30 \
            --max-chars 8000 \
            --sleep 1.0 \
            --verbose
    fi

    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to auto-translate ${lang_name} content!"
        exit 1
    fi
    echo "✅ ${lang_name} auto-translation completed!"

    echo -e "\n4/4 🚀 Skipping HTML build (handled by Read the Docs)"
done

# ========================== 6. Completion Notification ===========================
echo -e "\n"
echo "====================================================================="
echo "🎉 All translations generated successfully!"
echo "====================================================================="
echo "📌 Output root: ${BUILDDIR}"
echo "📌 English docs: ${HTML_ROOT}/en/index.html"
echo "📌 Chinese docs: ${HTML_ROOT}/zh_CN/index.html"
echo "====================================================================="ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss