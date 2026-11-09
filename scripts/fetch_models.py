"""Download a model version from its GitHub Release and verify every file against the committed checksum list.

Usage: python scripts/fetch_models.py v1 [v2 ...] [--repo Abhijit26918/cloud-sms] [--dest models]
The file names and SHA-256 values come from models/<version>/model.sha256 (committed in Git); the weights themselves
are only in the Release (tag model-<version>), never in Git.
"""
import argparse
import hashlib
import os
import urllib.request


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("versions", nargs="+")
    ap.add_argument("--repo", default="Abhijit26918/cloud-sms")
    ap.add_argument("--dest", default="models")
    a = ap.parse_args()
    for v in a.versions:
        d = os.path.join(a.dest, v)
        with open(os.path.join(d, "model.sha256"), encoding="utf-8") as f:
            entries = [line.split() for line in f if line.strip()]
        for digest, name in entries:
            path = os.path.join(d, name)
            if os.path.exists(path) and sha256(path) == digest:
                continue
            url = f"https://github.com/{a.repo}/releases/download/model-{v}/{name}"
            print("downloading", url, flush=True)
            urllib.request.urlretrieve(url, path)
            if sha256(path) != digest:
                raise SystemExit(f"checksum mismatch for {path}")
        print(f"{v}: {len(entries)} files verified")


if __name__ == "__main__":
    main()
