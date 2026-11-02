"""
Data acquisition module for LendingClub Loan Accepted Dataset.
Downloads the authentic historical loan records from Hugging Face:
https://huggingface.co/datasets/codesignal/lending-club-loan-accepted
Includes automatic resumable retries on network disconnects.
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
import urllib.request

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.config import (
    RAW_DATA_DIR,
    RAW_DATA_PATH,
    RAW_DATA_FILENAME,
    METADATA_DIR,
    DATASET_NAME,
    DATASET_SOURCE_URL,
    DATASET_REPO
)

DOWNLOAD_URL = f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/main/{RAW_DATA_FILENAME}"

def get_remote_file_size(url: str) -> int:
    """Retrieve Content-Length from remote server."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_len = resp.headers.get("Content-Length")
            return int(content_len) if content_len else 0
    except Exception:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_range = resp.headers.get("Content-Range")
            if content_range:
                return int(content_range.split("/")[-1])
            return 0

def download_dataset(force_download: bool = False, max_retries: int = 20) -> Path:
    """
    Download authentic LendingClub dataset from Hugging Face with progress reporting
    and automatic resume on disconnect.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    target_path = RAW_DATA_PATH
    temp_path = RAW_DATA_DIR / f"{RAW_DATA_FILENAME}.part"

    expected_size = get_remote_file_size(DOWNLOAD_URL)
    print(f"Dataset URL: {DOWNLOAD_URL}")
    print(f"Target file: {target_path}")
    print(f"Remote file size: {expected_size / (1024**2):.2f} MB ({expected_size:,} bytes)")

    if target_path.exists() and not force_download:
        actual_size = target_path.stat().st_size
        if expected_size > 0 and actual_size == expected_size:
            print(f"File already exists and size matches ({actual_size:,} bytes). Skipping download.")
            return target_path
        elif expected_size == 0 and actual_size > 100_000_000:
            print(f"File already exists ({actual_size:,} bytes). Skipping download.")
            return target_path
        else:
            print(f"Existing file size ({actual_size:,} bytes) differs from expected ({expected_size:,} bytes). Redownloading...")

    retry_count = 0
    chunk_size = 4 * 1024 * 1024  # 4 MB chunks

    start_time = time.time()
    last_log_time = start_time

    while retry_count < max_retries:
        existing_bytes = temp_path.stat().st_size if temp_path.exists() else 0
        if expected_size > 0 and existing_bytes >= expected_size:
            print(f"Temporary file reached full expected size ({existing_bytes:,} bytes). Finalizing...")
            break

        headers = {"User-Agent": "Mozilla/5.0"}
        if existing_bytes > 0:
            headers["Range"] = f"bytes={existing_bytes}-"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Resuming download from byte {existing_bytes:,} ({existing_bytes/(1024**2):.1f} MB)...")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting new download...")

        req = urllib.request.Request(DOWNLOAD_URL, headers=headers)
        mode = "ab" if existing_bytes > 0 else "wb"

        try:
            with urllib.request.urlopen(req, timeout=45) as resp, open(temp_path, mode) as out_file:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    existing_bytes += len(chunk)

                    current_time = time.time()
                    if current_time - last_log_time >= 15:
                        elapsed = current_time - start_time
                        pct = (existing_bytes / expected_size * 100) if expected_size > 0 else 0
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Downloaded {existing_bytes / (1024**2):.1f} MB / "
                              f"{expected_size / (1024**2):.1f} MB ({pct:.1f}%)")
                        sys.stdout.flush()
                        last_log_time = current_time

            # If loop finished cleanly and size reached
            if expected_size == 0 or temp_path.stat().st_size >= expected_size:
                break
        except Exception as e:
            retry_count += 1
            print(f"Warning: Disconnected ({e}). Retrying ({retry_count}/{max_retries}) in 3 seconds...")
            sys.stdout.flush()
            time.sleep(3)

    final_size = temp_path.stat().st_size if temp_path.exists() else 0
    if expected_size > 0 and final_size < expected_size:
        raise RuntimeError(f"Download incomplete: {final_size:,} bytes of {expected_size:,} bytes downloaded.")

    # Move temp file to final target
    if target_path.exists():
        target_path.unlink()
    temp_path.rename(target_path)

    elapsed_total = time.time() - start_time
    print(f"Download completed successfully in {elapsed_total:.1f}s. Final size: {target_path.stat().st_size:,} bytes.")
    sys.stdout.flush()

    save_metadata(target_path, expected_size)
    return target_path

def save_metadata(file_path: Path, remote_size: int):
    """Record provenance, schema, and statistics metadata."""
    stat = file_path.stat()
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        header_line = f.readline().strip()
        preview_rows = [f.readline().strip() for _ in range(5)]

    columns = [col.strip().strip('"') for col in header_line.split(",")]

    meta = {
        "dataset_name": DATASET_NAME,
        "source_url": DATASET_SOURCE_URL,
        "direct_download_url": DOWNLOAD_URL,
        "retrieval_timestamp": datetime.now().isoformat(),
        "local_file_path": str(file_path),
        "file_name": file_path.name,
        "file_size_bytes": stat.st_size,
        "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
        "expected_remote_size": remote_size,
        "total_columns": len(columns),
        "columns": columns,
        "preview_sample_row_count": len(preview_rows)
    }

    meta_file = METADATA_DIR / "raw_dataset_metadata.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4)
    print(f"Metadata recorded at {meta_file}")
    sys.stdout.flush()

if __name__ == "__main__":
    download_dataset()
