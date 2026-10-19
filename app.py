from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Lagos Food Price Tracker", layout="wide")

DATA_FILE = Path(__file__).with_name("public_prices.csv")


@st.cache_data(ttl=60)
def load_prices():
    return pd.read_csv(DATA_FILE)


st.title("Lagos Food Price Tracker")
st.write("Browse recorded food prices by market, seller type, item, and quantity.")

if not DATA_FILE.exists():
    st.error("public_prices.csv was not found. Run export_public_data.py first.")
    st.stop()

prices = load_prices()

if prices.empty:
    st.info("There are no price observations to show yet.")
    st.stop()

prices["observed_on"] = pd.to_datetime(prices["observed_on"], errors="coerce")
collection_dates = prices["observed_on"].dropna()
if not collection_dates.empty:
    first_date = collection_dates.min().strftime("%d %b %Y")
    last_date = collection_dates.max().strftime("%d %b %Y")
    st.caption(f"Collection dates covered: {first_date} to {last_date}.")

market_options = ["All markets"] + sorted(prices["market"].dropna().unique())
seller_type_options = ["All seller types"] + sorted(
    prices["seller_type"].dropna().unique()
)
item_options = ["All items"] + sorted(prices["item"].dropna().unique())
quantity_options = [
    "All reported quantities"
] + sorted(prices["quantity_reported"].dropna().unique())

selected_market = st.selectbox("Market", market_options)
selected_seller_type = st.selectbox("Seller type", seller_type_options)
selected_item = st.selectbox("Food item", item_options)
selected_quantity = st.selectbox("Reported quantity", quantity_options)

filtered = prices.copy()

if selected_market != "All markets":
    filtered = filtered[filtered["market"] == selected_market]

if selected_seller_type != "All seller types":
    filtered = filtered[filtered["seller_type"] == selected_seller_type]

if selected_item != "All items":
    filtered = filtered[filtered["item"] == selected_item]

if selected_quantity != "All reported quantities":
    filtered = filtered[
        filtered["quantity_reported"] == selected_quantity
    ]

filtered = filtered.sort_values("observed_on", ascending=False)

st.metric("Observations shown", len(filtered))
st.caption(
    "These are collected observations, not official market-wide prices. "
    "Retail and wholesale prices can differ. Quantities are shown as recorded, "
    "so prices for different quantities may not be directly comparable."
)

display = filtered.rename(columns={
    "observed_on": "Collection date",
    "market": "Market",
    "seller_type": "Seller type",
    "item": "Food item",
    "quantity_reported": "Reported quantity",
    "price_ngn": "Price (₦)",
})

st.dataframe(display, hide_index=True, use_container_width=True)
