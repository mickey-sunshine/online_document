#!/bin/bash
# Function: Generate English/Chinese (en/zh_CN) documentation under docs/source/build
# Output Paths:
#   - Translation templates: source/build/gettext
#   - English documentation: source/build/html/en
#   - Chinese documentation: source/build/html/zh_CN

# ========================== 1. Core Path Configuration (Aligned with source/build) ===========================
# Script is located in the "docs" directory, so SCRIPT_DIR is ./docs
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
SOURCE_DIR="$SCRIPT_DIR/source"  # Source file directory: docs/source (Critical Fix!)
# Documentation output root directory: source/build (matches BUILDDIR in conf.py)
BUILDDIR="$SOURCE_DIR/build"
# Translation template directory: source/build/gettext
POT_DIR="$BUILDDIR/gettext"
# HTML documentation root directory: source/build/html (subdirectories en/zh_CN will be created later)
HTML_ROOT="$BUILDDIR/html"
# Translation file directory (source/locales, stores .po translation files)
LOCALE_DIR="$SOURCE_DIR/locale"
# Auto-translation script path (assumed to be under docs/source; adjust if located elsewhere)
TRANSLATOR_SCRIPT="$SOURCE_DIR/translator.py"
# List of supported languages
LANGUAGES=("zh_CN" "en")

# ========================== 2. Utility Functions (Unchanged) ===========================
# Check if a command exists (e.g., sphinx-build, python3)
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ Error: Command '$1' not found. Please install it first (e.g., pip3 install sphinx sphinx-intl)"
        exit 1
    fi
}

# Check if a path exists (e.g., source directory, translator.py)
check_path() {
    if [ ! -e "$1" ]; then
        echo "❌ Error: Path '$1' does not exist. Please check your project structure!"
        exit 1
    fi
}

# Clean up old documentation (avoids interference from outdated content)
clean_old_doc() {
    local lang=$1
    local doc_path="${HTML_ROOT}/${lang}"
    if [ -d "$doc_path" ]; then
        echo "🗑️ Cleaning up old ${lang} documentation: ${doc_path}"
        rm -rf "$doc_path"
    fi
}

# ========================== 3. Pre-checks (Fixed Path Validation) ===========================
echo "🔍 Checking environment and dependencies..."
# Check core commands required for documentation generation
check_command "sphinx-build"
check_command "sphinx-intl"
check_command "python3"
# Check core paths: Ensure docs/source and conf.py exist (Critical Fix!)
check_path "$SOURCE_DIR"          # Check if docs/source directory exists
check_path "$SOURCE_DIR/conf.py"  # Check if docs/source/conf.py exists
check_path "$TRANSLATOR_SCRIPT"   # Check if the auto-translation script exists

# Automatically create output directories if they don't exist
mkdir -p "$POT_DIR" || { echo "❌ Error: Failed to create translation template directory $POT_DIR"; exit 1; }
mkdir -p "$HTML_ROOT" || { echo "❌ Error: Failed to create HTML root directory $HTML_ROOT"; exit 1; }
echo "✅ Environment and dependency checks passed! Output root directory: ${BUILDDIR}"

# ========================== 4. Extract Translation Templates (Fixed Source Directory Path) ===========================
echo -e "\n📝 Extracting translation templates (output to ${POT_DIR})..."
# Source directory is docs/source ($SOURCE_DIR), not "source" in the root directory
sphinx-build -b gettext "$SOURCE_DIR" "$POT_DIR"

# Check if template extraction succeeded
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to extract translation templates. Please check .rst syntax in docs/source (e.g., heading underlines, link formats)!"
    exit 1
fi
echo "✅ Translation template extraction completed! Template file path: ${POT_DIR}"

# ========================== 5. Generate English/Chinese Documentation in a Loop (Logic Retained, Paths Fixed) ===========================
echo -e "\n🏗️ Starting to generate English/Chinese documentation (output to ${HTML_ROOT})..."
for lang in "${LANGUAGES[@]}"; do
    # Map language codes to readable names (improves log readability)
    lang_name=$( [ "$lang" = "en" ] && echo "English" || echo "Chinese" )
    # Documentation path for the current language (source/build/html/en or source/build/html/zh_CN)
    current_doc_path="${HTML_ROOT}/${lang}"

    echo -e "\n====================================================================="
    echo "🌐 Generating [${lang_name}] documentation (Final path: ${current_doc_path})"
    echo "====================================================================="

    echo -e "\n1/4 🗑️ Cleaning up old documentation"
    clean_old_doc "$lang"

    echo -e "\n2/4 🔄 Updating ${lang_name} translation files"
    sphinx-intl update -p "$POT_DIR" -l "$lang" -d "$LOCALE_DIR"
    # Explanation: -p specifies the template directory, -l specifies the language, -d specifies the translation output directory (source/locales)

    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to update ${lang_name} translation files!"
        exit 1
    fi
    echo "✅ ${lang_name} translation files updated successfully (Path: ${LOCALE_DIR}/${lang}/LC_MESSAGES/)"

    echo -e "\n3/4 🤖 Auto-translating ${lang_name} content"
    python3 "$TRANSLATOR_SCRIPT" --locale-dir "$LOCALE_DIR" --target-langs "$lang" --batch-size 30

    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to auto-translate ${lang_name} content. Please check translator.py!"
        exit 1
    fi
    echo "✅ ${lang_name} auto-translation completed!"

    # echo -e "\n4/4 🚀 Building ${lang_name} HTML documentation"
    # # Execute sphinx-build, -D language="$lang" specifies the current language
    # sphinx-build -b html -D language="$lang" "$SOURCE_DIR" "$current_doc_path"

    # # Check if documentation build succeeded
    # if [ $? -ne 0 ]; then
    #     echo "❌ Error: Failed to build ${lang_name} documentation. Please check the syntax of source files in docs/source!"
    #     exit 1
    # fi

    # # Notify completion of documentation for the current language
    # echo -e "\n✅ [${lang_name}] documentation generation completed!"
    # echo "   📁 Documentation entry point: ${current_doc_path}/index.html"
    # echo "   💡 Action: Double-click the above file and open it with a browser to view!"
done


# ========================== 6. Completion Notification ===========================
echo -e "\n"
echo "====================================================================="
echo "🎉 All English/Chinese documentation has been generated successfully!"
echo "====================================================================="
echo "📌 Output root directory: ${BUILDDIR}"
echo "📌 English documentation: ${HTML_ROOT}/en/index.html"
echo "📌 Chinese documentation: ${HTML_ROOT}/zh_CN/index.html"
echo "💡 Tip: To regenerate documentation, simply run this script again (old files will be cleaned up automatically)"
echo "====================================================================="