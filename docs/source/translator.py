"""
sphinx_po_translator.py

方案 A 实现：按 PO 文件、但以“批次（batch）”把多个 msgid 一次性发给 DeepSeek，让模型利用上下文进行翻译。

特点（模块化、便于调试）：
- 把每一步分成独立函数（收集未翻译条目 -> 构建批次提示 -> 调用 API -> 解析返回 -> 回写 PO -> 保存/备份）。
- 支持 dry-run（只打印 prompt 不调用 API）便于调试。
- 支持按条目数量或按字符数分块（用于控制 token 大小）。
- 在失败解析 JSON 时会把原始响应保存到 responses/ 供人工检查。

使用：
    pip install openai polib
    export DEEPSEEK_API_KEY=你的_key
    python sphinx_po_translator.py --locale-dir locale --lang zh_CN --batch-size 10

注意：需要根据 DeepSeek 的 token 限制调整 --batch-size 或 --max-chars。
"""

import os
import polib
import time
import json
import argparse
import re
from openai import OpenAI
from typing import List, Dict, Tuple, Any


# -------------------- 配置 DeepSeek 客户端 --------------------
def init_client():
    api_key = "sk-70406818a671408b80f43720b7978aab"
    if not api_key:
        raise EnvironmentError("请先设置环境变量 DEEPSEEK_API_KEY")
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    return client


# -------------------- 工具函数 --------------------


def chunk_entries(entries: List[polib.POEntry], batch_size: int, max_chars: int) -> List[List[polib.POEntry]]:
    """按数量和字符数同时分批。返回批次列表，每项是一组 entry。"""
    batches = []
    cur = []
    cur_chars = 0
    for e in entries:
        est = len(e.msgid) + (len(e.msgid_plural) if e.msgid_plural else 0)
        # 当单条本身超过 max_chars 时也要至少放入一个批次
        if cur and (len(cur) >= batch_size or cur_chars + est > max_chars):
            batches.append(cur)
            cur = []
            cur_chars = 0
        cur.append(e)
        cur_chars += est
    if cur:
        batches.append(cur)
    return batches


def save_response_debug(po_path: str, batch_index: int, content: str):
    os.makedirs("responses", exist_ok=True)
    fname = os.path.join("responses", f"{os.path.basename(po_path)}.batch{batch_index}.resp.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  已保存原始响应到 {fname}")


# -------------------- Prompt 构造 --------------------


def build_prompt_for_batch(entries: List[polib.POEntry], po_path: str, start_index: int = 1) -> str:
    """为一个批次构建 prompt。每条用编号标记，包含文件/位置/上下文信息。

    要求模型仅输出 JSON 格式：
    返回格式为 dict，key 为数字字符串（从 start_index 开始），value 为：
      - 对于单数条目: {"translation": "..."}
      - 对于复数条目: {"translation": "...", "plural": ["...", "..."]}

    示例:
    {
      "1": {"translation": "翻译文本"},
      "2": {"translation": "xxx", "plural": ["xxx-plural0", "xxx-plural1"]}
    }
    """
    parts = []
    header = ("你是一个专业的技术文档翻译助手，主要为半导体、FPGA方面。\n"
              "请把下面列出的英文内容翻译成中文，并保留 reStructuredText 的标记（例如 :ref:, :doc:, **bold**, ``code``, 链接标记等）。\n"
              "不要添加任何额外解释，只返回严格的 JSON（见下文）。\n\n"
              "返回要求（非常重要）：\n"
              "1) 输出一个 JSON 对象，键为条目编号（字符串形式），值为翻译对象。\n"
              "2) 单数条目的值为 {\"translation\": \"...\"}。\n"
              "3) 如果原文有复数（msgid_plural），翻译对象还应包含键 \"plural\"，其值为一个数组，对应各复数形式的翻译，例如 ['form0', 'form1']。\n"
              "4) 翻译时请尽量保持术语一致。请严禁输出除 JSON 以外的内容。\n\n"
              "下面给出条目列表：\n")
    parts.append(header)

    idx = start_index
    for e in entries:
        occ = ", ".join([":".join(map(str, occ)) for occ in (e.occurrences or [])])
        parts.append(f"### ENTRY {idx} \nFILE: {po_path} \nOCCURRENCES: {occ}\nCONTEXT: {e.msgctxt}\nSINGULAR:\n{e.msgid}\n")
        if e.msgid_plural:
            parts.append(f"PLURAL:\n{e.msgid_plural}\n")
        parts.append("\n")
        idx += 1

    parts.append("输出示例（仅说明格式，务必输出实际 JSON 且不要包含注释）：\n"
                 "{\n  \"1\": {\"translation\": \"...\"},\n  \"2\": {\"translation\": \"...\", \"plural\": [\"...\", \"...\"]}\n}\n")
    prompt = "\n".join(parts)
    return prompt


# -------------------- 调用 DeepSeek API --------------------


def call_deepseek(client: OpenAI, prompt: str, max_retries: int = 2, temperature: float = 0.0) -> str:
    """调用 DeepSeek（通过 openai.OpenAI 客户端），返回文本响应。出现异常会重试几次。"""
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=temperature,
                max_tokens=8192,
            )
            content = response.choices[0].message.content
            return content
        except Exception as exc:
            print(f"  调用 DeepSeek 失败（尝试 {attempt}/{max_retries}）：{exc}")
            if attempt < max_retries:
                time.sleep(1 + 2 * attempt)
            else:
                raise
    raise RuntimeError("未能成功调用 DeepSeek API")


# -------------------- 解析模型返回 --------------------


def parse_json_from_response(text: str) -> Any:
    """尝试把模型返回解析为 JSON 对象。若失败，抛出异常。
    也会尝试从长文本中提取第一个 JSON 区块。
    """
    # 先尝试直接解析
    try:
        return json.loads(text)
    except Exception:
        # 尝试提取第一个 JSON 块
        m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                raise ValueError("无法从响应中解析 JSON（已尝试提取 JSON 子串但解析失败）")
        else:
            raise ValueError("响应中未找到 JSON 子串")


# -------------------- 回写翻译到 PO --------------------


def apply_translations_to_entries(entries: List[polib.POEntry], parsed: Dict[str, Any], start_index: int = 1) -> Tuple[int, int]:
    """把解析后的 JSON 应用到 entries。返回 (成功数, 失败数)。

    parsed 的结构期望为 {"1": {"translation": "...", "plural": [..]?}, ...}
    """
    success = 0
    fail = 0
    for i, entry in enumerate(entries):
        key = str(start_index + i)
        if key not in parsed:
            print(f"  WARNING: 响应中缺少条目 {key}")
            fail += 1
            continue
        val = parsed[key]
        if not isinstance(val, dict) or "translation" not in val:
            print(f"  WARNING: 条目 {key} 的结构不符合预期: {val}")
            fail += 1
            continue
        entry.msgstr = val["translation"].strip()
        # 处理复数
        if entry.msgid_plural:
            if "plural" in val and isinstance(val["plural"], list):
                # polib 要求 msgstr_plural 是一个 dict，键为索引字符串
                mp = {}
                for idx, s in enumerate(val["plural"]):
                    mp[str(idx)] = s
                entry.msgstr_plural = mp
            else:
                print(f"  WARNING: 条目 {key} 有复数原文，但响应中未提供 plural 字段。")
                # 不覆盖 plural 的话可能会导致构建错误，用户需人工处理
        success += 1
    return success, fail


# -------------------- 主处理流程（文件级） --------------------


def translate_po_file_batch(po_path: str, client: OpenAI, batch_size: int = 10, max_chars: int = 8000, sleep_secs: float = 1.0, dry_run: bool = False, save_backup: bool = True, start_index_offset: int = 1, max_retries_api: int = 2, verbose: bool = True):
    """处理一个 .po 文件：收集未翻译条目 -> 分批 -> 调用 API -> 解析 -> 写回并保存。"""
    print(f"处理 PO: {po_path}")
    po = polib.pofile(po_path)

    # 收集未翻译条目
    entries = [e for e in po if (not e.obsolete) and (not e.translated())]
    if not entries:
        print("  没有未翻译条目。")
        return

    batches = chunk_entries(entries, batch_size=batch_size, max_chars=max_chars)
    print(f"  共 {len(entries)} 条未翻译，分成 {len(batches)} 个批次（batch_size={batch_size}, max_chars={max_chars}）。")

    if save_backup:
        bak = po_path + ".bak"
        po.save(bak)
        print(f"  已保存备份: {bak}")

    batch_no = 0
    for batch in batches:
        batch_no += 1
        print(f"  处理第 {batch_no}/{len(batches)} 批（{len(batch)} 条）...")
        prompt = build_prompt_for_batch(batch, po_path, start_index=start_index_offset)

        if dry_run:
            print("  dry-run 模式：下面是要发送给模型的 prompt（前 1000 字）：")
            print(prompt[:1000])
            continue

        # 调用 API
        resp_text = call_deepseek(client, prompt, max_retries=max_retries_api)

        # 解析 JSON
        try:
            parsed = parse_json_from_response(resp_text)
        except Exception as exc:
            print(f"  ERROR: 无法解析模型返回为 JSON: {exc}")
            save_response_debug(po_path, batch_no, resp_text)
            continue

        # 如果返回是数组（按顺序），转换为映射
        if isinstance(parsed, list):
            parsed_map = {}
            for i, item in enumerate(parsed):
                parsed_map[str(start_index_offset + i)] = item
            parsed = parsed_map

        # 把翻译应用到条目
        succ, fail = apply_translations_to_entries(batch, parsed, start_index=start_index_offset)
        print(f"    应用翻译: 成功 {succ}, 失败 {fail}")

        # 每批次保存一次
        po.save(po_path)
        print(f"    已保存: {po_path}")

        # 保存原始响应供人工检查
        save_response_debug(po_path, batch_no, resp_text)

        time.sleep(sleep_secs)

    print("处理完成。建议用 po 编辑器（如 Poedit）或人工复核关键文件。")


# -------------------- 目录级别批量处理 --------------------


def translate_locale_dir_batches(locale_dir: str, lang: str = "zh_CN", **kwargs):
    base_path = os.path.join(locale_dir, lang, "LC_MESSAGES")
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"找不到路径: {base_path}")

    client = init_client()

    for root, _, files in os.walk(base_path):
        for f in files:
            if f.endswith('.po'):
                po_path = os.path.join(root, f)
                try:
                    translate_po_file_batch(po_path, client, **kwargs)
                except Exception as exc:
                    print(f"处理 {po_path} 时发生异常: {exc}")


# -------------------- CLI --------------------


def parse_args():
    p = argparse.ArgumentParser(description="批量翻译 Sphinx .po 文件（基于 DeepSeek），以批次形式提高上下文质量。")
    p.add_argument('--locale-dir', default='locales', help='Sphinx locale 目录')
    p.add_argument('--lang', default='zh_CN', help='目标语言代码')
    p.add_argument('--batch-size', type=int, default=50, help='每批的最大条目数')
    p.add_argument('--max-chars', type=int, default=8000, help='每批的最大字符数（用于控制 token 大小）')
    p.add_argument('--sleep', type=float, default=1.0, help='批次间休眠秒数（防速率限制）')
    p.add_argument('--dry-run', action='store_true', help='只打印 prompt，不调用 API')
    p.add_argument('--no-backup', dest='save_backup', action='store_false', help='不保存 .po 备份')
    p.add_argument('--verbose', action='store_true', help='输出更多调试信息')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    kwargs = {
        'batch_size': args.batch_size,
        'max_chars': args.max_chars,
        'sleep_secs': args.sleep,
        'dry_run': args.dry_run,
        'save_backup': args.save_backup,
        'verbose': args.verbose,
    }
    translate_locale_dir_batches(args.locale_dir, lang=args.lang, **kwargs)