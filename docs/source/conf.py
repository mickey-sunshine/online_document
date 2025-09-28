# -*- coding: utf-8 -*-
import os
import sys

# 项目信息
project = 'my project'
copyright = '2025, hello world'
author = 'mickey'
version = '1.0'
release = '1.0.0'

# 扩展
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# 国际化配置
language = None  # 不指定默认语言，由Read the Docs切换
locale_dirs = ['locale/']  # 翻译文件目录
gettext_compact = False    # 每个文档生成独立的翻译文件

# 主题配置
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'display_version': True,
}

# 文档源文件配置
source_suffix = '.rst'
master_doc = 'index'

# 支持的语言（必须与后续翻译配置对应）
supported_languages = {
    'en': 'English',
    'zh_CN': '中文'
}