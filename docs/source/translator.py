"""
translator.py
Batch translation tool for Sphinx PO files (powered by DeepSeek API)
Supports dynamic target language switching (en/zh_CN), automatic batching, and preserves reStructuredText markup
Usage:
1. Install dependencies: pip install openai polib
2. Set API Key: export DEEPSEEK_API_KEY=your_api_key (use "set DEEPSEEK_API_KEY=your_api_key" for Windows)
3. Translate to Chinese: python translator.py --locale-dir source/locale --lang zh_CN --batch-size 10
4. Translate to English: python translator.py --locale-dir source/locale --lang en --batch-size 10
"""

import os
import polib
import time
import json
import re
import argparse
from openai import OpenAI
from typing import List, Dict, Tuple, Any


# -------------------------- 1. Configuration & Initialization --------------------------
def init_deepseek_client() -> OpenAI:
    """Initialize DeepSeek client (compatible with OpenAI interface) by reading API Key from environment variable"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Please set the DEEPSEEK_API_KEY environment variable first\n"
            "Linux/Mac: export DEEPSEEK_API_KEY=your_api_key\n"
            "Windows: set DEEPSEEK_API_KEY=your_api_key"
        )
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"  # DeepSeek API base URL
        )
        return client
    except Exception as e:
        raise RuntimeError(f"Failed to initialize DeepSeek client: {str(e)}")


# -------------------------- 2. Utility Functions (Batching, Logging) --------------------------
def chunk_po_entries(
    entries: List[polib.POEntry],
    batch_size: int = 10,
    max_chars: int = 8000
) -> List[List[polib.POEntry]]:
    """
    Batch PO entries using dual criteria: entry count and total character count
    Prevents single-batch token overflow (DeepSeek's default limit is 8192 tokens)
    """
    batches = []
    current_batch = []
    current_chars = 0  # Count total characters in current batch (msgid + msgid_plural)

    for entry in entries:
        # Estimate character count for current entry (including plural form if exists)
        entry_chars = len(entry.msgid)
        if entry.msgid_plural:
            entry_chars += len(entry.msgid_plural)

        # Split into new batch if either condition is met:
        # 1. Current batch reaches maximum entry count
        # 2. Adding current entry exceeds maximum character limit (force add if single entry is too long)
        if (current_batch and (len(current_batch) >= batch_size or current_chars + entry_chars > max_chars)):
            batches.append(current_batch)
            current_batch = []
            current_chars = 0

        current_batch.append(entry)
        current_chars += entry_chars

    # Add the last incomplete batch
    if current_batch:
        batches.append(current_batch)

    return batches


def save_debug_response(po_file_path: str, batch_idx: int, response: str):
    """Save raw model response to 'responses/' directory for debugging purposes"""
    debug_dir = "responses"
    os.makedirs(debug_dir, exist_ok=True)
    # Generate debug filename (includes PO filename and batch number)
    po_filename = os.path.basename(po_file_path)
    debug_file = os.path.join(debug_dir, f"{po_filename}.batch{batch_idx}.txt")
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(f"PO File Path: {po_file_path}\n")
        f.write(f"Batch Number: {batch_idx}\n")
        f.write(f"Generation Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")
        f.write(response)
    print(f"  [Debug] Raw response saved to: {debug_file}")


# -------------------------- 3. Prompt Construction (Dynamic Language Adaptation) --------------------------
def build_batch_prompt(
    entries: List[polib.POEntry],
    po_file_path: str,
    target_lang: str,
    start_idx: int = 1
) -> str:
    """
    Dynamically generate prompt based on target language to ensure correct translation direction:
    - target_lang=zh_CN: English → Chinese
    - target_lang=en: Chinese → English (or retain original English if already in English)
    """
    # 1. Dynamically generate translation rules
    if target_lang == "zh_CN":
        translate_rule = "Translate the following English content to Chinese while maintaining technical document accuracy and professionalism"
    elif target_lang == "en":
        translate_rule = "Translate the following content to English (retain original English if already in English) and ensure consistent terminology"
    else:
        raise ValueError(f"Unsupported target language: {target_lang}, only en/zh_CN are supported")

    # 2. Prompt header (includes translation rules and format requirements)
    prompt_parts = [
        "You are a professional technical document translation assistant specializing in semiconductor and FPGA documentation localization.",
        translate_rule + ", and strictly preserve the following content:",
        "- reStructuredText markup (e.g., :ref:, :doc:, **bold text**, ``code snippets``, `links`)",
        "- Variable names, function names, and paths (e.g., ${HOME}, func())",
        "- Version numbers, numbers, and symbols (e.g., v1.0.0, 2024, %)",
        "",
        "【Output Requirements】",
        "1. Return ONLY JSON format, no additional explanations or comments!",
        "2. JSON Structure:",
        "   - Key: Entry number (string format, e.g., \"1\", \"2\")",
        "   - Value: Translation object (singular entries include \"translation\"; plural entries additionally include \"plural\" array)",
        "3. Example (format reference only, replace with actual translations):",
        '   { "1": { "translation": "User Manual" }, "2": { "translation": "File", "plural": ["File 1", "Files"] } }',
        "",
        "【Entries to Translate】",
    ]

    # 3. Populate entries to translate (includes file path and location info to help model understand context)
    for idx, entry in enumerate(entries):
        entry_num = start_idx + idx
        # Extract entry location info (file name and line number)
        occurrences = entry.occurrences or []
        occ_str = ", ".join([f"{file}:{line}" for file, line in occurrences])
        # Construct entry content
        prompt_parts.append(f"--- Entry {entry_num} ---")
        prompt_parts.append(f"PO File: {po_file_path}")
        prompt_parts.append(f"Location: {occ_str or 'Unknown'}")
        prompt_parts.append(f"Original Text (Singular): {entry.msgid}")
        if entry.msgid_plural:
            prompt_parts.append(f"Original Text (Plural): {entry.msgid_plural}")
        prompt_parts.append("")  # Empty line for separation

    return "\n".join(prompt_parts)


# -------------------------- 4. DeepSeek API Call --------------------------
def call_deepseek_api(
    client: OpenAI,
    prompt: str,
    max_retries: int = 3,
    temperature: float = 0.1
) -> str:
    """
    Call DeepSeek API to translate batch entries with retry mechanism
    temperature=0.1: Ensures translation stability (avoids excessive divergence)
    """
    for retry in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",  # DeepSeek general-purpose chat model
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=8192,  # Matches DeepSeek free-tier token limit
                timeout=30,
            )
            # Extract text content from model response
            content = response.choices[0].message.content.strip()
            if not content:
                raise ValueError("Model returned empty content")
            return content
        except Exception as e:
            error_msg = f"API call failed (Attempt {retry}/{max_retries}): {str(e)}"
            print(f"  [Error] {error_msg}")
            if retry < max_retries:
                sleep_time = 2 ** retry  # Exponential backoff (2s, 4s, 8s...)
                print(f"  [Wait] Retrying after {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                raise RuntimeError(f"API call failed after multiple attempts: {error_msg}")


# -------------------------- 5. Model Response Parsing --------------------------
def parse_translation_response(response: str) -> Dict[str, Any]:
    """
    Parse JSON response from model and handle common format issues (e.g., extra code block markers)
    """
    try:
        # Handle potential code block markers (e.g., ```json ... ```) returned by model
        json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
        # Parse JSON
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}\nRaw response snippet: {response[:200]}...")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during response parsing: {str(e)}")


# -------------------------- 6. Translate Single PO File --------------------------
def translate_single_po_file(
    po_file_path: str,
    client: OpenAI,
    target_lang: str,
    batch_size: int = 10,
    max_chars: int = 8000,
    save_backup: bool = True
) -> Tuple[int, int]:
    """
    Translate a single PO file and return (successful_translations_count, failed_translations_count)
    Workflow: Load PO → Filter untranslated entries → Batch translation → Write back results → Save
    """
    print(f"\n【Processing PO File】: {po_file_path}")
    # 1. Load PO file and create backup
    try:
        po = polib.pofile(po_file_path, encoding="utf-8")
        # Create backup (prevents file corruption if translation fails)
        if save_backup:
            backup_path = f"{po_file_path}.bak"
            po.save(backup_path)
            print(f"  [Backup] Saved to: {backup_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to load PO file: {str(e)}")

    # 2. Filter untranslated entries (exclude obsolete and already translated entries)
    untranslated = [
        entry for entry in po
        if not entry.obsolete and not entry.translated()
    ]
    if not untranslated:
        print(f"  [Skipped] No untranslated entries found")
        return (0, 0)
    print(f"  [Stats] Total {len(untranslated)} untranslated entries")

    # 3. Batch process entries
    batches = chunk_po_entries(untranslated, batch_size, max_chars)
    print(f"  [Batching] Split into {len(batches)} batches (Max {batch_size} entries/{max_chars} chars per batch)")

    total_success = 0
    total_fail = 0

    for batch_idx, batch in enumerate(batches, 1):
        print(f"\n  【Batch {batch_idx}/{len(batches)}】({len(batch)} entries)")
        # 4. Construct prompt and call API
        prompt = build_batch_prompt(batch, po_file_path, target_lang, start_idx=total_success + 1)
        try:
            # Call API (comment this line for dry-run mode to only print prompts)
            response = call_deepseek_api(client, prompt)
            save_debug_response(po_file_path, batch_idx, response)

            # 5. Parse response and write back translations
            parsed = parse_translation_response(response)
            batch_success, batch_fail = 0, 0

            for entry_idx, entry in enumerate(batch):
                entry_num = str(total_success + entry_idx + 1)
                # Check if current entry exists in parsed results
                if entry_num not in parsed:
                    print(f"    [Failed] Entry {entry_num}: No corresponding translation found in response")
                    batch_fail += 1
                    continue

                trans_data = parsed[entry_num]
                # Validate translation data format
                if not isinstance(trans_data, dict) or "translation" not in trans_data:
                    print(f"    [Failed] Entry {entry_num}: Invalid translation format ({trans_data})")
                    batch_fail += 1
                    continue

                # Write back singular translation
                entry.msgstr = trans_data["translation"].strip()
                # Write back plural translation (if exists)
                if entry.msgid_plural and "plural" in trans_data:
                    plural_trans = trans_data["plural"]
                    if isinstance(plural_trans, list) and len(plural_trans) > 0:
                        # polib requires plural translations in { "0": "...", "1": "..." } format
                        entry.msgstr_plural = {str(i): t.strip() for i, t in enumerate(plural_trans)}
                    else:
                        print(f"    [Warning] Entry {entry_num}: Invalid plural translation format, skipping plural section")

                batch_success += 1
                print(f"    [Success] Entry {entry_num}: {entry.msgid[:50]}... → {entry.msgstr[:50]}...")

            # Update total stats for current batch
            total_success += batch_success
            total_fail += batch_fail
            print(f"  【Batch Result】Success: {batch_success} entries, Failed: {batch_fail} entries")

            # 6. Save PO file after each batch (prevents progress loss from mid-process failures)
            po.save(po_file_path)
            print(f"  [Save] Updated PO file: {po_file_path}")

        except Exception as e:
            print(f"  [Batch Error] Processing failed: {str(e)}")
            total_fail += len(batch)
            continue

    # 7. Return total results
    print(f"\n【File Result】{po_file_path}: Success: {total_success} entries, Failed: {total_fail} entries")
    return (total_success, total_fail)


# -------------------------- 7. Batch Translate All PO Files in Directory --------------------------
def batch_translate_locale_dir(
    locale_dir: str,
    target_lang: str,
    batch_size: int = 10,
    max_chars: int = 8000,
    save_backup: bool = True
):
    """
    Batch translate all PO files for a specific language in the locale directory
    Required directory structure: locale_dir/[lang]/LC_MESSAGES/*.po (Sphinx standard structure)
    """
    # Check if target language directory exists
    target_dir = os.path.join(locale_dir, target_lang, "LC_MESSAGES")
    if not os.path.exists(target_dir):
        raise FileNotFoundError(f"Target language directory not found: {target_dir}\nPlease verify --locale-dir and --lang parameters")

    # Initialize client
    client = init_deepseek_client()
    print(f"【Starting Batch Translation】")
    print(f"Target Language: {target_lang}")
    print(f"PO File Directory: {target_dir}")
    print(f"Batch Configuration: {batch_size} entries/batch, {max_chars} chars/batch")
    print("=" * 60)

    # Traverse all PO files
    total_success = 0
    total_fail = 0
    po_files = [f for f in os.listdir(target_dir) if f.endswith(".po")]

    if not po_files:
        print(f"【No PO Files】No .po files found in {target_dir}")
        return

    for po_filename in po_files:
        po_file_path = os.path.join(target_dir, po_filename)
        try:
            success, fail = translate_single_po_file(
                po_file_path=po_file_path,
                client=client,
                target_lang=target_lang,
                batch_size=batch_size,
                max_chars=max_chars,
                save_backup=save_backup
            )
            total_success += success
            total_fail += fail
        except Exception as e:
            print(f"【File Skipped】{po_file_path}: Processing exception → {str(e)}")
            total_fail += 1  # Count as failure
            continue

    # Print final summary
    print("\n" + "=" * 60)
    print(f"【Batch Translation Summary】")
    print(f"Total PO Files Processed: {len(po_files)}")
    print(f"Total Successful Translations: {total_success}")
    print(f"Total Failed Translations: {total_fail}")
    print(f"Overall Success Rate: {total_success/(total_success+total_fail)*100:.1f}%" if (total_success+total_fail) > 0 else "N/A")
    print("=" * 60)


# -------------------------- 8. Command Line Interface & Main Function --------------------------
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Batch translate Sphinx PO files using DeepSeek API with dynamic language support")
    parser.add_argument(
        '--locale-dir', 
        default='locale', 
        help='Root directory of Sphinx locale files (contains language-specific subdirectories)'
    )
    parser.add_argument(
        '--lang', 
        default='en', 
        choices=['en', 'zh_CN'],
        help='Target language for translation (en/zh_CN)'
    )
    parser.add_argument(
        '--batch-size', 
        type=int, 
        default=10, 
        help='Maximum number of entries per translation batch (default: 10)'
    )
    parser.add_argument(
        '--max-chars', 
        type=int, 
        default=8000, 
        help='Maximum total characters per batch (prevents token overflow, default: 8000)'
    )
    parser.add_argument(
        '--no-backup', 
        dest='save_backup', 
        action='store_false', 
        help='Disable automatic backup of PO files (not recommended)'
    )
    return parser.parse_args()


def main():
    """Main function to execute batch translation"""
    args = parse_arguments()
    try:
        batch_translate_locale_dir(
            locale_dir=args.locale_dir,
            target_lang=args.lang,
            batch_size=args.batch_size,
            max_chars=args.max_chars,
            save_backup=args.save_backup
        )
    except Exception as e:
        print(f"\n【Fatal Error】{str(e)}")
        exit(1)


if __name__ == '__main__':
    main()  # Execute main function when script is run directly