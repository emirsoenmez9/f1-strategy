"""3. adım: lastik aşınma regresyonunu kur, parametreleri ve grafiği kaydet.

tur_süresi = sürücü_etkisi + bileşik_etkisi
           + (bileşiğe özel aşınma eğimi × lastik_yaşı) + (yakıt_etkisi × tur_no) + hata

Kullanım:
    python src/fit_model.py
"""
import argparse
import json
import sys

import matplotlib

matplotlib.use("Agg")  # ekransız ortamda da grafik kaydedebilmek için
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf

from common import PROCESSED, RESULTS, add_race_args, tag


def main():
    args = add_race_args(argparse.ArgumentParser(description=__doc__.splitlines()[0])).parse_args()
    t = tag(args.year, args.country)

    clean_path = PROCESSED / f"{t}_clean.csv"
    if not clean_path.exists():
        sys.exit(f"{clean_path} yok. Önce şunu çalıştır: python src/clean_data.py")
    clean = pd.read_csv(clean_path)

    formula = "lap_duration ~ C(driver_number) + C(compound) + tyre_life:C(compound) + lap_number"
    ols = smf.ols(formula, data=clean)

    # Klasik SE: turların birbirinden bağımsız olduğunu varsayar
    model_ols = ols.fit()
    if int(model_ols.nobs) != len(clean):
        sys.exit("Eksik değer nedeniyle satır düştü; kümeler hizalanamaz.")

    # Kümelenmiş SE: aynı sürücünün turları birbirine bağımlı sayılır.
    # Küme sayısı az (~20) olduğu için t dağılımı kullanılır.
    model = ols.fit(
        cov_type="cluster",
        cov_kwds={"groups": pd.factorize(clean["driver_number"])[0]},
        use_t=True,
    )

    ilgili = [p for p in model.params.index if "tyre_life" in p or p == "lap_number"]
    tablo = pd.DataFrame({
        "tahmin": model.params[ilgili],
        "SE_klasik": model_ols.bse[ilgili],
        "SE_kumelenmis": model.bse[ilgili],
    })
    tablo["SE_orani"] = tablo["SE_kumelenmis"] / tablo["SE_klasik"]
    ci = model.conf_int().loc[ilgili]
    tablo["GA95_alt"], tablo["GA95_ust"] = ci[0], ci[1]

    print(tablo.round(4).to_string())
    print("\nR-kare:", round(model.rsquared, 3),
          "| Gözlem:", int(model.nobs),
          "| Sürücü (küme):", clean.driver_number.nunique())
    print("Tur başına artık std (sn):", round(model.scale ** 0.5, 3))

    # Çıktılar
    RESULTS.mkdir(exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tablo.round(5).to_csv(RESULTS / f"{t}_deg_table.csv")

    compounds = sorted(clean.compound.unique())
    key = lambda c: f"tyre_life:C(compound)[{c}]"
    out = {
        "deg_per_lap": {c: float(model.params[key(c)]) for c in compounds},
        "deg_se": {c: float(model.bse[key(c)]) for c in compounds},  # sürücüye göre kümelenmiş
        "deg_se_klasik": {c: float(model_ols.bse[key(c)]) for c in compounds},
        "fuel_per_lap": float(model.params["lap_number"]),
        "lap_sigma": float(model.scale ** 0.5),
    }
    params_path = PROCESSED / f"{t}_params.json"
    with open(params_path, "w") as f:
        json.dump(out, f, indent=2)

    clean = clean.assign(resid=model.resid)
    fig, ax = plt.subplots(figsize=(9, 4))
    for comp, g in clean.groupby("compound"):
        ax.scatter(g.tyre_life, g.resid, s=8, alpha=0.5, label=comp)
    ax.axhline(0, color="black", lw=1)
    ax.set_xlabel("Lastik yaşı (tur)")
    ax.set_ylabel("Artık (sn)")
    ax.legend()
    fig_path = RESULTS / f"{t}_residuals.png"
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")

    print("\nKaydedildi:", params_path, "|", fig_path, "|", RESULTS / f"{t}_deg_table.csv")


if __name__ == "__main__":
    main()
