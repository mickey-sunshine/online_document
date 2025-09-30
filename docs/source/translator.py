import os
import polib
import time
import json
import argparse
import re
import subprocess  # For calling msgfmt command (PO → MO compilation)
from openai import OpenAI
from typing import List, Dict, Tuple, Any


# -------------------- Initialize DeepSeek Client --------------------
def init_client():
    """Initialize OpenAI-compatible client for DeepSeek API with hardcoded API key."""
    # Hardcoded API Key (as requested by user)
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
    
    Args:
        entries: List of untranslated POEntry objects
        batch_size: Max number of entries per batch
        max_chars: Max total characters per batch (estimated from msgid/msgid_plural)
    
    Returns:
        List of batches, each containing a subset of POEntry objects
    """
    batches = []
    current_batch = []
    current_char_count = 0

    for entry in entries:
        # Estimate character count (include singular + plural if present)
        entry_char_est = len(entry.msgid) + (len(entry.msgid_plural) if entry.msgid_plural else 0)
        
        # Split into new batch if current batch exceeds limits (preserve single large entries)
        if current_batch and (len(current_batch) >= batch_size or current_char_count + entry_char_est > max_chars):
            batches.append(current_batch)
            current_batch = []
            current_char_count = 0
        
        current_batch.append(entry)
        current_char_count += entry_char_est

    # Add remaining entries as the last batch
    if current_batch:
        batches.append(current_batch)
    
    return batches


def save_response_debug(po_path: str, batch_index: int, target_lang: str, content: str):
    """
    Save raw API responses to debug directory for troubleshooting JSON parsing failures.
    
    Args:
        po_path: Path to the PO file being processed
        batch_index: Batch number (for file naming)
        target_lang: Target language code (e.g., zh_CN, en)
        content: Raw API response text
    """
    # Create debug directory (organized by target language)
    debug_dir = os.path.join("responses", target_lang)
    os.makedirs(debug_dir, exist_ok=True)
    
    # Generate debug filename with PO name and batch number
    debug_filename = os.path.join(debug_dir, f"{os.path.basename(po_path)}.batch{batch_index}.resp.txt")
    with open(debug_filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"  Saved raw response to {debug_filename}")


def compile_po_to_mo(po_path: str, verbose: bool = True) -> bool:
    """
    Compile .po file to binary .mo file using msgfmt (from gettext toolset).
    
    Args:
        po_path: Full path to the source .po file
        verbose: Whether to print compilation status logs
    
    Returns:
        True if compilation succeeds, False otherwise
    """
    # Generate .mo file path (same directory and name as .po file)
    mo_path = os.path.splitext(po_path)[0] + ".mo"
    
    try:
        # Execute msgfmt command: msgfmt -o <output.mo> <input.po>
        result = subprocess.run(
            ["msgfmt", "-o", mo_path, po_path],
            check=True,          # Raise error if command exits with non-zero code
            capture_output=True, # Capture stdout/stderr for debugging
            text=True            # Treat output as text (not binary)
        )
        
        if verbose:
            print(f"    Compiled PO → MO: {os.path.basename(po_path)} → {os.path.basename(mo_path)}")
        return True
    
    except FileNotFoundError:
        # msgfmt command not found (gettext not installed)
        print(f"  Error: 'msgfmt' command not found. Install gettext first:")
        print(f"         - Linux: sudo apt install gettext")
        print(f"         - macOS: brew install gettext")
        print(f"         - Windows: Download from https://mlocati.github.io/articles/gettext-iconv-windows.html")
        return False
    
    except subprocess.CalledProcessError as e:
        # msgfmt failed (e.g., invalid PO file syntax)
        print(f"  Error: Failed to compile {os.path.basename(po_path)}")
        print(f"    Detailed error: {e.stderr.strip()}")
        return False


# -------------------- Prompt Construction (Multi-Language Support) --------------------
def build_prompt_for_batch(entries: List[polib.POEntry], po_path: str, target_lang: str, start_index: int = 1) -> str:
    """
    Build a structured prompt for batch translation, tailored to target language.
    
    Ensures the model returns ONLY valid JSON with translations, preserving reStructuredText markup.
    
    Args:
        entries: List of POEntry objects in the current batch
        po_path: Path to the PO file (for context in prompt)
        target_lang: Target language code (e.g., zh_CN, en)
        start_index: Starting entry number (for consistent numbering across batches)
    
    Returns:
        Formatted prompt string for DeepSeek API
    """
    # Set translation direction based on target language
    if target_lang.startswith("zh"):
        translation_instruction = "Translate the following English content into Simplified Chinese"
    elif target_lang.startswith("en"):
        translation_instruction = "Translate the following non-English content into English (keep original if already in English)"
    else:
        translation_instruction = f"Translate the following content into {target_lang}"

    prompt_parts = []
    # Prompt header: Define role, rules, and JSON format
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

    # Add each entry's context and content to the prompt
    current_idx = start_index
    for entry in entries:
        # Format occurrence info (file path + line number) for context
        occurrences = ", ".join([":".join(map(str, occ)) for occ in (entry.occurrences or [])]) or "Unknown location"
        
        prompt_parts.append(f"### Entry {current_idx} \n")
        prompt_parts.append(f"PO File: {po_path} \n")
        prompt_parts.append(f"Source Location: {occurrences} \n")
        if entry.msgctxt:  # Include context if available (improves translation accuracy)
            prompt_parts.append(f"Context: {entry.msgctxt} \n")
        prompt_parts.append(f"Singular Text to Translate:\n{entry.msgid}\n")
        
        # Add plural text if the entry has it
        if entry.msgid_plural:
            prompt_parts.append(f"Plural Text to Translate:\n{entry.msgid_plural}\n")
        
        # Add separator for readability
        prompt_parts.append("\n" + "-"*50 + "\n")
        current_idx += 1

    # Add JSON example to reinforce correct format
    prompt_parts.append("JSON Format Example (Replace with YOUR translations—no comments):\n")
    prompt_parts.append("{\n")
    prompt_parts.append('  "1": {"translation": "Device initialization steps"},\n')
    prompt_parts.append('  "2": {"translation": "Configuration file", "plural": ["1 configuration file", "Multiple configuration files"]}\n')
    prompt_parts.append("}\n")

    return "\n".join(prompt_parts)


# -------------------- DeepSeek API Call --------------------
def call_deepseek(client: OpenAI, prompt: str, max_retries: int = 2, temperature: float = 0.0) -> str:
    """
    Call DeepSeek API with retries for transient errors (e.g., network issues, rate limits).
    
    Args:
        client: Initialized OpenAI-compatible client
        prompt: Formatted prompt string
        max_retries: Number of retries on failure (default: 2)
        temperature: Model creativity (0.0 = stable/consistent for technical translation)
    
    Returns:
        Raw API response content (model's output)
    
    Raises:
        RuntimeError: If API call fails after all retries
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=8192  # Align with DeepSeek's model token limit
            )
            return response.choices[0].message.content
        
        except Exception as e:
            # Truncate error message to 100 chars for readability
            error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
            print(f"  DeepSeek API call failed (Attempt {attempt}/{max_retries}): {error_msg}")
            
            # Exponential backoff to avoid rate limits
            if attempt < max_retries:
                sleep_time = 1 + 2 * attempt
                print(f"  Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                raise RuntimeError(f"API call failed after {max_retries} retries") from e
    
    raise RuntimeError("Failed to complete DeepSeek API call (unexpected path)")


# -------------------- Parse API Response --------------------
def parse_json_from_response(text: str) -> Any:
    """
    Parse JSON from API response, handling cases where the model adds extra text.
    
    Args:
        text: Raw API response text
    
    Returns:
        Parsed JSON object (dict or list)
    
    Raises:
        ValueError: If no valid JSON is found or parsing fails
    """
    # First try direct JSON parsing (ideal case: model returns only JSON)
    try:
        return json.loads(text)
    
    except json.JSONDecodeError:
        # Extract first valid JSON block (handles extra explanatory text)
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
    """
    Apply parsed JSON translations to POEntry objects.
    
    Args:
        entries: List of POEntry objects to update
        parsed: Parsed JSON translations (dict with entry numbers as keys)
        start_index: Starting entry number (matches prompt numbering)
    
    Returns:
        Tuple (success_count, failure_count): Number of entries updated successfully/failed
    """
    success_count = 0
    failure_count = 0

    for idx, entry in enumerate(entries):
        entry_key = str(start_index + idx)  # Match entry numbering in the prompt
        
        # Skip if no translation exists for this entry
        if entry_key not in parsed:
            print(f"  Warning: No translation found for Entry {entry_key}")
            failure_count += 1
            continue

        translation_data = parsed[entry_key]
        # Validate translation structure (must have "translation" key)
        if not isinstance(translation_data, dict) or "translation" not in translation_data:
            print(f"  Warning: Invalid structure for Entry {entry_key} (missing 'translation' key): {translation_data}")
            failure_count += 1
            continue

        # Apply singular translation
        entry.msgstr = translation_data["translation"].strip()
        
        # Apply plural translation if the entry requires it
        if entry.msgid_plural:
            if "plural" in translation_data and isinstance(translation_data["plural"], list):
                # polib expects msgstr_plural to be a dict (key: plural index string)
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
    """
    End-to-end processing for a single PO file:
    1. Load PO file and collect untranslated entries
    2. Chunk entries into batches
    3. Translate batches via DeepSeek API
    4. Apply translations to PO file
    5. Save updated PO file
    6. Compile PO → MO (auto-compilation)
    
    Args:
        po_path: Full path to the PO file
        client: Initialized DeepSeek client
        target_lang: Target language code (e.g., zh_CN, en)
        batch_size: Max entries per API call (default: 10)
        max_chars: Max characters per batch (default: 8000)
        sleep_secs: Seconds to sleep between batches (rate limit avoidance)
        dry_run: If True, print prompts only (no API calls/compilation)
        save_backup: If True, create a backup of the original PO file
        verbose: If True, print detailed processing logs
    """
    print(f"\n[Target Language: {target_lang}] Processing PO file: {po_path}")
    
    # Load PO file with UTF-8 encoding (supports multi-language content)
    try:
        po_file = polib.pofile(po_path, encoding="utf-8")
    except Exception as e:
        print(f"  Error: Failed to load PO file: {str(e)}")
        return

    # Filter untranslated, non-obsolete entries (skip already translated content)
    untranslated_entries = [entry for entry in po_file if (not entry.obsolete) and (not entry.translated())]
    if not untranslated_entries:
        print(f"  No untranslated entries found. Skipping translation.")
        # Still compile PO → MO if .mo is missing (for consistency)
        if not dry_run:
            compile_po_to_mo(po_path, verbose=verbose)
        return

    # Split entries into batches (fit API token limits)
    batches = chunk_entries(untranslated_entries, batch_size=batch_size, max_chars=max_chars)
    print(f"  Total untranslated entries: {len(untranslated_entries)} → Split into {len(batches)} batches")
    print(f"  Batch constraints: Max {batch_size} entries / {max_chars} characters")

    # Create backup of original PO file before modification
    if save_backup and not dry_run:
        backup_path = f"{po_path}.{target_lang}.bak"
        po_file.save(backup_path)
        print(f"  Created backup file: {backup_path}")

    # Process each batch sequentially
    for batch_num, batch_entries in enumerate(batches, start=1):
        print(f"  Processing Batch {batch_num}/{len(batches)} ({len(batch_entries)} entries)...")
        
        # Build prompt for current batch
        prompt = build_prompt_for_batch(
            entries=batch_entries,
            po_path=po_path,
            target_lang=target_lang,
            start_index=(batch_num - 1) * batch_size + 1  # Continuous numbering across batches
        )

        # Dry-run mode: print prompt preview without API calls
        if dry_run:
            print(f"  [Dry-Run] Prompt Preview (first 1500 chars):\n{prompt[:1500]}...")
            continue

        # Call DeepSeek API to get translations
        try:
            api_response = call_deepseek(client, prompt)
        except Exception as e:
            print(f"  Error: Batch {batch_num} API call failed: {str(e)}")
            continue

        # Parse JSON response from API
        try:
            parsed_translations = parse_json_from_response(api_response)
        except ValueError as e:
            print(f"  Error: Batch {batch_num} JSON parsing failed: {str(e)}")
            save_response_debug(po_path, batch_num, target_lang, api_response)
            continue

        # Convert list responses to dict (if model returns list instead of object)
        if isinstance(parsed_translations, list):
            parsed_translations = {str(i + 1): item for i, item in enumerate(parsed_translations)}

        # Apply parsed translations to PO entries
        success, fail = apply_translations_to_entries(
            entries=batch_entries,
            parsed=parsed_translations,
            start_index=(batch_num - 1) * batch_size + 1
        )
        print(f"    Applied translations: {success} successful, {fail} failed")

        # Save updated PO file
        po_file.save(po_path)
        print(f"    Saved updates to PO file: {po_path}")

        # Auto-compile PO → MO after saving updates
        compile_po_to_mo(po_path, verbose=verbose)

        # Save raw response for debugging
        save_response_debug(po_path, batch_num, target_lang, api_response)

        # Sleep between batches to avoid rate limits
        time.sleep(sleep_secs)

    print(f"[Target Language: {target_lang}] Finished processing {po_path}")


# -------------------- Batch Processing for Locale Directory --------------------
def translate_locale_dir_batches(locale_dir: str, target_langs: List[str], **kwargs):
    """
    Batch process all PO files in a locale directory for multiple target languages.
    
    Args:
        locale_dir: Root directory containing language-specific subdirectories (e.g., locale/zh_CN)
        target_langs: List of target language codes (e.g., ["zh_CN", "en"])
       ** kwargs: Additional parameters passed to translate_po_file_batch()
    """
    if not os.path.exists(locale_dir):
        raise FileNotFoundError(f"Locale directory not found: {locale_dir}")

    # Initialize API client (reused across all languages/files)
    client = init_client()

    # Process each target language
    for lang in target_langs:
        # Sphinx standard PO file path: locale/<lang>/LC_MESSAGES
        po_root_dir = os.path.join(locale_dir, lang, "LC_MESSAGES")
        if not os.path.exists(po_root_dir):
            print(f"Warning: PO directory for {lang} not found: {po_root_dir} → Skipping language")
            continue

        # Traverse all PO files in the language's LC_MESSAGES directory
        for root, _, files in os.walk(po_root_dir):
            for file in files:
                if file.endswith(".po"):
                    po_file_path = os.path.join(root, file)
                    try:
                        translate_po_file_batch(po_file_path, client, lang, **kwargs)
                    except Exception as e:
                        print(f"Error: Failed to process {po_file_path}: {str(e)}")
                        continue


# -------------------- Command Line Interface (CLI) & Main Function --------------------
def parse_args():
    """Parse command line arguments for the translation script."""
    parser = argparse.ArgumentParser(description="Batch translate Sphinx PO files via DeepSeek API with auto PO→MO compilation.")
    parser.add_argument('--locale-dir', default='locales', 
                      help="Root directory of locale files (default: 'locales')")
    parser.add_argument('--target-langs', required=True, 
                      help="Comma-separated list of target languages (e.g., 'zh_CN,en')")
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
    return parser.parse_args()


def main():
    """Main entry point: parse arguments and start batch translation."""
    # Parse command line arguments
    args = parse_args()
    
    # Validate and process target languages
    target_langs = [lang.strip() for lang in args.target_langs.split(',') if lang.strip()]
    if not target_langs:
        raise ValueError("No valid target languages provided. Check --target-langs argument.")

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
    try:
        translate_locale_dir_batches(
            locale_dir=args.locale_dir,
            target_langs=target_langs,** translation_kwargs
        )
    except Exception as e:
        print(f"Fatal error during translation: {str(e)}")
        exit(1)

    print("\nBatch translation completed successfully!")


if __name__ == '__main__':
    main()