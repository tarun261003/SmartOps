# smartops_agent/analytics_tools.py
from pathlib import Path
from typing import Dict, Any

import pandas as pd


def analyze_sales_csv(file_path: str) -> Dict[str, Any]:
    """
    Basic sales analysis: totals, by-month, by-region.

    CSV expected columns (you can adjust):
      - date
      - month
      - region
      - revenue
      - units

    Output is numeric/structured so the LLM can narrate it.
    """
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    df = pd.read_csv(path)

    report: Dict[str, Any] = {}

    if "revenue" in df.columns:
        report["total_revenue"] = float(df["revenue"].sum())
        report["avg_revenue"] = float(df["revenue"].mean())

    if "units" in df.columns:
        report["total_units"] = int(df["units"].sum())
        report["avg_units"] = float(df["units"].mean())

    if "month" in df.columns and "revenue" in df.columns:
        report["revenue_by_month"] = {
            str(k): float(v) for k, v in df.groupby("month")["revenue"].sum().items()
        }

    if "region" in df.columns and "revenue" in df.columns:
        report["revenue_by_region"] = {
            str(k): float(v) for k, v in df.groupby("region")["revenue"].sum().items()
        }

    report["row_count"] = int(len(df))

    return report