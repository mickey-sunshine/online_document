import os
import polib
import time
import json
import argparse
import re
from openai import OpenAI
from typing import List, Dict, Tuple, Any


# -------------------- Initialize DeepSeek Client --------------------
def init_client():
    # Hardcoded API Key (as requested)
    api_key = "sk-70406818a671408b80f43720b7978aab"
    if not api_key:
        raise EnvironmentError("DeepSeek API Key is not set (check hardcoded value in init_client())")
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    return client


# -------------------- Utility Functions --------------------
def chunk_entries(entries: List[polib.POEntry], batch_size: int, max_chars: int) -> List[List[polib.POEntry]]:
    """Chunk entries by both count and character limit. Returns a list of batches, each containing a group of entries."""
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
    """Save raw API responses for debugging, organized by target language."""
    debug_dir = os.path.join("responses", target_lang)
    os.makedirs(debug_dir, exist_ok=True)
    
    debug_filename = os.path.join(debug_dir, f"{os.path.basename(po_path)}.batch{batch_index}.resp.txt")
    with open(debug_filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"  Saved raw response to {debug_filename}")


# -------------------- Prompt Construction (Multi-Language Support) --------------------
def build_prompt_for_batch(entries: List[polib.POEntry], po_path: str, target_lang: str, start_index: int = 1) -> str:
    """Build a prompt for a batch of entries, dynamically adjusting translation direction based on target language."""
    if target_lang.startswith("zh"):
        translation_instruction = "Translate the following English content into Simplified Chinese"
    elif target_lang.startswith("en"):
        translation_instruction = "Translate the following non-English content into English (keep original if already in English)"
    else:
        translation_instruction = f"Translate the following content into {target_lang}"

    prompt_parts = []
    header = (f"You are a professional technical document translator specializing in semiconductor and FPGA fields.\n"
              f"{translation_instruction}, while preserving all reStructuredText markup (e.g., :ref:, :doc:, **bold**, ``code``, link tags).\n"
              "DO NOT add any extra explanations—only return valid JSON (see format requirements below).\n\n"
              "Response Requirements (Critical):\n"
              "1) Output a single JSON object where keys are entry numbers (as strings, e.g., \"1\", \"2\") and values are translation objects.\n"
              "2) For singular entries: Value = {\"translation\": \"Translated text\"}\n"
              "3) For plural entries (with msgid_plural): Value must include a \"plural\" key (array of plural translations, e.g., [\"Form 1\", \"Form 2\"]).\n"
              "4) Maintain consistent terminology. NEVER include content other than JSON (no comments, explanations, or line breaks).\n\n"
              "Entry List:\n")
    prompt_parts.append(header)

    current_idx = start_index
    for entry in entries:
        occurrences = ", ".join([":".join(map(str, occ)) for occ in (entry.occurrences or [])]) or "Unknown location"
        
        prompt_parts.append(f"### Entry {current_idx} \n")
        prompt_parts.append(f"PO File: {po_path} \n")
        prompt_parts.append(f"Occurrences: {occurrences} \n")
        if entry.msgctxt:
            prompt_parts.append(f"Context: {entry.msgctxt} \n")
        prompt_parts.append(f"Singular Text:\n{entry.msgid}\n")
        
        if entry.msgid_plural:
            prompt_parts.append(f"Plural Text:\n{entry.msgid_plural}\n")
        
        prompt_parts.append("\n" + "-"*50 + "\n")
        current_idx += 1

    prompt_parts.append("JSON Format Example (Replace with actual translations—no comments):\n")
    prompt_parts.append("{\n")
    prompt_parts.append('  "1": {"translation": "Device initialization steps"},\n')
    prompt_parts.append('  "2": {"translation": "Configuration file", "plural": ["1 configuration file", "Multiple configuration files"]}\n')
    prompt_parts.append("}\n")

    return "\n".join(prompt_parts)


# -------------------- DeepSeek API Call --------------------
def call_deepseek(client: OpenAI, prompt: str, max_retries: int = 2, temperature: float = 0.0) -> str:
    """Call DeepSeek API via OpenAI-compatible client. Retry on failures."""
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
            print(f"  DeepSeek API call failed (Attempt {attempt}/{max_retries}): {str(e)[:100]}")
            if attempt < max_retries:
                time.sleep(1 + 2 * attempt)
            else:
                raise RuntimeError(f"API call failed after {max_retries} retries") from e
    
    raise RuntimeError("Failed to complete DeepSeek API call")


# -------------------- Parse API Response --------------------
def parse_json_from_response(text: str) -> Any:
    """Parse JSON from API response. Handle cases where extra text surrounds the JSON."""
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
    """Apply parsed translations to PO entries. Return (success_count, failure_count)."""
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
    """Process a single PO file: collect untranslated entries → batch → API call → parse → write back."""
    print(f"\n[Target Language: {target_lang}] Processing PO file: {po_path}")
    
    try:
        po_file = polib.pofile(po_path, encoding="utf-8")
    except Exception as e:
        print(f"  Error: Failed to load PO file: {str(e)}")
        return

    untranslated_entries = [entry for entry in po_file if (not entry.obsolete) and (not entry.translated())]
    if not untranslated_entries:
        print(f"  No untranslated entries found. Skipping.")
        return

    batches = chunk_entries(untranslated_entries, batch_size=batch_size, max_chars=max_chars)
    print(f"  Total untranslated entries: {len(untranslated_entries)} → Split into {len(batches)} batches (max {batch_size} entries / {max_chars} chars per batch)")

    if save_backup:
        backup_path = f"{po_path}.{target_lang}.bak"
        po_file.save(backup_path)
        print(f"  Created backup file: {backup_path}")

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
        print(f"    Saved updates to: {po_path}")

        save_response_debug(po_path, batch_num, target_lang, api_response)
        time.sleep(sleep_secs)

    print(f"[Target Language: {target_lang}] Finished processing {po_path}")


# -------------------- Batch Processing for Locale Directory --------------------
def translate_locale_dir_batches(locale_dir: str, target_langs: List[str], **kwargs):
    """Batch process all PO files in the locale directory for multiple target languages."""
    if not os.path.exists(locale_dir):
        raise FileNotFoundError(f"Locale directory not found: {locale_dir}")

    client = init_client()

    for lang in target_langs:
        po_root_dir = os.path.join(locale_dir, lang, "LC_MESSAGES")
        if not os.path.exists(po_root_dir):
            print(f"Warning: PO directory for {lang} not found: {po_root_dir} → Skipping this language")
            continue

        for root, _, files in os.walk(po_root_dir):
            for file in files:
                if file.endswith(".po"):
                    po_file_path = os.path.join(root, file)
                    try:
                        translate_po_file_batch(po_file_path, client, lang,** kwargs)
                    except Exception as e:
                        print(f"Error: Failed to process {po_file_path}: {str(e)}")
                        continue


# -------------------- Command Line Interface (CLI) & Main Function --------------------
def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Batch translate Sphinx PO files via DeepSeek (supports multiple target languages).")
    parser.add_argument('--locale-dir', default='locales', help="Sphinx locale directory path (default: 'locales')")
    parser.add_argument('--target-langs', required=True, help="Comma-separated target languages (e.g., 'zh_CN,en')")
    parser.add_argument('--batch-size', type=int, default=10, help="Max number of entries per batch (default: 10)")
    parser.add_argument('--max-chars', type=int, default=8000, help="Max characters per batch (controls token size, default: 8000)")
    parser.add_argument('--sleep', type=float, default=1.0, help="Seconds between batches to avoid rate limits (default: 1.0)")
    parser.add_argument('--dry-run', action='store_true', help="Only print prompts without calling API")
    parser.add_argument('--no-backup', dest='save_backup', action='store_false', help="Disable backup of PO files")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose output")
    return parser.parse_args()


def main():
    """Main execution function: parse args → start translation."""
    args = parse_args()
    # Convert comma-separated target languages to list
    target_langs = [lang.strip() for lang in args.target_langs.split(',') if lang.strip()]
    
    if not target_langs:
        raise ValueError("No valid target languages provided (check --target-langs)")

    # Prepare keyword arguments for translation functions
    translation_kwargs = {
        'batch_size': args.batch_size,
        'max_chars': args.max_chars,
        'sleep_secs': args.sleep,
        'dry_run': args.dry_run,
        'save_backup': args.save_backup,
        'verbose': args.verbose
    }

    # Start batch translation for all target languages
    translate_locale_dir_batches(
        locale_dir=args.locale_dir,
        target_langs=target_langs,
        **translation_kwargs
    )


if __name__ == '__main__':
    main()