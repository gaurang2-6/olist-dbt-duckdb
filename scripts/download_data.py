"""Download the seven Olist tables into data/raw/ and check each file's SHA-256.

    python scripts/download_data.py
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/tunguyenn99/ecommerce-data-modeling/HEAD/dataset/"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
FILES = {
    "olist_customers_dataset.csv": "983a422239e1712ded753b3bf9ecf47dc73f144d306029dcfa99e70a226883d2",
    "olist_order_items_dataset.csv": "0bc4d068c4fe38cbb01bd90e8746e3c613fe7b4baef75fab7b0e329701c3e279",
    "olist_order_payments_dataset.csv": "4f713964f2815dbbaa40b9488268c55aac3627bfce5aa96cf58d1f3616de3cc0",
    "olist_order_reviews_dataset.csv": "012b61c7593e34f51fa614efdf802b9c7056ce6aae5307ddb93236e7cfc797d7",
    "olist_orders_dataset.csv": "8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf",
    "olist_products_dataset.csv": "3e6569628a17fbc75fd206ee357b59e20364b9afa90f5b6cd5b4d624c58aa9cc",
    "olist_sellers_dataset.csv": "1f643d2b950373b85735e7794b20986f528d7a000432e7c6f9bcbb44d0846a0e",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for name, digest in FILES.items():
        path = RAW / name
        if not path.exists():
            print(f"downloading {name}")
            urllib.request.urlretrieve(BASE + name, path)
        if sha256(path) != digest:
            sys.exit(f"{name}: checksum mismatch, delete it and run again")
    print(f"{len(FILES)} files OK in {RAW}")


if __name__ == "__main__":
    main()
