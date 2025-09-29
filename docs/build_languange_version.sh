#!/bin/bash
# 功能：在 source/build 下生成 en/zh_CN 中英文文档
# 输出路径：
#   - 翻译模板：source/build/gettext
#   - 英文文档：source/build/html/en
#   - 中文文档：source/build/html/zh_CN

# ========================== 1. 核心路径配置（对齐 source/build）==========================
# 脚本与 source 目录同级，所以 SOURCE_DIR 是 ./source
SOURCE_DIR="./source"  # 源文件目录（存放 conf.py、index.rst）
# 文档输出根目录：source/build（与 conf.py 中的 BUILDDIR 一致）
BUILDDIR="build"
# 翻译模板目录：source/build/gettext（与 conf.py 中的 gettext_output_dir 一致）
POT_DIR="${BUILDDIR}/gettext"
# HTML 文档根目录：source/build/html（后续分 en/zh_CN）
HTML_ROOT="${BUILDDIR}/html"
# 翻译文件目录（source/locales，存放 .po 翻译文件）
LOCALE_DIR="${SOURCE_DIR}/locale"
# 自动翻译脚本路径（假设在 source 下，若不在需调整）
TRANSLATOR_SCRIPT="${SOURCE_DIR}/translator.py"
# 支持的语言列表
LANGUAGES=("zh_CN" "en")

# ========================== 2. 工具函数（辅助检查和清理）==========================
# 检查命令是否存在（如 sphinx-build、python3）
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ 错误：未找到命令 '$1'，请先安装（如 pip3 install sphinx sphinx-intl）"
        exit 1
    fi
}

# 检查路径是否存在（如 source 目录、translator.py）
check_path() {
    if [ ! -e "$1" ]; then
        echo "❌ 错误：路径 '$1' 不存在，请检查项目结构！"
        exit 1
    fi
}

# 清理旧文档（避免旧内容干扰）
clean_old_doc() {
    local lang=$1
    local doc_path="${HTML_ROOT}/${lang}"
    if [ -d "$doc_path" ]; then
        echo "🗑️  清理旧 ${lang} 文档：${doc_path}"
        rm -rf "$doc_path"
    fi
}

# ========================== 3. 前置检查（确保环境和路径正常）==========================
echo "🔍 正在检查环境和依赖..."
# 检查核心命令
check_command "sphinx-build"
check_command "sphinx-intl"
check_command "python3"
# 检查核心路径（确保 source 目录和翻译脚本存在）
check_path "$SOURCE_DIR"          # 检查源文件目录
check_path "$TRANSLATOR_SCRIPT"  # 检查自动翻译脚本（若没有可注释此句）
# 自动创建输出目录（source/build、source/build/gettext、source/build/html）
mkdir -p "$POT_DIR" || { echo "❌ 错误：无法创建翻译模板目录 $POT_DIR"; exit 1; }
mkdir -p "$HTML_ROOT" || { echo "❌ 错误：无法创建 HTML 根目录 $HTML_ROOT"; exit 1; }
echo "✅ 环境和依赖检查通过！输出根目录：${BUILDDIR}"

# ========================== 4. 提取翻译模板（生成 .pot 文件到 source/build/gettext）==========================
echo -e "\n📝 正在提取翻译模板（输出到 ${POT_DIR}）..."
# 执行 sphinx-build 生成 .pot 模板（-b gettext 表示提取翻译模板）
sphinx-build -b gettext "$SOURCE_DIR" "$POT_DIR"

# 检查模板提取是否成功
if [ $? -ne 0 ]; then
    echo "❌ 错误：提取翻译模板失败，请检查 source 下的 .rst/.md 语法（如标题下划线、链接格式）！"
    exit 1
fi
echo "✅ 翻译模板提取完成！模板文件路径：${POT_DIR}"

# ========================== 5. 循环生成中英文文档（输出到 source/build/html）==========================
echo -e "\n🏗️  开始生成中英文文档（输出到 ${HTML_ROOT}）..."
for lang in "${LANGUAGES[@]}"; do
    # 语言名称映射（提升日志可读性）
    lang_name=$( [ "$lang" = "en" ] && echo "英文" || echo "中文" )
    # 当前语言的文档路径（source/build/html/en 或 source/build/html/zh_CN）
    current_doc_path="${HTML_ROOT}/${lang}"

    echo -e "\n====================================================================="
    echo "🌐 正在生成【${lang_name}】文档（最终路径：${current_doc_path}）"
    echo "====================================================================="

    # 步骤 1：清理旧文档
    echo -e "\n1/4 🗑️  清理旧文档"
    clean_old_doc "$lang"

    # 步骤 2：更新当前语言的翻译文件（生成 .po 文件到 source/locales）
    echo -e "\n2/4 🔄 更新 ${lang_name} 翻译文件"
    sphinx-intl update -p "$POT_DIR" -l "$lang" -d "$LOCALE_DIR"
    # 解释：-p 指定模板目录，-l 指定语言，-d 指定翻译文件输出目录（source/locales）

    if [ $? -ne 0 ]; then
        echo "❌ 错误：更新 ${lang_name} 翻译文件失败！"
        exit 1
    fi
    echo "✅ ${lang_name} 翻译文件更新完成（路径：${LOCALE_DIR}/${lang}/LC_MESSAGES/）"

    # 步骤 3：自动翻译（调用 translator.py 填充 .po 文件，若无此脚本可注释）
    echo -e "\n3/4 🤖 自动翻译 ${lang_name} 内容"
    python3 "$TRANSLATOR_SCRIPT" --locale-dir "$LOCALE_DIR" --target-langs "$lang" --batch-size 10

    if [ $? -ne 0 ]; then
        echo "❌ 错误：${lang_name} 自动翻译失败，请检查 translator.py！"
        exit 1
    fi
    echo "✅ ${lang_name} 自动翻译完成！"

    # 步骤 4：构建当前语言的 HTML 文档（输出到 source/build/html/[lang]）
    echo -e "\n4/4 🚀 构建 ${lang_name} HTML 文档"
    # 执行 sphinx-build，-D language="$lang" 指定当前语言
    sphinx-build -b html -D language="$lang" "$SOURCE_DIR" "$current_doc_path"

    # 检查文档构建是否成功
    if [ $? -ne 0 ]; then
        echo "❌ 错误：构建 ${lang_name} 文档失败，请检查 source 下的源文件语法！"
        exit 1
    fi

    # 步骤 5：提示当前语言文档完成
    echo -e "\n✅ 【${lang_name}】文档生成完成！"
    echo "   📁 文档入口：${current_doc_path}/index.html"
    echo "   💡 操作：双击上述文件，用浏览器打开即可浏览！"
done

# ========================== 6. 全流程完成提示==========================
echo -e "\n"
echo "====================================================================="
echo "🎉 中英文文档全部生成完成！"
echo "====================================================================="
echo "📌 输出根目录：${BUILDDIR}"
echo "📌 英文文档：${HTML_ROOT}/en/index.html"
echo "📌 中文文档：${HTML_ROOT}/zh_CN/index.html"
echo "💡 提示：若需重新生成，直接再次执行本脚本即可（会自动清理旧文档）"
echo "====================================================================="