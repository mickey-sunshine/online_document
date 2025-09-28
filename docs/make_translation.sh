#!/bin/bash
# 注意：此脚本必须放在 docs 目录下，且在 docs 目录中执行

# 第一步：生成 .pot 翻译模板文件（使用相对路径：source 目录在当前目录下）
sphinx-build -b gettext source source/locale

# 检查模板文件是否生成成功
if [ ! -d "source/locale" ]; then
  echo "错误：未生成翻译模板文件，请检查 sphinx-build 是否安装正确"
  exit 1
fi

# 第二步：初始化英文翻译（-p 指定 pot 文件目录为 source/locale）
sphinx-intl update -p source/locale -l en

# 第三步：初始化中文翻译
sphinx-intl update -p source/locale -l zh_CN

echo "翻译文件生成成功！"
echo "英文翻译文件路径：source/locale/en/LC_MESSAGES/"
echo "中文翻译文件路径：source/locale/zh_CN/LC_MESSAGES/"