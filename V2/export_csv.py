"""CSV + JSON export helpers."""

import json
from io import BytesIO, StringIO
import pandas as pd


def build_csv(df):
    """Return a BytesIO of the DataFrame as UTF-8 CSV."""
    out = StringIO()
    export_df = df.copy()
    for col in ["complaint_categories", "keywords"]:
        if col in export_df.columns:
            if col == "keywords":
                export_df[col] = export_df[col].apply(
                    lambda kws: ", ".join(
                        kw.get("keyword", "") if isinstance(kw, dict) else str(kw)
                        for kw in kws
                    )
                )
            else:
                export_df[col] = export_df[col].apply(
                    lambda cats: ", ".join(str(c) for c in cats)
                )
    export_df.to_csv(out, index=False)
    return BytesIO(out.getvalue().encode("utf-8"))


def build_json(kpis, executive_report, records):
    """Return a BytesIO of the full analysis as JSON."""
    payload = {
        "kpis": kpis,
        "executive_report": executive_report,
        "records": records,
    }
    return BytesIO(json.dumps(payload, indent=2, default=str).encode("utf-8"))