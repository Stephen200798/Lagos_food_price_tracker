from pathlib import Path

import mssql_python
import pandas as pd

connection_string = (
    "Server=localhost\\SQLEXPRESS;"
    "Database=LagosFoodPriceTracker;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

query = """
SELECT observed_on, market, seller_type, item, quantity_reported, price_ngn
FROM dbo.PriceObservations
ORDER BY observed_on DESC, market, item;
"""

connection = mssql_python.connect(connection_string)
cursor = connection.cursor()

try:
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
finally:
    cursor.close()
    connection.close()

public_data = pd.DataFrame.from_records(rows, columns=columns)
output_file = Path(__file__).with_name("public_prices.csv")
public_data.to_csv(output_file, index=False)

print(f"Exported {len(public_data)} price observations.")
print(f"Saved to: {output_file}")
print("Included fields: date, market, seller type, item, reported quantity, and price.")
