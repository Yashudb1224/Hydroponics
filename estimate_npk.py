# estimate_npk.py
import pandas as pd
import os

BASE = os.path.dirname(os.path.abspath(__file__))
RATIOS_PATH = os.path.join(BASE, "models", "npk_ratios.csv")

if os.path.exists(RATIOS_PATH):
    ratios = pd.read_csv(RATIOS_PATH)
else:
    # fallback empty df
    ratios = pd.DataFrame(columns=["plant","stage","rN","rP","rK"])

def estimate_npk_from_tds(tds_ppm, plant, stage, scale=1.0):
    """
    Convert tds_ppm (ppm) into estimated N,P,K (mg/L) using ratios.
    scale: calibration factor to match lab mg/L (adjust after lab test).
    """
    # handle missing/zero tds
    if tds_ppm is None:
        return 0.0, 0.0, 0.0
    # find ratio row
    row = ratios[(ratios["plant"] == plant) & (ratios["stage"] == stage)]
    if not row.empty:
        rN = float(row.iloc[0]["rN"])
        rP = float(row.iloc[0]["rP"])
        rK = float(row.iloc[0]["rK"])
    else:
        # fallback to global mean ratios
        if not ratios.empty:
            rN = ratios["rN"].mean()
            rP = ratios["rP"].mean()
            rK = ratios["rK"].mean()
        else:
            # uniform split if nothing else
            rN, rP, rK = 0.5, 0.25, 0.25

    total_est = tds_ppm * scale
    return round(total_est * rN, 2), round(total_est * rP, 2), round(total_est * rK, 2)
