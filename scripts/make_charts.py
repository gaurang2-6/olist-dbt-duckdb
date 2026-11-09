"""Read the dbt marts and write the README charts to reports/figures/.

    python scripts/make_charts.py      (after `dbt build`)
"""
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "figures"
BLUE, ORANGE, INK, INK2, GRID, SURFACE, GREY = ("#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df",
                                                "#fcfcfb", "#a3a29e")
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK, "axes.titlesize": 13,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "xtick.color": INK2, "ytick.color": INK2, "font.size": 10,
    "legend.frameon": False, "lines.linewidth": 2,
})
# Months with a full set of orders (Olist's data starts thin in late 2016 and stops mid-Sep 2018).
FULL_MONTHS = "month between date '2017-01-01' and date '2018-08-01'"


def delivery_reviews(con):
    d = con.sql("select * from marts.mart_delivery_reviews order by delivery_bucket").df()
    labels = [b.split(". ", 1)[1].replace("on the promised day", "on the day") for b in d.delivery_bucket]
    late = d.delivery_bucket.str.contains("late")
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    ax.bar(labels, d.share_1_2_stars * 100, color=[ORANGE if x else BLUE for x in late], width=0.62)
    for i, (v, n) in enumerate(zip(d.share_1_2_stars, d.orders)):
        ax.annotate(f"{v:.0%}", (i, v * 100), xytext=(0, 4), textcoords="offset points", ha="center",
                    color=INK, fontsize=10, fontweight="bold")
        ax.annotate(f"{n:,} orders", (i, 0), xytext=(0, 5), textcoords="offset points", ha="center",
                    color=SURFACE, fontsize=8)
    ax.grid(axis="x", visible=False)
    ax.set(ylabel="Reviews with 1 or 2 stars (%)", ylim=(0, 90), xlabel="Delivered vs. the date promised at checkout")
    ax.set_title("1-2 star reviews jump from 9% to 79% once delivery slips past the promise", pad=12)
    fig.tight_layout()
    fig.savefig(OUT / "delivery_reviews.png", dpi=150)
    plt.close(fig)


def monthly(con):
    m = con.sql(f"select * from marts.mart_monthly_kpis where {FULL_MONTHS} order by month").df()
    fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    panels = [(m.orders / 1000, "Orders (thousands)", BLUE),
              (m.late_share * 100, "Delivered late (%)", ORANGE),
              (m.avg_review_score, "Average review score", INK2)]
    for ax, (y, label, color) in zip(axes, panels):
        ax.plot(m.month, y, color=color, marker="o", ms=4)
        ax.set_ylabel(label)
        ax.grid(axis="x", visible=False)
    for month in ["2017-11-01", "2018-03-01"]:
        for ax in axes:
            ax.axvline(matplotlib.dates.datestr2num(month), color=GRID, lw=6, zorder=0)
    axes[1].annotate("Black Friday\nNov 2017", (matplotlib.dates.datestr2num("2017-11-01"), 12.4),
                     xytext=(-12, 0), textcoords="offset points", ha="right", va="center", color=INK, fontsize=9)
    axes[1].annotate("Feb–Mar 2018", (matplotlib.dates.datestr2num("2018-03-01"), 19.0),
                     xytext=(-12, 0), textcoords="offset points", ha="right", va="center", color=INK, fontsize=9)
    axes[0].set_title("Each spike in late deliveries is matched by a dip in review scores", pad=12)
    fig.tight_layout()
    fig.savefig(OUT / "monthly_kpis.png", dpi=150)
    plt.close(fig)


def states(con):
    s = con.sql("""
        select customer_state as state, count(*) as orders, avg(delivery_days) as days,
               avg(review_score) as score
        from marts.fct_orders where status = 'delivered'
        group by 1 having count(*) >= 300 order by days
    """).df()
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    colors = [BLUE if st == "SP" else GREY for st in s.state]
    ax.bar(s.state, s.days, color=colors, width=0.65)
    ax.grid(axis="x", visible=False)
    ax.set(ylabel="Average days from purchase to delivery")
    ax.annotate(f"São Paulo: {s.days.iloc[0]:.1f} days,\n{s.orders.iloc[0] / s.orders.sum():.0%} of orders",
                (0, s.days.iloc[0]), xytext=(6, 48), textcoords="offset points", color=INK, fontsize=9,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.set_title("Outside São Paulo, parcels take nearly 3x as long to arrive", pad=12)
    fig.tight_layout()
    fig.savefig(OUT / "delivery_by_state.png", dpi=150)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(ROOT / "olist.duckdb"), read_only=True) as con:
        delivery_reviews(con)
        monthly(con)
        states(con)
    print(f"Wrote charts to {OUT}")


if __name__ == "__main__":
    main()
