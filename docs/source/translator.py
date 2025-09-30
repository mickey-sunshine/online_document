import os
import polib
import time
import json
import argparse
import re
import subprocess
from openai import OpenAI
from typing import List, Dict, Tuple, Any


# -------------------- Initialize DeepSeek Client --------------------
def init_client():
    """Initialize OpenAI-compatible client for DeepSeek API."""
    api_key = "sk-70406818a671408b80f43720b7978aab"  # Hardcoded API key
    if not api_key:
        raise EnvironmentError("DeepSeek API Key is not set")
    
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


# -------------------- Utility Functions --------------------
def chunk_entries(entries: List[polib.POEntry], batch_size: int, max_chars: int) -> List[List[polib.POEntry]]:
    """Chunk PO entries to fit API token constraints."""
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
    """Save raw API responses for debugging (only in verbose mode)."""
    debug_dir = os.path.join("responses", target_lang)
    os.makedirs(debug_dir, exist_ok=True)
    debug_filename = os.path.join(debug_dir, f"{os.path.basename(po_path)}.batch{batch_index}.resp.txt")
    with open(debug_filename, "w", encoding="utf-8") as f:
        f.write(content)


def compile_po_to_mo(po_path: str, verbose: bool = True) -> bool:
    """Compile .po file to .mo (binary) using msgfmt."""
    mo_path = os.path.splitext(po_path)[0] + ".mo"
    
    try:
        result = subprocess.run(
            ["msgfmt", "-o", mo_path, po_path],
            check=True,
            capture_output=True,
            text=True
        )
        if verbose:
            print(f"    Compiled PO → MO: {os.path.basename(po_path)}")
        return True
    
    except FileNotFoundError:
        print(f"  Error: 'msgfmt' not found. Install gettext (sudo apt install gettext)")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  Error compiling {os.path.basename(po_path)}: {e.stderr.strip()}")
        return False


# -------------------- Prompt Construction --------------------
def build_prompt_for_batch(entries: List[polib.POEntry], po_path: str, target_lang: str, start_index: int = 1) -> str:
    """Build structured prompt for batch translation."""
    if target_lang.startswith("zh"):
        translation_instruction = "Translate English to Simplified Chinese"
    elif target_lang.startswith("en"):
        translation_instruction = "Translate non-English to English"
    else:
        translation_instruction = f"Translate to {target_lang}"

    prompt_parts = [
        f"You are a technical translator specializing in semiconductors and FPGAs.\n"
        f"{translation_instruction}, preserving reStructuredText markup (e.g., :ref:, **bold**, ``code``).\n"
        "Return ONLY valid JSON (no extra text). Format:\n"
        "- Singular: {\"1\": {\"translation\": \"text\"}}\n"
        "- Plural: {\"2\": {\"translation\": \"text\", \"plural\": [\"plural1\", \"plural2\"]}}\n\n"
        "Entries to translate:\n"
    ]

    current_idx = start_index
    for entry in entries:
        occurrences = ", ".join([":".join(map(str, occ)) for occ in (entry.occurrences or [])]) or "Unknown"
        prompt_parts.append(f"### Entry {current_idx}\n")
        prompt_parts.append(f"File: {po_path}\n")
        prompt_parts.append(f"Location: {occurrences}\n")
        if entry.msgctxt:
            prompt_parts.append(f"Context: {entry.msgctxt}\n")
        prompt_parts.append(f"Text: {entry.msgid}\n")
        if entry.msgid_plural:
            prompt_parts.append(f"Plural Text: {entry.msgid_plural}\n")
        prompt_parts.append("\n" + "-"*50 + "\n")
        current_idx += 1

    prompt_parts.append("JSON Example:\n")
    prompt_parts.append("{\n")
    prompt_parts.append('  "1": {"translation": "Device initialization"}\n')
    prompt_parts.append("}\n")

    return "\n".join(prompt_parts)


# -------------------- DeepSeek API Call --------------------
def call_deepseek(client: OpenAI, prompt: str, max_retries: int = 2, temperature: float = 0.0) -> str:
    """Call DeepSeek API with retries for transient errors."""
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
            print(f"  API failed (Attempt {attempt}/{max_retries}): {error_msg}")
            
            if attempt < max_retries:
                sleep_time = 1 + 2 * attempt
                time.sleep(sleep_time)
            else:
                raise RuntimeError(f"API failed after {max_retries} retries") from e
    
    raise RuntimeError("API call failed unexpectedly")


# -------------------- Parse API Response --------------------
def parse_json_from_response(text: str) -> Any:
    """Parse JSON from API response (handle extra text)."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        json_match = re.search(r"(\{[\s\S]*?\}|(\[)[\s\S]*?\])", text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON fragment: {str(e)}") from e
        else:
            raise ValueError("No valid JSON in response")


# -------------------- Apply Translations --------------------
def apply_translations_to_entries(entries: List[polib.POEntry], parsed: Dict[str, Any], start_index: int = 1) -> Tuple[int, int]:
    """Apply parsed translations to PO entries."""
    success_count = 0
    failure_count = 0

    for idx, entry in enumerate(entries):
        entry_key = str(start_index + idx)
        
        if entry_key not in parsed:
            print(f"  Warning: No translation for Entry {entry_key}")
            failure_count += 1
            continue

        translation_data = parsed[entry_key]
        if not isinstance(translation_data, dict) or "translation" not in translation_data:
            print(f"  Warning: Invalid structure for Entry {entry_key}")
            failure_count += 1
            continue

        entry.msgstr = translation_data["translation"].strip()
        
        if entry.msgid_plural:
            if "plural" in translation_data and isinstance(translation_data["plural"], list):
                entry.msgstr_plural = {str(i): t.strip() for i, t in enumerate(translation_data["plural"])}
            else:
                print(f"  Warning: Missing plural for Entry {entry_key}")
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
    """Process a single PO file with batch translation."""
    if verbose:
        print(f"\n[Processing {target_lang}] {po_path}")
    
    try:
        po_file = polib.pofile(po_path, encoding="utf-8")
    except Exception as e:
        print(f"  Error loading PO file: {str(e)}")
        return

    # Skip fully translated files (critical optimization)
    untranslated_entries = [e for e in po_file if (not e.obsolete) and (not e.translated())]
    if not untranslated_entries:
        if verbose:
            print(f"  No untranslated entries. Skipping.")
        compile_po_to_mo(po_path, verbose=verbose)
        return

    batches = chunk_entries(untranslated_entries, batch_size=batch_size, max_chars=max_chars)
    if verbose:
        print(f"  {len(untranslated_entries)} entries → {len(batches)} batches")

    # Save backup only if needed
    if save_backup and not dry_run:
        backup_path = f"{po_path}.{target_lang}.bak"
        po_file.save(backup_path)
        if verbose:
            print(f"  Created backup: {backup_path}")

    # Process batches
    for batch_num, batch_entries in enumerate(batches, start=1):
        if verbose:
            print(f"  Batch {batch_num}/{len(batches)} ({len(batch_entries)} entries)")
        
        prompt = build_prompt_for_batch(
            entries=batch_entries,
            po_path=po_path,
            target_lang=target_lang,
            start_index=(batch_num - 1) * batch_size + 1
        )

        if dry_run:
            if verbose:
                print(f"  [Dry Run] Prompt preview:\n{prompt[:500]}...")
            continue

        try:
            api_response = call_deepseek(client, prompt)
        except Exception as e:
            print(f"  Batch {batch_num} failed: {str(e)}")
            continue

        try:
            parsed_translations = parse_json_from_response(api_response)
        except ValueError as e:
            print(f"  Batch {batch_num} JSON error: {str(e)}")
            save_response_debug(po_path, batch_num, target_lang, api_response)
            continue

        # Convert list responses to dict
        if isinstance(parsed_translations, list):
            parsed_translations = {str(i + 1): item for i, item in enumerate(parsed_translations)}

        success, fail = apply_translations_to_entries(
            entries=batch_entries,
            parsed=parsed_translations,
            start_index=(batch_num - 1) * batch_size + 1
        )
        if verbose:
            print(f"    Applied: {success} success, {fail} failed")

        po_file.save(po_path)
        compile_po_to_mo(po_path, verbose=verbose)

        if verbose:
            save_response_debug(po_path, batch_num, target_lang, api_response)

        time.sleep(sleep_secs)

    if verbose:
        print(f"[Completed {target_lang}] {po_path}")


# -------------------- Batch Processing --------------------
def translate_locale_dir_batches(locale_dir: str, target_langs: List[str], **kwargs):
    """Process all PO files in locale directory for target languages."""
    if not os.path.exists(locale_dir):
        raise FileNotFoundError(f"Locale directory not found: {locale_dir}")

    client = init_client()  # Reuse client for all languages

    for lang in target_langs:
        po_root_dir = os.path.join(locale_dir, lang, "LC_MESSAGES")
        if not os.path.exists(po_root_dir):
            print(f"Warning: {lang} directory not found: {po_root_dir} → Skipping")
            continue

        for root, _, files in os.walk(po_root_dir):
            for file in files:
                if file.endswith(".po"):
                    po_file_path = os.path.join(root, file)
                    # Pre-check for untranslated entries (skip if none)
                    try:
                        po_file = polib.pofile(po_file_path, encoding="utf-8")
                        untranslated = [e for e in po_file if not e.obsolete and not e.translated()]
                        if not untranslated:
                            if kwargs.get('verbose'):
                                print(f"  No untranslated entries in {po_file_path} → Skipping")
                            compile_po_to_mo(po_file_path, verbose=kwargs.get('verbose'))
                            continue
                    except Exception as e:
                        print(f"  Error checking {po_file_path}: {str(e)} → Skipping")
                        continue
                    # Process only if untranslated entries exist
                    try:
                        translate_po_file_batch(po_file_path, client, lang,** kwargs)
                    except Exception as e:
                        print(f"Error processing {po_file_path}: {str(e)}")
                        continue


# -------------------- CLI & Main --------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Batch translate PO files via DeepSeek API")
    parser.add_argument('--locale-dir', default='locales', 
                      help="Root directory of locale files (default: 'locales')")
    parser.add_argument('--target-langs', required=True, 
                      help="Comma-separated target languages (e.g., 'zh_CN,en')")
    parser.add_argument('--batch-size', type=int, default=10, 
                      help="Entries per API batch (default: 10)")
    parser.add_argument('--max-chars', type=int, default=12000,  # Increased default
                      help="Max characters per batch (default: 12000)")
    parser.add_argument('--sleep', type=float, default=1.0, 
                      help="Seconds between batches (default: 1.0)")
    parser.add_argument('--dry-run', action='store_true', 
                      help="Print prompts only (no API calls)")
    parser.add_argument('--no-backup', dest='save_backup', action='store_false', 
                      help="Disable PO file backups")
    parser.add_argument('--no-verbose', dest='verbose', action='store_false', 
                      help="Disable detailed logs")
    return parser.parse_args()


def main():
    args = parse_args()
    target_langs = [lang.strip() for lang in args.target_langs.split(',') if lang.strip()]
    if not target_langs:
        raise ValueError("No valid target languages provided")

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
            **translation_kwargs
        )
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        exit(1)

    print("\nBatch translation completed!")


if __name__ == '__main__':
    main()