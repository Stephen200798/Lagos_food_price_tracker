# Lagos Food Price Tracker

A small Streamlit dashboard for browsing food-price observations collected in Lagos markets.

## What the app shows

The dashboard reads `public_prices.csv` and lets visitors filter observations by market, seller type, food item, and the quantity reported by the collector. Each row shows the collection date, seller type, reported quantity, and price in naira.

## Data notes

- Prices are observations collected from sellers, not an official market-wide price list.
- Seller type is included as recorded (retail, wholesale, or supermarket) so visitors can filter these observations separately.
- Quantities are kept as reported. A price for a basket, derica, kilogram, or other measure may not be directly comparable with a different quantity.
- The published dataset contains no collector names or raw Google Form responses.
- Refresh `public_prices.csv` after loading new approved observations into SQL Server by running `export_public_data.py`.

## Publish the dashboard

For deployment, include `app.py`, `public_prices.csv`, `requirements.txt`, and this README in the GitHub repository. In Streamlit Community Cloud, select `app.py` as the app's main file. The deployed dashboard reads the CSV snapshot; it does not connect to the local SQL Server.

Before uploading, check that the repository does not contain the original Google Form response export, collector names, database backups, or credentials. `.gitignore` excludes CSV files except for the public-safe `public_prices.csv` snapshot.

When new observations are ready, review them, load them into SQL Server, export an updated `public_prices.csv`, then upload that reviewed snapshot to GitHub to update the online dashboard.

## Run the dashboard locally

The app uses only `app.py`, `public_prices.csv`, `requirements.txt`, and this README when it is deployed. The local SQL Server connection is used by the separate data-preparation scripts.
