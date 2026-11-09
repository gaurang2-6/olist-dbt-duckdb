"""A small Streamlit dashboard over the dbt marts.

    streamlit run dashboard/app.py      (after `dbt build`)
"""
from pathlib import Path

import altair as alt
import duckdb
import streamlit as st

DB = Path(__file__).resolve().parents[1] / "olist.duckdb"
BLUE, ORANGE, GREY = "#2a78d6", "#eb6834", "#a3a29e"

st.set_page_config(page_title="Olist marts", layout="wide")


@st.cache_data
def q(sql: str):
    with duckdb.connect(str(DB), read_only=True) as con:
        return con.sql(sql).df()


if not DB.exists():
    st.error("olist.duckdb not found. Run `dbt build` first (see the README).")
    st.stop()

st.title("Olist marketplace: delivery and reviews")
st.caption("Built from the dbt marts in olist.duckdb. Sep 2016 and Sep-Oct 2018 are partial months and are left out.")

monthly = q("""select * from marts.mart_monthly_kpis
               where month between date '2017-01-01' and date '2018-08-01' order by month""")
first, last = monthly.month.min().date(), monthly.month.max().date()
start, end = st.slider("Months", min_value=first, max_value=last, value=(first, last), format="MMM YYYY")
m = monthly[(monthly.month.dt.date >= start) & (monthly.month.dt.date <= end)]

orders = q(f"""select * from marts.fct_orders
               where status = 'delivered' and purchase_month between date '{start}' and date '{end}'""")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Delivered orders", f"{len(orders):,}")
c2.metric("Revenue (BRL)", f"{orders.order_value.sum() / 1e6:.2f}M")
c3.metric("Delivered late", f"{orders.is_late.mean():.1%}")
c4.metric("Average review", f"{orders.review_score.mean():.2f}")

left, right = st.columns(2)
with left:
    st.subheader("Late deliveries by month")
    st.altair_chart(alt.Chart(m).mark_line(point=True, color=ORANGE).encode(
        x=alt.X("month:T", title=None), y=alt.Y("late_share:Q", title="Delivered late", axis=alt.Axis(format="%")),
        tooltip=[alt.Tooltip("month:T", format="%b %Y"), alt.Tooltip("late_share:Q", format=".1%"), "orders:Q"],
    ), width="stretch")
with right:
    st.subheader("Average review score by month")
    st.altair_chart(alt.Chart(m).mark_line(point=True, color=BLUE).encode(
        x=alt.X("month:T", title=None), y=alt.Y("avg_review_score:Q", title="Average review", scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("month:T", format="%b %Y"), alt.Tooltip("avg_review_score:Q", format=".2f")],
    ), width="stretch")

st.subheader("Share of 1-2 star reviews, by delivery timing")
buckets = q("select * from marts.mart_delivery_reviews order by delivery_bucket")
buckets["timing"] = buckets.delivery_bucket.str.split(". ", n=1).str[1]
buckets["late"] = buckets.delivery_bucket.str.contains("late")
st.altair_chart(alt.Chart(buckets).mark_bar().encode(
    x=alt.X("timing:N", sort=None, title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y("share_1_2_stars:Q", title="1-2 star reviews", axis=alt.Axis(format="%")),
    color=alt.condition("datum.late", alt.value(ORANGE), alt.value(BLUE)),
    tooltip=["timing", alt.Tooltip("share_1_2_stars:Q", format=".1%"), "orders:Q"],
), width="stretch")

left, right = st.columns(2)
with left:
    st.subheader("Days to deliver, by state")
    states = (orders.groupby("customer_state")
              .agg(orders=("order_id", "size"), days=("delivery_days", "mean")).reset_index()
              .query("orders >= 100"))
    st.altair_chart(alt.Chart(states).mark_bar(color=GREY).encode(
        x=alt.X("customer_state:N", sort="y", title=None), y=alt.Y("days:Q", title="Average days"),
        tooltip=["customer_state", alt.Tooltip("days:Q", format=".1f"), "orders:Q"],
    ), width="stretch")
with right:
    st.subheader("Top categories by revenue")
    cats = q("select * from marts.mart_category_performance order by revenue desc limit 15")
    st.dataframe(cats.style.format({"revenue": "{:,.0f}", "freight_to_price": "{:.1%}", "late_share": "{:.1%}",
                                    "avg_review_score": "{:.2f}"}), hide_index=True, width="stretch")
