"""Render three portable, source-linked views from the reconciled SQL aggregates."""

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
NAVY = "#183247"
TEAL = "#137F83"
LIGHT_TEAL = "#9ED6CE"
AMBER = "#B67425"
GREY = "#5C6E7B"
GRID = "#E2E9ED"
PAPER = "#F7F9FA"


def read_csv(name):
    with (RESULTS / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def money(value, decimals=2):
    return f"£{value / 1_000_000:.{decimals}f}m"


def pct(value):
    return f"{value:.1%}"


def page(title, subtitle):
    fig = plt.figure(figsize=(16, 10.5), facecolor="white")
    fig.text(0.045, 0.963, "RETAIL CUSTOMER & SALES ANALYSIS", size=11, weight="bold", color=TEAL)
    fig.text(0.045, 0.919, title, size=25, weight="bold", color=NAVY)
    fig.text(0.045, 0.887, subtitle, size=12, color=GREY)
    return fig


def card(fig, x, width, label, value, detail):
    ax = fig.add_axes((x, 0.76, width, 0.095))
    ax.set_facecolor(PAPER)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(0.06, 0.76, label, transform=ax.transAxes, size=11, color=GREY)
    ax.text(0.06, 0.37, value, transform=ax.transAxes, size=24, weight="bold", color=NAVY)
    ax.text(0.06, 0.10, detail, transform=ax.transAxes, size=10, color=GREY)


def axes(fig, rect, title):
    ax = fig.add_axes(rect)
    ax.set_title(title, loc="left", pad=16, size=14, weight="bold", color=NAVY)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=GREY, length=0, pad=6)
    ax.set_axisbelow(True)
    return ax


def footer(fig, extra=""):
    fig.text(0.045, 0.043, extra, size=10, color=GREY)
    fig.text(
        0.045,
        0.022,
        "Source: Chen (2012), UCI Online Retail II · CC BY 4.0. "
        "UK online gift retailer · GBP · Dec 2009–Nov 2011. Partial Dec 2011 excluded.",
        size=9.5,
        color=GREY,
    )


def save(fig, filename):
    target = OUTPUT / filename
    fig.savefig(target, format="svg", metadata={"Date": None})
    target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")
    plt.close(fig)


def sales_view(summary, monthly, countries, quality):
    previous, current = summary["year_comparison"]
    growth = current["sales_value"] / previous["sales_value"] - 1
    fig = page(
        "Sales are steady; order count and basket value moved differently",
        f"Jan–Nov 2011 recorded sales {growth:+.1%} versus the same months of 2010. "
        "Read cancellation records separately.",
    )
    card(fig, 0.045, 0.215, "Recorded sales", money(summary["sales_value"]), "24 complete months")
    card(
        fig,
        0.277,
        0.215,
        "Purchase invoices",
        f"{summary['sales_orders']:,}",
        "Distinct eligible invoices",
    )
    card(
        fig,
        0.509,
        0.215,
        "Average invoice value",
        f"£{summary['average_order_value']:,.0f}",
        "Recorded sales ÷ purchase invoices",
    )
    card(
        fig,
        0.741,
        0.214,
        "Cancellation value",
        money(summary["cancellation_value"]),
        "Recorded in the same window",
    )

    x = np.arange(len(monthly))
    values = [float(row["sales_value"]) for row in monthly]
    month_labels = [row["month"][:7] for row in monthly]
    ax = axes(fig, (0.075, 0.445, 0.52, 0.245), "Monthly recorded sales")
    ax.plot(x, values, color=TEAL, linewidth=2.7, marker="o", markersize=4)
    ax.fill_between(x, values, color=TEAL, alpha=0.07)
    ax.set_ylim(0, max(values) * 1.18)
    ax.set_xlim(-0.5, len(x) - 0.5)
    ax.set_xticks(x[::3], month_labels[::3], rotation=0, size=9)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"£{value / 1_000_000:.1f}m"))
    ax.grid(axis="y", color=GRID)

    panel = fig.add_axes((0.65, 0.432, 0.30, 0.265))
    panel.axis("off")
    panel.text(0, 1.03, "Like-for-like months", size=14, weight="bold", color=NAVY)
    panel.text(0, 0.91, "January–November", size=11, color=GREY)
    panel.text(0.49, 0.80, "2010", size=10, color=GREY, ha="right")
    panel.text(0.74, 0.80, "2011", size=10, color=GREY, ha="right")
    panel.text(1.00, 0.80, "Change", size=10, color=GREY, ha="right")
    metrics = [
        ("Recorded sales", "sales_value", money),
        ("Invoices", "sales_orders", lambda value: f"{value:,}"),
        ("Avg. invoice", "average_order_value", lambda value: f"£{value:,.0f}"),
    ]
    for y, (label, key, formatter) in zip((0.66, 0.49, 0.32), metrics):
        change = current[key] / previous[key] - 1
        panel.text(0, y, label, size=11, color=NAVY)
        panel.text(0.49, y, formatter(previous[key]), size=11, ha="right", color=NAVY)
        panel.text(0.74, y, formatter(current[key]), size=11, ha="right", color=NAVY)
        panel.text(1, y, f"{change:+.1%}", size=11, weight="bold", ha="right", color=TEAL)
    order_effect = (current["sales_orders"] - previous["sales_orders"]) * previous[
        "average_order_value"
    ]
    basket_effect = current["sales_orders"] * (
        current["average_order_value"] - previous["average_order_value"]
    )

    def signed_thousands(value):
        return f"{'+' if value >= 0 else '−'}£{abs(value) / 1000:,.0f}k"

    panel.text(
        0,
        0.10,
        f"Arithmetic bridge: invoices {signed_thousands(order_effect)}; "
        f"invoice value {signed_thousands(basket_effect)}.",
        size=10,
        color=GREY,
    )
    panel.text(
        0, 0.00, "This decomposition does not explain customer motives.", size=9.5, color=GREY
    )

    ax = axes(fig, (0.075, 0.13, 0.52, 0.23), "Cancellation amounts by recorded month")
    cancels = [float(row["cancellation_value"]) for row in monthly]
    ax.bar(x, cancels, color=AMBER, width=0.68)
    ax.set_xticks(x[::3], month_labels[::3], size=9)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"£{value / 1000:,.0f}k"))
    ax.set_xlim(-0.5, len(x) - 0.5)
    ax.grid(axis="y", color=GRID)

    ax = axes(fig, (0.76, 0.13, 0.19, 0.23), "Largest sales markets")
    top = countries[:5]
    positions = np.arange(len(top))
    ax.barh(positions, [float(row["sales_value"]) for row in top], color=TEAL, height=0.55)
    ax.set_yticks(positions, [row["country"] for row in top], size=10)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"£{value / 1_000_000:.0f}m"))
    ax.grid(axis="x", color=GRID)
    footer(
        fig,
        "Overlapping sheets reconciled; remaining identical rows retained. "
        "Cancellations are not matched to original purchases. See data-quality notes.",
    )
    save(fig, "sales-overview.svg")


def repeat_view(summary, cohorts):
    fig = page(
        "Customer purchasing over time",
        "Compare the same observation window before judging repeat purchasing. "
        "Customer measures use identified buyers only.",
    )
    card(
        fig,
        0.045,
        0.29,
        "Repeat within 90 days",
        pct(summary["repeat_90d_rate"]),
        f"{summary['repeated_90d']:,} of {summary['eligible_90d']:,} mature customers",
    )
    card(
        fig,
        0.355,
        0.29,
        "Two or more orders in 24 months",
        pct(summary["repeat_customer_share"]),
        f"{summary['repeat_customers']:,} of {summary['customers']:,} observed customers",
    )
    card(
        fig,
        0.665,
        0.29,
        "Sales linked to a customer ID",
        pct(summary["known_customer_value_coverage"]),
        "Coverage of recorded sales value",
    )

    months = sorted({row["cohort_month"] for row in cohorts})
    sizes = {row["cohort_month"]: int(row["cohort_customers"]) for row in cohorts}
    matrix = np.full((len(months), 12), np.nan)
    for row in cohorts:
        value = row["repeat_rate"]
        if value != "":
            matrix[months.index(row["cohort_month"]), int(row["month_index"])] = float(value)
    ax = axes(fig, (0.18, 0.14, 0.71, 0.51), "Monthly purchasing by first observed purchase cohort")
    cmap = LinearSegmentedColormap.from_list("retail_teal", ["#F0F7F7", "#74BEB8", TEAL, NAVY])
    cmap.set_bad("#E8EDF0")
    im = ax.imshow(matrix, vmin=0, vmax=1, cmap=cmap, aspect="auto", interpolation="nearest")
    for y in range(len(months)):
        for x in range(12):
            if not np.isnan(matrix[y, x]):
                ax.text(
                    x,
                    y,
                    f"{matrix[y, x]:.0%}",
                    ha="center",
                    va="center",
                    size=8,
                    color="white" if matrix[y, x] >= 0.58 else NAVY,
                )
    ax.set_yticks(
        np.arange(len(months)), [f"{month[:7]}   n={sizes[month]:,}" for month in months], size=9
    )
    ax.set_xticks(np.arange(12), [str(n) for n in range(12)], size=10)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.set_xlabel("Months since first observed purchase", color=GREY, labelpad=9, size=10)
    ax.set_xticks(np.arange(-0.5, 12, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(months), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.3)
    ax.tick_params(which="minor", bottom=False, left=False)
    cax = fig.add_axes((0.915, 0.27, 0.013, 0.30))
    colorbar = fig.colorbar(im, cax=cax, format=FuncFormatter(lambda value, _: f"{value:.0%}"))
    colorbar.outline.set_visible(False)
    colorbar.ax.tick_params(labelsize=9, length=0, colors=GREY)
    fig.text(
        0.18,
        0.102,
        "Cell = customers with a purchase in that month ÷ original cohort customers. "
        "Grey cells are not yet observable. Month 0 is 100% by definition.",
        size=10,
        color=GREY,
    )
    footer(
        fig,
        "The first observed order may not be a lifetime first purchase. "
        "Monthly purchasing is not continuous retention; 90-day repeat uses only fully observed customers.",
    )
    save(fig, "customer-repeat.svg")


def priority_view(summary, segments):
    order = [
        "Active repeat",
        "Recent single-order",
        "Lapsed repeat",
        "Lapsed single-order",
        "No orders in last 12 months",
    ]
    data = {row["segment"]: row for row in segments}
    total_value = sum(float(row["sales_value_12m"]) for row in segments)
    active_share = float(data["Active repeat"]["sales_value_12m"]) / total_value
    fig = page(
        "Repeat buyers account for most identified-customer sales",
        f"Active repeat buyers account for {active_share:.1%} of identified-customer sales "
        "in Dec 2010–Nov 2011. Snapshot: 1 December 2011.",
    )
    card(
        fig,
        0.045,
        0.29,
        "Identified customers",
        f"{summary['customers']:,}",
        "Observed across 24 months",
    )
    card(
        fig,
        0.355,
        0.29,
        "Active repeat buyers",
        f"{int(data['Active repeat']['customers']):,}",
        "Purchased ≤90 days ago; ≥2 orders in 12 months",
    )
    card(
        fig,
        0.665,
        0.29,
        "Lapsed repeat buyers",
        f"{int(data['Lapsed repeat']['customers']):,}",
        "Purchased >90 days ago; ≥2 orders in 12 months",
    )

    y = np.arange(len(order))
    counts = [int(data[name]["customers"]) for name in order]
    shares = [float(data[name]["sales_value_12m"]) / total_value for name in order]
    colors = [TEAL, "#4D9DA0", AMBER, "#C9A171", "#ADBBC4"]
    left = axes(fig, (0.225, 0.43, 0.31, 0.255), "Customers by segment")
    left.barh(y, counts, color=colors, height=0.57)
    left.set_yticks(
        y,
        [
            name.replace("No orders in last 12 months", "No orders in last 12 months")
            for name in order
        ],
        size=11,
    )
    left.invert_yaxis()
    left.set_xlim(0, max(counts) * 1.28)
    left.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
    left.grid(axis="x", color=GRID)
    for pos, count in zip(y, counts):
        left.text(count + max(counts) * 0.025, pos, f"{count:,}", va="center", size=11, color=NAVY)

    right = axes(fig, (0.64, 0.43, 0.29, 0.255), "Share of last-12-month sales")
    right.barh(y, shares, color=colors, height=0.57)
    right.set_yticks(y, [""] * len(y))
    right.invert_yaxis()
    right.set_xlim(0, 1.04)
    right.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))
    right.grid(axis="x", color=GRID)
    for pos, share in zip(y, shares):
        right.text(share + 0.02, pos, f"{share:.1%}", va="center", size=11, color=NAVY)
    fig.text(
        0.225,
        0.382,
        "Recent = last purchase ≤90 days ago. Single-order = one invoice in the last 12 months. "
        "All groups are mutually exclusive.",
        size=10,
        color=GREY,
    )
    fig.text(
        0.045, 0.315, "Questions to take into a business review", size=15, weight="bold", color=NAVY
    )

    prompts = [
        (
            0.045,
            TEAL,
            "Active repeat",
            "Review service and assortment needs.",
            "Many customers are wholesalers.\nCheck buying cadence before choosing an offer.",
        ),
        (
            0.355,
            AMBER,
            "Lapsed repeat",
            "Investigate changes in purchasing.",
            "Compare prior cadence and product mix.\nSeasonality may explain a long gap.",
        ),
        (
            0.665,
            "#4D9DA0",
            "Recent single-order",
            "Explore barriers to a second purchase.",
            "Review the first basket and customer context.\nTest a proposal before assuming an effect.",
        ),
    ]
    for x, color, title, action, detail in prompts:
        ax = fig.add_axes((x, 0.115, 0.29, 0.16))
        ax.set_facecolor(PAPER)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.text(0.05, 0.78, title, transform=ax.transAxes, color=color, size=13, weight="bold")
        ax.text(0.05, 0.52, action, transform=ax.transAxes, color=NAVY, size=11)
        ax.text(0.05, 0.18, detail, transform=ax.transAxes, color=GREY, size=10, linespacing=1.6)
    footer(
        fig,
        "Segments describe observed purchases, not predicted churn. "
        "Sales shares use identified customers only; follow-up proposals need customer context and contact permissions.",
    )
    save(fig, "customer-priorities.svg")


def main():
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 11,
            "svg.fonttype": "none",
            "svg.hashsalt": "retail-analysis-v1",
        }
    )
    OUTPUT.mkdir(exist_ok=True)
    summary = json.loads((RESULTS / "summary.json").read_text())
    quality = json.loads((RESULTS / "quality.json").read_text())
    sales_view(summary, read_csv("monthly.csv"), read_csv("countries.csv"), quality)
    repeat_view(summary, read_csv("cohorts.csv"))
    priority_view(summary, read_csv("segments.csv"))
    print("Rendered sales-overview.svg, customer-repeat.svg and customer-priorities.svg")


if __name__ == "__main__":
    main()
