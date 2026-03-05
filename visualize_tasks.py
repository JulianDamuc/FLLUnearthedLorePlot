"""
FLL Unearthed – Task Completion Time Visualizer
================================================
Accepts a list of time strings in "M:SS" or "MM:SS" format (range 00:00 – 2:30).
  • "00:00"  → task was NOT completed
  • Any other time → seconds elapsed when the task was completed

Produces a PowerPoint-ready PNG with two side-by-side panels:
  Left  – histogram of completion times (bins of 15 seconds)
  Right – donut chart showing Done vs. Not Done ratio
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, safe for all environments

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import numpy as np
from pathlib import Path


# ── colour palette (PowerPoint-friendly) ────────────────────────────────────
DONE_COLOR       = "#2196F3"   # blue
NOT_DONE_COLOR   = "#FF5252"   # red-accent
BG_COLOR         = "#FFFFFF"
GRID_COLOR       = "#E0E0E0"
TEXT_COLOR       = "#212121"
ACCENT_COLOR     = "#0D47A1"   # dark-blue for accents
BAR_LABEL_OFFSET = 0.05        # small vertical gap between bar top and count label


# ── helpers ──────────────────────────────────────────────────────────────────
def parse_time(t: str) -> int:
    """Convert 'M:SS' or 'MM:SS' string to total seconds."""
    parts = t.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid time format: '{t}' – expected M:SS or MM:SS")
    minutes, seconds = int(parts[0]), int(parts[1])
    total = minutes * 60 + seconds
    if not (0 <= total <= 150):
        raise ValueError(f"Time '{t}' is out of range (00:00 – 2:30)")
    return total


def seconds_to_label(s: int) -> str:
    """Return 'M:SS' display label for an integer second value."""
    return f"{s // 60}:{s % 60:02d}"


# ── main visualisation ────────────────────────────────────────────────────────
def visualize(
    time_points: list[str],
    output_path: str | Path = "task_completion.png",
    title: str = "FLL Unearthed – Task Completion Times",
) -> Path:
    """
    Build and save the combined chart.

    Parameters
    ----------
    time_points : list of strings like "1:45", "0:30", "00:00", …
    output_path : where to save the PNG (default: task_completion.png)
    title       : overall figure title

    Returns
    -------
    Path to the saved file.
    """
    if not time_points:
        raise ValueError("time_points list is empty – nothing to visualise.")

    # ── parse & split ────────────────────────────────────────────────────────
    all_seconds = [parse_time(t) for t in time_points]
    total       = len(all_seconds)
    not_done    = [s for s in all_seconds if s == 0]
    done        = [s for s in all_seconds if s != 0]

    n_not_done = len(not_done)
    n_done     = len(done)

    # ── figure layout ────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(14, 6.5), facecolor=BG_COLOR)
    fig.suptitle(
        title,
        fontsize=18, fontweight="bold", color=TEXT_COLOR,
        y=0.97, x=0.5,
    )

    # Two columns: histogram (wider) | donut
    gs = fig.add_gridspec(1, 2, width_ratios=[2, 1], wspace=0.35,
                          left=0.07, right=0.97, top=0.88, bottom=0.13)
    ax_hist  = fig.add_subplot(gs[0, 0])
    ax_donut = fig.add_subplot(gs[0, 1])

    # ── LEFT: histogram of completion times ──────────────────────────────────
    if n_done > 0:
        # Bins every 15 seconds: 0–15, 15–30, …, 135–150 (plus one boundary at 150)
        bin_edges  = list(range(15, 151, 15))  # [15, 30, 45, …, 150]
        # Prepend 1 so completions from 00:01 fall in the first bin
        bin_edges  = [1] + bin_edges

        counts, edges = np.histogram(done, bins=bin_edges)

        bar_width = [(edges[i + 1] - edges[i]) * 0.80 for i in range(len(counts))]
        bar_left  = [edges[i] + (edges[i + 1] - edges[i]) * 0.10 for i in range(len(counts))]

        bars = ax_hist.bar(
            bar_left, counts, width=bar_width,
            color=DONE_COLOR, edgecolor="white", linewidth=0.8,
            label="Task completed", align="edge", zorder=3,
        )

        # Annotate each bar with its count (skip zeros)
        for bar, count in zip(bars, counts):
            if count > 0:
                ax_hist.text(
                    bar.get_x() + bar.get_width() / 2,
                    count + BAR_LABEL_OFFSET,
                    str(int(count)),
                    ha="center", va="bottom",
                    fontsize=9, color=TEXT_COLOR, fontweight="bold",
                )

        # X-axis ticks at bin edges labelled as M:SS
        tick_positions = [e for e in bin_edges]
        tick_labels    = [seconds_to_label(e) for e in tick_positions]
        ax_hist.set_xticks(tick_positions)
        ax_hist.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=8)
        ax_hist.set_xlim(bin_edges[-1] + 2, bin_edges[0] - 2)
    else:
        ax_hist.text(
            0.5, 0.5, "No completed tasks",
            ha="center", va="center", transform=ax_hist.transAxes,
            fontsize=14, color=NOT_DONE_COLOR,
        )
        ax_hist.set_xticks([])

    # Styling
    ax_hist.set_facecolor(BG_COLOR)
    ax_hist.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax_hist.set_ylabel("Number of Teams", fontsize=11, color=TEXT_COLOR, labelpad=8)
    ax_hist.set_xlabel("Completion Time (M:SS)", fontsize=11, color=TEXT_COLOR, labelpad=8)
    ax_hist.set_title("Distribution of Completion Times", fontsize=13,
                      color=TEXT_COLOR, pad=10)
    ax_hist.tick_params(colors=TEXT_COLOR)
    ax_hist.spines[["top", "right"]].set_visible(False)
    ax_hist.spines[["left", "bottom"]].set_color(GRID_COLOR)
    ax_hist.yaxis.grid(True, color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax_hist.set_axisbelow(True)

    # "Not done" annotation below the histogram
    if n_not_done > 0:
        pct = n_not_done / total * 100
        ax_hist.annotate(
            f"⚠  {n_not_done} team(s) did NOT complete the task "
            f"({pct:.1f} %)",
            xy=(0.5, -0.30), xycoords="axes fraction",
            ha="center", va="center",
            fontsize=10, color=NOT_DONE_COLOR, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFEBEE",
                      edgecolor=NOT_DONE_COLOR, linewidth=1.2),
        )

    # ── RIGHT: donut chart ───────────────────────────────────────────────────
    sizes  = [n_done, n_not_done]
    colors = [DONE_COLOR, NOT_DONE_COLOR]
    labels = [f"Completed\n{n_done} ({n_done/total*100:.1f}%)",
              f"Not Done\n{n_not_done} ({n_not_done/total*100:.1f}%)"]

    wedge_props = dict(width=0.55, edgecolor="white", linewidth=2)
    wedges, texts = ax_donut.pie(
        sizes, colors=colors, wedgeprops=wedge_props,
        startangle=90, counterclock=False,
    )

    # Centre text
    ax_donut.text(0, 0, f"{total}\nTeams",
                  ha="center", va="center",
                  fontsize=13, fontweight="bold", color=TEXT_COLOR)

    # Legend
    legend_patches = [
        mpatches.Patch(color=DONE_COLOR,     label=labels[0]),
        mpatches.Patch(color=NOT_DONE_COLOR, label=labels[1]),
    ]
    ax_donut.legend(handles=legend_patches, loc="lower center",
                    bbox_to_anchor=(0.5, -0.18), fontsize=9,
                    frameon=False, ncol=1)
    ax_donut.set_title("Completion Overview", fontsize=13,
                       color=TEXT_COLOR, pad=10)

    # ── save ────────────────────────────────────────────────────────────────
    output_path = Path(output_path)
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"Chart saved → {output_path.resolve()}")
    return output_path


# ── example / demo ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Sample data: mix of completion times and "00:00" (not done)
    sample_data = [
        "00:00", "00:00", "00:00",          # did not do the task
        "0:22", "0:35", "0:48",
        "1:00", "1:05", "1:12", "1:15",
        "1:30", "1:30", "1:45",
        "2:00", "2:10", "2:20", "2:28",
        "0:55", "1:38", "00:00",
    ]

    visualize(sample_data, output_path="task_completion.png")
