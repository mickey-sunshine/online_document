import os
import polib
import time
import json
import argparse
import re
import subprocess
import multiprocessing
from openai import OpenAI
from typing import List, Dict, Tuple, Any


# -------------------- Initialize DeepSeek Client --------------------
def init_client():
    """Initialize OpenAI-compatible client for DeepSeek API with hardcoded API key."""
    # Hardcoded API Key
    api_key = "sk-70406818a671408b80f43720b7978aab"
    if not api_key:
        raise EnvironmentError("DeepSeek API Key is not set (check hardcoded value in init_client())")
    
    # Configure DeepSeek API endpoint (OpenAI-compatible base URL)
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    return client


# -------------------- Utility Functions --------------------
def chunk_entries(entries: List[polib.POEntry], batch_size: int, max_chars: int) -> List[List[polib.POEntry]]:
    """
    Chunk PO entries by both entry count and character limit to fit API token constraints.
    """
    batches = []
    current_batch = []
    current_char_count = 0

    for entry in entries:
        entry_char_est = len(entry.msgid) + (len(entry.msgid_plural) if entry.msgid_plural else 0)
        
        if current_batch and (len(current_batch) >= batch_size or current_char_count + entry_char_est > max_chars):
            batches.append(current_batch)
            current_batch = []
            current_char_count = 0
        
        current_batch.append(entry)
        current_char_count += entry_char_est

    if current_batch:
        batches.append(current_batch)
    
    return batches


def save_response_debug(po_path: str, batch_index: int, target_lang: str, content: str):
    """Save raw API responses to debug directory"""
    debug_dir = os.path.join("responses", target_lang)
    os.makedirs(debug_dir, exist_ok=True)
    
    debug_filename = os.path.join(debug_dir, f"{os.path.basename(po_path)}.batch{batch_index}.resp.txt")
    with open(debug_filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"  Saved raw response to {debug_filename}")


# -------------------- Check if Compilation is Needed (Skip Unmodified Files) --------------------
def needs_compilation(po_path: str) -> bool:
    """Check if PO file needs recompilation by comparing modification time with MO file"""
    mo_path = os.path.splitext(po_path)[0] + ".mo"
    if not os.path.exists(mo_path):
        return True
    return os.path.getmtime(po_path) > os.path.getmtime(mo_path)


def compile_po_to_mo(po_path: str, verbose: bool = True) -> bool:
    """Compile .po file to binary .mo file using msgfmt"""
    if not needs_compilation(po_path):
        if verbose:
            print(f"    Skipping compilation: {os.path.basename(po_path)} (no changes)")
        return True

    mo_path = os.path.splitext(po_path)[0] + ".mo"
    
    try:
        result = subprocess.run(
            ["msgfmt", "-o", mo_path, po_path],
            check=True,
            capture_output=True,
            text=True
        )
        
        if verbose:
            print(f"    Compiled PO → MO: {os.path.basename(po_path)} → {os.path.basename(mo_path)}")
        return True
    
    except FileNotFoundError:
        print(f"  Error: 'msgfmt' command not found. Install gettext first:")
        print(f"         - Linux: sudo apt install gettext")
        print(f"         - macOS: brew install gettext")
        print(f"         - Windows: Download from https://mlocati.github.io/articles/gettext-iconv-windows.html")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  Error: Failed to compile {os.path.basename(po_path)}")
        print(f"    Detailed error: {e.stderr.strip()}")
        return False


# -------------------- Multiprocessing Wrapper Function --------------------
def process_po_wrapper(args):
    """Wrapper for multiprocessing to process single PO file"""
    # 关键修改：不在参数中传递client，而是在子进程内初始化
    po_file_path, lang, translation_kwargs = args
    try:
        # 每个子进程单独初始化客户端
        client = init_client()
        translate_po_file_batch(
            po_path=po_file_path,
            client=client,
            target_lang=lang,** translation_kwargs
        )
    except Exception as e:
        print(f"  Error processing {os.path.basename(po_file_path)}: {str(e)}")


# -------------------- Prompt Construction --------------------
def build_prompt_for_batch(entries: List[polib.POEntry], po_path: str, target_lang: str, start_index: int = 1) -> str:
    """Build a structured prompt for batch translation"""
    if target_lang.startswith("zh"):
        translation_instruction = "Translate the following English content into Simplified Chinese"
    elif target_lang.startswith("en"):
        translation_instruction = "Translate the following non-English content into English (keep original if already in English)"
    else:
        translation_instruction = f"Translate the following content into {target_lang}"

    prompt_parts = []
    header = (f"You are a professional technical document translator specializing in semiconductor and FPGA fields.\n"
              f"{translation_instruction}, while strictly preserving all reStructuredText markup (e.g., :ref:, :doc:, **bold**, ``code``, link tags).\n"
              "DO NOT add any extra explanations—only return valid JSON (follow format requirements below).\n\n"
              "Response Requirements (Critical):\n"
              "1) Output a single JSON object where keys are entry numbers (as strings: e.g., \"1\", \"2\") and values are translation objects.\n"
              "2) For singular entries (no msgid_plural): Value = {\"translation\": \"Translated text here\"}\n"
              "3) For plural entries (with msgid_plural): Value MUST include a \"plural\" key (array of plural translations: e.g., [\"1 item\", \"2+ items\"])\n"
              "4) Maintain consistent technical terminology. NEVER include content other than JSON (no comments, notes, or line breaks).\n\n"
              "Entry List (Translate these):\n")
    prompt_parts.append(header)

    current_idx = start_index
    for entry in entries:
        occurrences = ", ".join([":".join(map(str, occ)) for occ in (entry.occurrences or [])]) or "Unknown location"
        
        prompt_parts.append(f"### Entry {current_idx} \n")
        prompt_parts.append(f"PO File: {po_path} \n")
        prompt_parts.append(f"Source Location: {occurrences} \n")
        if entry.msgctxt:
            prompt_parts.append(f"Context: {entry.msgctxt} \n")
        prompt_parts.append(f"Singular Text to Translate:\n{entry.msgid}\n")
        
        if entry.msgid_plural:
            prompt_parts.append(f"Plural Text to Translate:\n{entry.msgid_plural}\n")
        
        prompt_parts.append("\n" + "-"*50 + "\n")
        current_idx += 1

    prompt_parts.append("JSON Format Example (Replace with YOUR translations—no comments):\n")
    prompt_parts.append("{\n")
    prompt_parts.append('  "1": {"translation": "Device initialization steps"},\n')
    prompt_parts.append('  "2": {"translation": "Configuration file", "plural": ["1 configuration file", "Multiple configuration files"]}\n')
    prompt_parts.append("}\n")

    return "\n".join(prompt_parts)


# -------------------- DeepSeek API Call --------------------
def call_deepseek(client: OpenAI, prompt: str, max_retries: int = 2, temperature: float = 0.0) -> str:
    """Call DeepSeek API with retries for transient errors"""
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=8192
            )
            return response.choices[0].message.content
        
        except Exception as e:
            error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
            print(f"  DeepSeek API call failed (Attempt {attempt}/{max_retries}): {error_msg}")
            
            if attempt < max_retries:
                sleep_time = 1 + 2 * attempt
                print(f"  Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                raise RuntimeError(f"API call failed after {max_retries} retries") from e
    
    raise RuntimeError("Failed to complete DeepSeek API call (unexpected path)")


# -------------------- Parse API Response --------------------
def parse_json_from_response(text: str) -> Any:
    """Parse JSON from API response, handling extra text"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        json_match = re.search(r"(\{[\s\S]*?\}|(\[)[\s\S]*?\])", text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                raise ValueError(f"Extracted JSON fragment failed to parse: {str(e)}") from e
        else:
            raise ValueError("No valid JSON found in API response (model may have added extra text)")


# -------------------- Apply Translations to PO File --------------------
def apply_translations_to_entries(entries: List[polib.POEntry], parsed: Dict[str, Any], start_index: int = 1) -> Tuple[int, int]:
    """Apply parsed translations to POEntry objects"""
    success_count = 0
    failure_count = 0

    for idx, entry in enumerate(entries):
        entry_key = str(start_index + idx)
        
        if entry_key not in parsed:
            print(f"  Warning: No translation found for Entry {entry_key}")
            failure_count += 1
            continue

        translation_data = parsed[entry_key]
        if not isinstance(translation_data, dict) or "translation" not in translation_data:
            print(f"  Warning: Invalid structure for Entry {entry_key} (missing 'translation' key): {translation_data}")
            failure_count += 1
            continue

        entry.msgstr = translation_data["translation"].strip()
        
        if entry.msgid_plural:
            if "plural" in translation_data and isinstance(translation_data["plural"], list):
                entry.msgstr_plural = {str(plural_idx): trans.strip() for plural_idx, trans in enumerate(translation_data["plural"])}
            else:
                print(f"  Warning: Entry {entry_key} has plural text but no valid 'plural' array in response")
                failure_count += 1
                continue

        success_count += 1

    return success_count, failure_count


# -------------------- Core PO File Processing --------------------
def translate_po_file_batch(
    po_path: str,
    client: OpenAI,
    target_lang: str,
    batch_size: int = 10,
    max_chars: int = 8000,
    sleep_secs: float = 1.0,
    dry_run: bool = False,
    save_backup: bool = True,
    verbose: bool = True
):
    """End-to-end processing for a single PO file"""
    if target_lang.strip().lower() == "en":
        repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        source_dir = os.path.join(repo_dir, "docs", "source")
        build_cmd = f"sphinx-build -b html {source_dir} {os.path.join(repo_dir, 'docs', 'build', 'en')}"
        
        print(f"\n[Target Language: {target_lang}] English does not require locale files. Build HTML directly from source:")
        print(f"  Source files location: {source_dir} (includes manual, appendix, __static)")
        print(f"  Command to generate English HTML: {build_cmd}")
        print(f"  Output location after execution: {os.path.join(repo_dir, 'docs', 'build', 'en')}")
        return

    print(f"\n[Target Language: {target_lang}] Processing PO file: {po_path}")
    
    try:
        po_file = polib.pofile(po_path, encoding="utf-8")
    except Exception as e:
        print(f"  Error: Failed to load PO file: {str(e)}")
        return

    untranslated_entries = [entry for entry in po_file if (not entry.obsolete) and (not entry.translated())]
    if not untranslated_entries:
        print(f"  No untranslated entries found. Checking compilation status...")
        if not dry_run:
            compile_po_to_mo(po_path, verbose=verbose)
        return

    batches = chunk_entries(untranslated_entries, batch_size=batch_size, max_chars=max_chars)
    print(f"  Total untranslated entries: {len(untranslated_entries)} → Split into {len(batches)} batches")
    print(f"  Batch constraints: Max {batch_size} entries / {max_chars} characters")

    if save_backup and not dry_run:
        backup_path = f"{po_path}.{target_lang}.bak"
        if not os.path.exists(backup_path) or os.path.getmtime(po_path) > os.path.getmtime(backup_path):
            po_file.save(backup_path)
            print(f"  Created/updated backup file: {backup_path}")

    for batch_num, batch_entries in enumerate(batches, start=1):
        print(f"  Processing Batch {batch_num}/{len(batches)} ({len(batch_entries)} entries)...")
        
        prompt = build_prompt_for_batch(
            entries=batch_entries,
            po_path=po_path,
            target_lang=target_lang,
            start_index=(batch_num - 1) * batch_size + 1
        )

        if dry_run:
            print(f"  [Dry-Run] Prompt Preview (first 1500 chars):\n{prompt[:1500]}...")
            continue

        try:
            api_response = call_deepseek(client, prompt)
        except Exception as e:
            print(f"  Error: Batch {batch_num} API call failed: {str(e)}")
            continue

        try:
            parsed_translations = parse_json_from_response(api_response)
        except ValueError as e:
            print(f"  Error: Batch {batch_num} JSON parsing failed: {str(e)}")
            save_response_debug(po_path, batch_num, target_lang, api_response)
            continue

        if isinstance(parsed_translations, list):
            parsed_translations = {str(i + 1): item for i, item in enumerate(parsed_translations)}

        success, fail = apply_translations_to_entries(
            entries=batch_entries,
            parsed=parsed_translations,
            start_index=(batch_num - 1) * batch_size + 1
        )
        print(f"    Applied translations: {success} successful, {fail} failed")

        po_file.save(po_path)
        print(f"    Saved updates to PO file: {po_path}")

        compile_po_to_mo(po_path, verbose=verbose)
        save_response_debug(po_path, batch_num, target_lang, api_response)
        time.sleep(sleep_secs)

    print(f"[Target Language: {target_lang}] Finished processing {po_path}")


# -------------------- Batch Processing for Locale Directory --------------------
def translate_locale_dir_batches(locale_dir: str, target_langs: List[str], max_workers: int = None, **kwargs):
    """Batch process all PO files in parallel using multiprocessing"""
    if not os.path.exists(locale_dir):
        raise FileNotFoundError(f"Locale directory not found: {locale_dir}")

    max_workers = max_workers or multiprocessing.cpu_count()
    print(f"Using parallel processing with {max_workers} workers")

    tasks = []  # save tasks for multiprocessing

    for lang in target_langs:
        lang_lower = lang.strip().lower()
        
        if lang_lower == "en":
            translate_po_file_batch(
                po_path="N/A (English uses source files)",
                client=None,  # no client needed for English
                target_lang=lang,** kwargs
            )
            continue
        
        po_root_dir = os.path.join(locale_dir, lang, "LC_MESSAGES")
        if not os.path.exists(po_root_dir):
            print(f"Warning: PO directory for {lang} not found: {po_root_dir} → Skipping language")
            continue

        for root, _, files in os.walk(po_root_dir):
            for file in files:
                if file.endswith(".po"):
                    po_file_path = os.path.join(root, file)
                    # key modification: not passing client, will be initialized in subprocess
                    tasks.append((po_file_path, lang, kwargs))

    if tasks:
        with multiprocessing.Pool(processes=max_workers) as pool:
            pool.map(process_po_wrapper, tasks)


# -------------------- Command Line Interface & Main Function --------------------
def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Batch translate Sphinx PO files via DeepSeek API (with parallel processing).")
    parser.add_argument('--locale-dir', default='locales', 
                      help="Root directory of locale files (default: 'locales')")
    parser.add_argument('--target-langs', required=True, 
                      help="Comma-separated list of target languages (e.g., 'en,zh_CN')")
    parser.add_argument('--batch-size', type=int, default=10, 
                      help="Maximum number of entries per API batch (default: 10)")
    parser.add_argument('--max-chars', type=int, default=8000, 
                      help="Maximum characters per batch (controls token usage, default: 8000)")
    parser.add_argument('--sleep', type=float, default=1.0, 
                      help="Seconds to sleep between batches (avoids rate limits, default: 1.0)")
    parser.add_argument('--dry-run', action='store_true', 
                      help="Only print prompts (no API calls or file modifications)")
    parser.add_argument('--no-backup', dest='save_backup', action='store_false', 
                      help="Disable creation of PO file backups")
    parser.add_argument('--verbose', action='store_true', 
                      help="Enable detailed logging output")
    parser.add_argument('--max-workers', type=int, 
                      help=f"Number of parallel workers (default: CPU count, {multiprocessing.cpu_count()})")
    return parser.parse_args()


def main():
    """Main entry point with parallel processing"""
    args = parse_args()
    target_langs = [lang.strip() for lang in args.target_langs.split(',') if lang.strip()]
    if not target_langs:
        raise ValueError("No valid target languages provided. Check --target-langs argument.")

    translation_kwargs = {
        'batch_size': args.batch_size,
        'max_chars': args.max_chars,
        'sleep_secs': args.sleep,
        'dry_run': args.dry_run,
        'save_backup': args.save_backup,
        'verbose': args.verbose
    }

    try:
        translate_locale_dir_batches(
            locale_dir=args.locale_dir,
            target_langs=target_langs,
            max_workers=args.max_workers,
            **translation_kwargs
        )
    except Exception as e:
        print(f"Fatal error during translation: {str(e)}")
        exit(1)

    print("\nBatch processing completed. English HTML can be generated via the provided command.")


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')  # For compatibility across platforms
    main()