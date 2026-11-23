"""1. adım: OpenF1'den tur ve lastik stint verisini çek, ham CSV olarak kaydet.

Kullanım:
    python src/fetch_data.py
    python src/fetch_data.py --year 2024 --country Bahrain
"""
import argparse
import sys
import time

import pandas as pd
import requests

from common import RAW, add_race_args, tag

BASE = "https://api.openf1.org/v1"


def get(endpoint, retries=3, **params):
    """OpenF1'e istek at; hız sınırına (429) takılırsa bekleyip tekrar dene."""
    for attempt in range(retries):
        r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=30)
        if r.status_code == 429:
            time.sleep(2 * (attempt + 1))
            continue
        r.raise_for_status()
        return pd.DataFrame(r.json())
    raise RuntimeError(f"{endpoint}: istek sınırına takıldı, biraz sonra tekrar dene.")


def main():
    parser = add_race_args(argparse.ArgumentParser(description=__doc__.splitlines()[0]))
    parser.add_argument("--session-key", type=int, help="Bilinen session_key varsa doğrudan kullan")
    args = parser.parse_args()

    if args.session_key:
        session_key = args.session_key
    else:
        sessions = get("sessions", year=args.year, country_name=args.country, session_name="Race")
        if sessions.empty:
            sys.exit(f"{args.country} {args.year} için yarış oturumu bulunamadı.")
        print(sessions[["session_key", "session_name", "country_name", "date_start"]])
        if len(sessions) > 1:
            print("Birden fazla yarış bulundu, ilki kullanılıyor (başkası için --session-key ver).")
        session_key = int(sessions.loc[0, "session_key"])

    laps = get("laps", session_key=session_key)
    stints = get("stints", session_key=session_key)
    print("Tur sayısı:", len(laps), "| Stint sayısı:", len(stints))

    df = laps.merge(stints, on="driver_number", suffixes=("", "_stint"))
    df = df[(df.lap_number >= df.lap_start) & (df.lap_number <= df.lap_end)].copy()
    df["tyre_life"] = df.tyre_age_at_start + (df.lap_number - df.lap_start)

    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / f"{tag(args.year, args.country)}_race.csv"
    df.to_csv(path, index=False)
    print("Kaydedildi:", path)


if __name__ == "__main__":
    main()
