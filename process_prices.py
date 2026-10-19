from pathlib import Path
import re 
import sys

import pandas as pd

DEFAULT_FILE_NAME = "Lagos Food Price Tracker (Responses) - Form Responses 1.csv"
def load_responses(csv_path: Path) -> pd.DataFrame:
    """Read th Google Forms CSV export without changing the source file."""
    if not csv_path.exists():
       raise FileNotFoundError(f"File not found: {csv_path}")

    raw = pd.read_csv(csv_path)

    #Trim accidental spaces in headings, e.g 'market_name '.
    raw.columns = [str(column).strip() for column in raw.columns]

    #Give key columns stable names for the rest of the pipeline.
    raw = raw.rename(columns={
        "Timestamp": "submitted_at",
        "date_of_collection": "observed_on",
        "market_name": "market",
        "vendor_type": "seller_type",
        "food_category": "category",
        "item_name": "item",
        "quantity": "quantity_reported",
        "price(#)": "price_reported",
        "quality": "quality_reported"
    })
    return raw

def prepare_prices(raw: pd.DataFrame) -> pd.DataFrame:
    """Make an analysis copy; keep reported quantities as written by collectors."""
    data = raw.copy()

    #Collector names are not needed for price comparisons.
    data = data.drop(columns=["Name"], errors="ignore")

    #Remove leading/trailing spaces and normalize text labels for grouping.
    for column in data.columns:
        if data[column].dtype == object:
            data[column] = data[column].astype("string").str.strip()

    for column in ["market", "seller_type", "category", "item"]:
        if column in data.columns:
            data[column] = data[column].str.lower()

    #Parse the collection date. Invalid values become missing and are flagged below.
    if "observed_on" in data.columns:
        data["observed_on"] = pd.to_datetime(
            data["observed_on"], format="mixed", errors="coerce"
        ).dt.date 

    #Convert prices such as '#50,000' or '#50,000' to numeric naira values.
    if "price_reported" in data.columns:
        price_text = data["price_reported"].astype("string")
        price_text = price_text.str.replace(r"[^0-9.\-]", "", regex=True)
        data["price_ngn"] = pd.to_numeric(price_text, errors="coerce")

    #Keep quantity exactly as reported, do not guess weights for local measures.
    if "quantity_reported" in data.columns:
        data["quantity_reported"] = (
            data["quantity_reported"].astype("string").str.strip()
        )

    if "quality_reported" in data.columns:
        data["quality_reported"] = pd.to_numeric(
            data["quality_reported"], errors="coerce"
        )

    return data

def main() -> None:
    csv_path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path.home() / "Downloads" / DEFAULT_FILE_NAME
    )

    raw = load_responses(csv_path)
    prices = prepare_prices(raw)

    required = ["observed_on", "market", "item", "quantity_reported", "price_ngn"]
    missing_columns = [column for column in required if column not in prices.columns]
    if missing_columns:
        raise ValueError(f"The form export is missing expected columns: {missing_columns}")

    incomplete = prices[required].isna().any(axis=1)
    invalid_price = prices["price_ngn"].isna() | (prices["price_ngn"] <= 0)

    print(f"Response rows read: {len(prices)}")
    print(f"Rows missing required fields: {int(incomplete.sum())}")
    print(f"ROws with a missing or non-positive price: {int(invalid_price.sum())}")
    print("\nRows by market and item (with quantity as reported):")
    summary = (
        prices.groupby(["market", "item", "quantity_reported"], dropna=False)
        .size()
        .rename("observations")
        .reset_index()
        .sort_values(["market", "item", "quantity_reported"])
    )
    print(summary.to_string(index=False))
    print("\nNo cleaned file was reported, the source data remains unchanged.")

if __name__ == "__main__":
    main()


