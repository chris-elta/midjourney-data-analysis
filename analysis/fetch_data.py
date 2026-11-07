"""Download the succinctly/midjourney-prompts Parquet files and record checksums.

Usage (from the repo root):
    PYTHONPATH=analysis/.deps python3 analysis/fetch_data.py

Writes data/raw/{train,validation,test}.parquet and data/raw/MANIFEST.json
(URL, byte size, SHA-256, download time). Report the SHA-256 values in the
paper so others can confirm they analysed the same files.
"""
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DATASET = "succinctly/midjourney-prompts"
SPLITS = ("train", "validation", "test")
URL = "https://huggingface.co/api/datasets/{ds}/parquet/default/{split}/0.parquet"

RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {"dataset": DATASET, "files": {}}
    for split in SPLITS:
        url = URL.format(ds=DATASET, split=split)
        dest = RAW_DIR / f"{split}.parquet"
        if not dest.exists():
            print(f"downloading {split} ...", file=sys.stderr)
            req = urllib.request.Request(url, headers={"User-Agent": "comp9200-a3"})
            with urllib.request.urlopen(req) as r, dest.open("wb") as f:
                f.write(r.read())
        manifest["files"][split] = {
            "url": url,
            "bytes": dest.stat().st_size,
            "sha256": sha256(dest),
        }
    manifest["checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (RAW_DIR / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
