from decimal import Decimal
from pathlib import Path

import mssql_python
import pandas as pd

from process_prices import load_responses, prepare_prices


csv_path = (
    Path.home()
    / "Downloads"
    / "Lagos Food Price Tracker (Responses) - Form Responses 1.csv"
)

raw = load_responses(csv_path)
prices = prepare_prices(raw)

connection_string = (
    "Server=localhost\\SQLEXPRESS;"
    "Database=LagosFoodPriceTracker;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

insert_sql = """
INSERT INTO dbo.PriceObservations (
    submitted_at,
    observed_on,
    market,
    seller_type,
    category,
    item,
    quantity_reported,
    price_ngn,
    quality_rating
)
VALUES (
    %(submitted_at)s,
    %(observed_on)s,
    %(market)s,
    %(seller_type)s,
    %(category)s,
    %(item)s,
    %(quantity_reported)s,
    %(price_ngn)s,
    %(quality_rating)s
)
"""


def optional_text(value):
    if pd.isna(value):
        return None
    return str(value)


connection = mssql_python.connect(connection_string)
cursor = connection.cursor()

try:
    cursor.execute(
        "SELECT submitted_at FROM dbo.PriceObservations "
        "WHERE submitted_at IS NOT NULL"
    )
    already_loaded = {row[0] for row in cursor.fetchall()}

    inserted = 0
    skipped = 0

    for _, row in prices.iterrows():
        submitted_at = pd.to_datetime(
            row["submitted_at"], format="mixed", errors="coerce"
        )

        if pd.isna(submitted_at):
            skipped += 1
            continue

        submitted_at = submitted_at.to_pydatetime().replace(microsecond=0)

        if submitted_at in already_loaded:
            skipped += 1
            continue

        observed_on = row["observed_on"]
        if isinstance(observed_on, pd.Timestamp):
            observed_on = observed_on.date()

        quality = row["quality_reported"]
        if pd.isna(quality):
            quality = None
        else:
            quality = int(quality)

        values = {
            "submitted_at": submitted_at,
            "observed_on": observed_on,
            "market": str(row["market"]),
            "seller_type": optional_text(row["seller_type"]),
            "category": optional_text(row["category"]),
            "item": str(row["item"]),
            "quantity_reported": str(row["quantity_reported"]),
            "price_ngn": Decimal(str(row["price_ngn"])),
            "quality_rating": quality,
        }

        cursor.execute(insert_sql, values)
        already_loaded.add(submitted_at)
        inserted += 1

    connection.commit()
    print(f"Inserted {inserted} new records; skipped {skipped} records.")

except Exception:
    connection.rollback()
    raise

finally:
    cursor.close()
    connection.close()
