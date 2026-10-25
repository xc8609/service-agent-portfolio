"""Render the three portable review pages from reconciled SQL results.

These are GitHub/browser previews. Native analytical filters live in the Tableau
workbook; the previews never imply that tab navigation recalculates measures.
"""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUTPUT = ROOT / "dashboard"
INK = "#292B29"
TEAL = "#285F57"
BRONZE = "#876B45"
MUTED = "#66665E"
GRID = "#DEDCD3"
PAPER = "#F7F5EF"
NEGATIVE = "#965448"


def read_csv(name):
    with (RESULTS / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def money(value):
    return f"£{value / 1_000_000:.2f}m"


def page(number, title, subtitle):
    fig = plt.figure(figsize=(16, 10), facecolor=PAPER)
    fig.text(
        0.045,
        0.958,
        f"CLIENT DEVELOPMENT  /  RETAIL INTELLIGENCE                                      {number} / 03",
        size=10,
        color=BRONZE,
        weight="bold",
    )
    fig.text(0.045, 0.902, title, size=25, color=INK, fontfamily="serif")
    fig.text(0.045, 0.866, subtitle, size=11, color=MUTED)
    return fig


def card(fig, x, label, value, detail):
    fig.text(x, 0.805, label.upper(), size=10, color=MUTED)
    fig.text(x, 0.755, value, size=29, color=INK)
    fig.text(x, 0.725, detail, size=10, color=MUTED)


def axes(fig, rect, title):
    ax = fig.add_axes(rect, facecolor=PAPER)
    ax.set_title(title, loc="left", pad=17, size=13, weight="bold", color=INK)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0, pad=6)
    ax.set_axisbelow(True)
    return ax


def footer(fig, text):
    fig.text(0.045, 0.062, text, size=10, color=INK)
    fig.text(
        0.045,
        0.029,
        "Source: Chen (2012), UCI Online Retail II · CC BY 4.0 · UK online gift retail · GBP. Native filters: Tableau workbook.",
        size=9,
        color=MUTED,
    )


def save(fig, name):
    target = OUTPUT / name
    fig.savefig(target, format="svg", metadata={"Date": None})
    target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")
    plt.close(fig)


def sales_view(summary, monthly, bridge):
    prior, current = summary["year_comparison"]
    fig = page(
        "01",
        "Sales grew while the number of orders declined",
        "Trading performance · January–November 2011 vs January–November 2010 · All countries",
    )
    for x, label, key, fmt in [
        (0.045, "Recorded sales", "sales_value", money),
        (0.365, "Purchase invoices", "sales_orders", lambda n: f"{n:,}"),
        (0.685, "Average invoice value", "average_order_value", lambda n: f"£{n:,.2f}"),
    ]:
        change = current[key] / prior[key] - 1
        card(fig, x, label, fmt(current[key]), f"{change:+.1%} vs comparable 2010 period")
    ax = axes(fig, (0.075, 0.36, 0.52, 0.27), "Comparable monthly sales")
    for year, color, style in [("2010", BRONZE, "--"), ("2011", TEAL, "-")]:
        data = [
            row for row in monthly if row["month"].startswith(year) and row["month"][5:7] != "12"
        ]
        ax.plot(
            range(1, 12),
            [float(r["sales_value"]) for r in data],
            color=color,
            linestyle=style,
            linewidth=2.5,
            marker="o",
            markersize=4,
            label=year,
        )
    ax.set_xticks(
        range(1, 12),
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"],
        size=10,
    )
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda n, _: f"£{n / 1_000_000:.1f}m"))
    ax.grid(axis="y", color=GRID)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    right = axes(fig, (0.80, 0.36, 0.15, 0.27), "Order change by customer group")
    labels = {
        "Both periods": "Bought in both periods",
        "Current period only": "Only in 2011 period",
        "Prior period only": "Only in 2010 period",
        "Unidentified customer": "Unidentified customer",
    }
    vals = [int(r["order_change"]) for r in bridge]
    y = np.arange(len(vals))
    right.barh(y, vals, color=[TEAL if n >= 0 else NEGATIVE for n in vals], height=0.52)
    right.set_yticks(y, [labels[r["customer_group"]] for r in bridge], size=10)
    right.invert_yaxis()
    right.axvline(0, color=MUTED, linewidth=0.7)
    span = max(abs(n) for n in vals) or 1
    right.set_xlim(-span * 1.5, span * 1.5)
    right.set_xlabel("Change in purchase invoices", size=9, color=MUTED)
    for pos, val in enumerate(vals):
        right.text(
            val + (span * 0.06 if val >= 0 else -span * 0.06),
            pos,
            f"{val:+,}",
            ha="left" if val >= 0 else "right",
            va="center",
            size=10,
            color=INK,
        )
    fig.text(0.045, 0.235, "FROM FINDING TO BUSINESS REVIEW", size=11, color=BRONZE, weight="bold")
    delta = current["sales_orders"] - prior["sales_orders"]
    fig.text(
        0.045,
        0.192,
        f"The four customer groups reconcile to {delta:+,} invoices. Investigate buying cadence and product mix within the declining groups.",
        size=12,
        color=INK,
    )
    fig.text(
        0.045,
        0.147,
        "“Only in 2011” describes this comparison window, not verified customer acquisition. The bridge explains arithmetic contribution.",
        size=10,
        color=MUTED,
    )
    footer(
        fig,
        "Sales include retained delivery/service charges; cancellations remain separate. Compare the same months before interpreting growth.",
    )
    save(fig, "sales-overview.svg")


def client_view(summary, segments, cohorts):
    fig = page(
        "02",
        "Understand the relationship behind repeat purchases",
        "Client development · Snapshot: 1 December 2011 · Frequency and spending: preceding 12 complete months",
    )
    data = {r["segment"]: r for r in segments}
    card(
        fig,
        0.045,
        "Identified customers",
        f"{summary['customers']:,}",
        f"{summary['known_customer_value_coverage']:.1%} of sales value linked to a customer",
    )
    card(
        fig,
        0.365,
        "Repeat within 90 days",
        f"{summary['repeat_90d_rate']:.1%}",
        f"{summary['repeated_90d']:,} / {summary['eligible_90d']:,} with a complete window",
    )
    card(
        fig,
        0.685,
        "Lapsed repeat buyers",
        f"{int(data['Lapsed repeat']['customers']):,}",
        "Last purchase >90 days ago; ≥2 orders in 12 months",
    )
    order = [
        "Active repeat",
        "Recent single-order",
        "Lapsed repeat",
        "Lapsed single-order",
        "No orders in last 12 months",
    ]
    counts = [int(data[n]["customers"]) for n in order]
    ax = axes(fig, (0.185, 0.36, 0.25, 0.26), "Customer portfolio")
    ax.barh(range(5), counts, height=0.53, color=[TEAL, TEAL, BRONZE, TEAL, TEAL])
    ax.set_yticks(
        range(5),
        [
            "Active repeat",
            "Recent single-order",
            "Lapsed repeat",
            "Lapsed single-order",
            "No purchases in 12m",
        ],
        size=10,
    )
    ax.invert_yaxis()
    ax.set_xlim(0, max(counts) * 1.23)
    ax.grid(axis="x", color=GRID)
    ax.set_xlabel("Customers", color=MUTED, size=9)
    for i, n in enumerate(counts):
        ax.text(n + 30, i, f"{n:,}", va="center", size=10, color=INK)
    # First 12 observed cohorts have complete M1–M6 windows. Full cohorts remain in Tableau.
    months = sorted({r["cohort_month"] for r in cohorts})[:12]
    matrix = np.full((len(months), 6), np.nan)
    sizes = {}
    for row in cohorts:
        month = row["cohort_month"]
        idx = int(row["month_index"])
        if month in months and 1 <= idx <= 6:
            sizes[month] = int(row["cohort_customers"])
            if row["repeat_rate"] != "":
                matrix[months.index(month), idx - 1] = float(row["repeat_rate"])
    heat = axes(fig, (0.615, 0.30, 0.325, 0.33), "Monthly purchasing · first 12 observed cohorts")
    cmap = LinearSegmentedColormap.from_list("client_teal", [PAPER, "#A7C4B5", TEAL])
    cmap.set_bad("#E3E1DA")
    heat.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    heat.set_xticks(range(6), [f"M{i}" for i in range(1, 7)], size=10)
    heat.xaxis.tick_top()
    heat.set_yticks(range(12), [f"{m[:7]}  ·  n={sizes[m]:,}" for m in months], size=9)
    for y in range(12):
        for x in range(6):
            if not np.isnan(matrix[y, x]):
                heat.text(
                    x,
                    y,
                    f"{matrix[y, x]:.0%}",
                    ha="center",
                    va="center",
                    size=9,
                    color="white" if matrix[y, x] > 0.65 else INK,
                )
    fig.text(
        0.615,
        0.257,
        "M0 omitted (100% by definition). Full cohort history in Tableau.",
        size=9,
        color=MUTED,
    )
    fig.text(0.045, 0.205, "REVIEW PRIORITY", size=11, color=BRONZE, weight="bold")
    value = float(data["Lapsed repeat"]["sales_value_12m"])
    fig.text(
        0.045,
        0.164,
        f"The {int(data['Lapsed repeat']['customers']):,} lapsed repeat buyers account for £{value:,.0f} of recorded sales in the preceding 12 months.",
        size=12,
        color=INK,
    )
    fig.text(
        0.045,
        0.126,
        "Review their purchase cadence and product preferences before choosing a follow-up approach.",
        size=11,
        color=MUTED,
    )
    footer(
        fig,
        "Groups describe observed activity. Monthly cohort purchasing and 90-day repeat use different, explicitly defined denominators.",
    )
    save(fig, "client-development.svg")


def product_view(products, diagnostics):
    comparison = diagnostics["comparison"]
    fig = page(
        "03",
        "Find the products behind the change in sales",
        "Product preferences · January–November 2011 vs January–November 2010 · Merchandise only · All countries",
    )
    card(
        fig,
        0.045,
        "Merchandise sales",
        money(comparison["current_merchandise_value"]),
        "Delivery and other non-merchandise shown separately",
    )
    card(
        fig,
        0.365,
        "Merchandise invoices",
        f"{comparison['current_merchandise_orders']:,}",
        "Distinct invoices containing at least one merchandise line",
    )
    card(
        fig,
        0.685,
        "Top 10 product share",
        f"{comparison['top10_current_share']:.1%}",
        "Top 10 codes by value ÷ all merchandise value",
    )
    sorted_rows = sorted(products, key=lambda r: float(r["value_change"]))
    chosen = sorted_rows[:4] + sorted_rows[-4:]
    chosen.sort(key=lambda r: float(r["value_change"]), reverse=True)
    values = [float(r["value_change"]) for r in chosen]
    ax = axes(
        fig,
        (0.40, 0.30, 0.55, 0.34),
        "Largest product contributions to value change · four increases and four decreases",
    )
    ax.barh(
        range(len(chosen)),
        values,
        color=[TEAL if n >= 0 else NEGATIVE for n in values],
        height=0.55,
    )
    ax.set_yticks(
        range(len(chosen)),
        [f"{r['product_label'][:36]}  [{r['product_key']}]" for r in chosen],
        size=9,
    )
    ax.invert_yaxis()
    ax.axvline(0, color=MUTED, linewidth=0.8)
    span = max(abs(n) for n in values) or 1
    ax.set_xlim(min(values) - span * 0.2, max(values) + span * 0.23)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda n, _: f"£{n / 1000:,.0f}k"))
    ax.grid(axis="x", color=GRID)
    for pos, val in enumerate(values):
        ax.text(
            val + (span * 0.02 if val >= 0 else -span * 0.02),
            pos,
            f"{val / 1000:+,.1f}k",
            va="center",
            ha="left" if val >= 0 else "right",
            size=10,
            color=INK,
        )
    remainder = sum(float(r["value_change"]) for r in products) - sum(values)
    fig.text(
        0.045,
        0.225,
        f"Other products: £{remainder:+,.0f} change. All products reconcile to £{comparison['current_merchandise_value'] - comparison['prior_merchandise_value']:+,.0f}.",
        size=11,
        color=INK,
    )
    fig.text(0.045, 0.178, "NEXT QUESTION", size=11, color=BRONZE, weight="bold")
    fig.text(
        0.045,
        0.14,
        "Use Tableau to compare product presence across customer groups and distinguish broad demand from a few large orders.",
        size=12,
        color=INK,
    )
    footer(
        fig,
        "Product invoice counts overlap. Penetration uses all merchandise invoices in the selected date/country/customer-group scope.",
    )
    save(fig, "product-preferences.svg")


def main():
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.serif": ["Georgia", "DejaVu Serif"],
            "font.size": 11,
            "svg.fonttype": "none",
            "svg.hashsalt": "retail-client-development-v2",
        }
    )
    OUTPUT.mkdir(exist_ok=True)
    summary = json.loads((RESULTS / "summary.json").read_text())
    diagnostics = json.loads((RESULTS / "diagnostic_summary.json").read_text())
    sales_view(summary, read_csv("monthly.csv"), read_csv("order_bridge.csv"))
    client_view(summary, read_csv("segments.csv"), read_csv("cohorts.csv"))
    product_view(read_csv("product_changes.csv"), diagnostics)
    print("Rendered trading, client-development and product-preferences previews.")


if __name__ == "__main__":
    main()
