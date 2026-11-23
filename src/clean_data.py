"""2. adım: ham veriyi temizle, işlenmiş CSV olarak kaydet.

Kullanım:
    python src/clean_data.py
"""
import argparse
import sys

import pandas as pd

from common import PROCESSED, RAW, add_race_args, tag


def main():
    args = add_race_args(argparse.ArgumentParser(description=__doc__.splitlines()[0])).parse_args()
    t = tag(args.year, args.country)

    raw_path = RAW / f"{t}_race.csv"
    if not raw_path.exists():
        sys.exit(f"{raw_path} yok. Önce şunu çalıştır: python src/fetch_data.py")

    df = pd.read_csv(raw_path)
    clean = df.copy()
    print("Çift satır kontrolü:", clean.duplicated(["driver_number", "lap_number"]).sum())

    # Her pilotun son turu
    last_lap = clean.groupby("driver_number")["lap_number"].transform("max")
    clean["is_pit_in_lap"] = (clean.lap_number == clean.lap_end) & (clean.lap_end < last_lap)

    clean = clean[
        (clean.lap_number > 1)
        & (~clean.is_pit_out_lap)
        & (~clean.is_pit_in_lap)
        & (clean.lap_duration.notna())
    ]

    # Çok yavaş turları ele (medyanın %107'sinden yavaşlar)
    med = clean.lap_duration.median()
    clean = clean[clean.lap_duration <= 1.07 * med]

    print("Önce:", len(df), "| Sonra:", len(clean))
    print(clean.compound.value_counts().to_string())

    PROCESSED.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED / f"{t}_clean.csv"
    clean.to_csv(out_path, index=False)
    print("Kaydedildi:", out_path)


if __name__ == "__main__":
    main()
