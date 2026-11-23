"""Ortak yollar ve komut satırı argümanları."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"


def tag(year: int, country: str) -> str:
    """Dosya adı öneki, örn. bahrain_2024."""
    return f"{country.lower().replace(' ', '_')}_{year}"


def add_race_args(parser):
    parser.add_argument("--year", type=int, default=2024, help="Sezon (varsayılan: 2024)")
    parser.add_argument("--country", default="Bahrain", help="Ülke adı, OpenF1'deki yazımıyla (varsayılan: Bahrain)")
    return parser
