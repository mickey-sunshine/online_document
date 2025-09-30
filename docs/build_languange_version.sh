#!/bin/bash
# Function: Generate English/Chinese (en/zh_CN) documentation under docs/source/build
# Output Paths:
#   - Translation templates: source/build/gettext
#   - English documentation: source/build/html/en
#   - Chinese documentation: source/build/html/zh_CN

# ========================== 1. Core Path Configuration ===========================
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
SOURCE_DIR="$SCRIPT_DIR/source"  # Source directory: docs/source
BUILDDIR="$SOURCE_DIR/build"     # Output root directory: docs/source/build
POT_DIR="$BUILDDIR/gettext"      # Directory for translation templates
HTML_ROOT="$BUILDDIR/html"       # Root directory for HTML output
LOCALE_DIR="$SOURCE_DIR/locale"  # Directory for translation files (.po)
TRANSLATOR_SCRIPT="$SOURCE_DIR/translator.py"  # Path to the translation script
LANGUAGES=("zh_CN" "en")         # List of supported languages

# ========================== 2. Utility Functions ===========================
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo " Error: Command '$1' not found. Install via: pip3 install sphinx sphinx-intl"
        exit 1
    fi
}

check_path() {
    if [ ! -e "$1" ]; then
        echo " Error: Path '$1' does not exist. Please check your project structure!"
        exit 1
    fi
}

clean_old_doc() {
    local lang=$1
    local doc_path="${HTML_ROOT}/${lang}"
    if [ -d "$doc_path" ]; then
        echo " Cleaning old ${lang} documentation: ${doc_path}"
        rm -rf "$doc_path"
    fi
}

# ========================== 3. Pre-checks (Optimized I/O) ===========================
echo " Checking environment and dependencies..."
check_command "sphinx-build"
check_command "sphinx-intl"
check_command "python3"

REQUIRED_PATHS=("$SOURCE_DIR" "$SOURCE_DIR/conf.py" "$TRANSLATOR_SCRIPT")
for path in "${REQUIRED_PATHS[@]}"; do
    check_path "$path"
done

mkdir -p "$POT_DIR" "$HTML_ROOT" || { echo " Error: Failed to create output directories"; exit 1; }
echo " Environment checks passed! Output root directory: ${BUILDDIR}"

# ========================== 4. Extract Translation Templates ===========================
echo -e "\n Extracting translation templates (output to ${POT_DIR})..."
sphinx-build -b gettext "$SOURCE_DIR" "$POT_DIR"

if [ $? -ne 0 ]; then
    echo " Error: Failed to extract translation templates. Please check .rst syntax!"
    exit 1
fi
echo " Translation templates extracted successfully: ${POT_DIR}"

# ========================== 5. Generate Translations and HTML ===========================
echo -e "\n Starting translation and HTML generation (output to ${HTML_ROOT})..."
for lang in "${LANGUAGES[@]}"; do
    lang_name=$( [ "$lang" = "en" ] && echo "English" || echo "Chinese" )
    current_doc_path="${HTML_ROOT}/${lang}"

    echo -e "\n====================================================================="
    echo " Processing [${lang_name}] documentation (Final path: ${current_doc_path})"
    echo "====================================================================="

    echo -e "\n1/4  Cleaning old documentation files"
    clean_old_doc "$lang"

    echo -e "\n2/4  Updating ${lang_name} translation files"
    sphinx-intl update -p "$POT_DIR" -l "$lang" -d "$LOCALE_DIR"
    if [ $? -ne 0 ]; then
        echo " Error: Failed to update ${lang_name} translation files!"
        exit 1
    fi
    echo " ${lang_name} translation files updated: ${LOCALE_DIR}/${lang}/LC_MESSAGES/"

    echo -e "\n3/4  Auto-translating ${lang_name} content"
    if [ "$READTHEDOCS" = "True" ]; then
        python3 "$TRANSLATOR_SCRIPT" \
            --locale-dir "$LOCALE_DIR" \
            --target-langs "$lang" \
            --batch-size 20 \
            --max-chars 12000 \
            --sleep 0.3 \
            --no-backup
    else
        python3 "$TRANSLATOR_SCRIPT" \
            --locale-dir "$LOCALE_DIR" \
            --target-langs "$lang" \
            --batch-size 20 \
            --max-chars 8000 \
            --sleep 1.0
    fi

    if [ $? -ne 0 ]; then
        echo " Error: Failed to auto-translate ${lang_name} content!"
        exit 1
    fi
    echo " ${lang_name} auto-translation completed successfully!"

    echo -e "\n4/4  Building ${lang_name} HTML documentation"
    # Core modification: Restore HTML build command, with RTD environment check to avoid duplicate builds
    if [ "$READTHEDOCS" != "True" ]; then
        # Local environment: Run sphinx-build to generate HTML
        sphinx-build -b html -D language="$lang" "$SOURCE_DIR" "$current_doc_path"
        if [ $? -ne 0 ]; then
            echo " Error: Failed to build ${lang_name} HTML documentation!"
            exit 1
        fi
        echo " ${lang_name} HTML documentation built: ${current_doc_path}/index.html"
    else
        # RTD environment: Skip build (handled automatically by the platform)
        echo " Skipping HTML build (will be handled by Read the Docs)"
    fi
done

# ========================== 6. Completion Notification ===========================
echo -e "\n"
echo "====================================================================="
echo " All documentation generated successfully!"
echo "====================================================================="
echo " Output root directory: ${BUILDDIR}"
echo " English documentation: ${HTML_ROOT}/en/index.html"
echo " Chinese documentation: ${HTML_ROOT}/zh_CN/index.html"
echo "====================================================================="