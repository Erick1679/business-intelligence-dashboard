"""Interactive business intelligence dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).parent / "data/customer_transactions.csv"

st.set_page_config(
    page_title="Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_data():
    """Load cleaned customer transaction data."""
    data = pd.read_csv(DATA_PATH)

    data["transaction_date"] = pd.to_datetime(
        data["transaction_date"],
        errors="coerce",
    )

    data["amount"] = pd.to_numeric(
        data["amount"],
        errors="coerce",
    )

    return data


data = load_data()

required = {
    "transaction_id",
    "customer_id",
    "transaction_date",
    "amount",
    "channel",
    "country",
    "data_quality_status",
}

if not required.issubset(data.columns):
    st.error("The customer dataset is missing required columns.")
    st.stop()

valid = data.loc[
    data["data_quality_status"] == "Valid"
].dropna(
    subset=["transaction_date", "amount", "customer_id"]
).copy()

if valid.empty:
    st.error("No valid customer transactions are available.")
    st.stop()


st.title("📊 Business Intelligence Dashboard")
st.caption("Customer revenue, purchasing behavior, and segmentation")

# Sidebar filters

st.sidebar.header("Dashboard Filters")

countries = sorted(valid["country"].dropna().unique().tolist())
channels = sorted(valid["channel"].dropna().unique().tolist())

selected_countries = st.sidebar.multiselect(
    "Country",
    options=countries,
    default=countries,
)

selected_channels = st.sidebar.multiselect(
    "Sales Channel",
    options=channels,
    default=channels,
)

minimum_date = valid["transaction_date"].min().date()
maximum_date = valid["transaction_date"].max().date()

date_range = st.sidebar.date_input(
    "Transaction Date Range",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date,
)

if len(date_range) != 2:
    st.info("Select both a start date and an end date.")
    st.stop()

start_date, end_date = date_range

filtered = valid.loc[
    valid["country"].isin(selected_countries)
    & valid["channel"].isin(selected_channels)
    & valid["transaction_date"].dt.date.between(
        start_date, end_date
    )
].copy()

if filtered.empty:
    st.warning("No transactions match your selected filters.")
    st.stop()


# Business KPIs

revenue = float(filtered["amount"].sum())
transactions = len(filtered)
customers = filtered["customer_id"].nunique()
average_order = revenue / transactions

customer_frequency = filtered.groupby(
    "customer_id"
).size()

repeat_rate = (
    (customer_frequency > 1).mean() * 100
)

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"{revenue:,.2f}")
col2.metric("Transactions", f"{transactions:,}")
col3.metric("Customers", f"{customers:,}")
col4.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")

st.metric("Average Order Value", f"{average_order:,.2f}")


# Monthly revenue

monthly = filtered.copy()

monthly["month"] = (
    monthly["transaction_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_revenue = (
    monthly.groupby("month", as_index=False)
    .agg(
        revenue=("amount", "sum"),
        transactions=("transaction_id", "count"),
    )
    .sort_values("month")
)

revenue_chart = px.bar(
    monthly_revenue,
    x="month",
    y="revenue",
    title="Monthly Revenue Performance",
    labels={
        "month": "Month",
        "revenue": "Revenue",
    },
)

st.plotly_chart(revenue_chart, width="stretch")


# Revenue by country and channel

left, right = st.columns(2)

with left:
    country_revenue = (
        filtered.groupby("country", as_index=False)
        .agg(revenue=("amount", "sum"))
    )

    country_chart = px.bar(
        country_revenue,
        x="country",
        y="revenue",
        title="Revenue by Country",
    )

    st.plotly_chart(country_chart, width="stretch")

with right:
    channel_revenue = (
        filtered.groupby("channel", as_index=False)
        .agg(revenue=("amount", "sum"))
    )

    channel_chart = px.pie(
        channel_revenue,
        names="channel",
        values="revenue",
        title="Revenue by Sales Channel",
    )

    st.plotly_chart(channel_chart, width="stretch")


# RFM customer segmentation

st.subheader("Customer Segmentation")

reference_date = pd.Timestamp(end_date) + pd.Timedelta(days=1)

rfm = (
    filtered.groupby("customer_id")
    .agg(
        last_purchase=("transaction_date", "max"),
        frequency=("transaction_id", "count"),
        monetary=("amount", "sum"),
    )
    .reset_index()
)

rfm["recency_days"] = (
    reference_date - rfm["last_purchase"].dt.normalize()
).dt.days

rfm["segment"] = "Needs Attention"

loyal = (
    (rfm["frequency"] >= 3)
    & (rfm["recency_days"] <= 30)
)

recent = (
    (rfm["recency_days"] <= 30)
    & ~loyal
)

at_risk = (
    (rfm["recency_days"] > 30)
    & (rfm["frequency"] >= 3)
)

rfm.loc[loyal, "segment"] = "Loyal"
rfm.loc[recent, "segment"] = "Recent"
rfm.loc[at_risk, "segment"] = "At Risk"

segment_counts = (
    rfm.groupby("segment", as_index=False)
    .agg(customers=("customer_id", "count"))
)

segment_chart = px.pie(
    segment_counts,
    names="segment",
    values="customers",
    title="Customer Segments",
)

st.plotly_chart(segment_chart, width="stretch")

st.dataframe(
    rfm[
        [
            "customer_id",
            "recency_days",
            "frequency",
            "monetary",
            "segment",
        ]
    ],
    width="stretch",
    hide_index=True,
)


# Transaction details and export

st.subheader("Filtered Transactions")

st.dataframe(
    filtered,
    width="stretch",
    hide_index=True,
)

st.download_button(
    label="Download Filtered Transactions",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_transactions.csv",
    mime="text/csv",
)

st.caption(
    "Synthetic portfolio dataset. "
    "All KPIs and visualizations use valid transactions only."
)
