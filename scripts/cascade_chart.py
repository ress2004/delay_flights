"""Renders the "delays are inherited" cascade chart, styled to match the
departure-board palette used in docs/index.html (--board / --amber / --good
/ --bad). Run with: python scripts/cascade_chart.py
"""
import os

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

labels = ["First flight\nof the day", "Previous flight\non time",
          "Previous flight\n15–60 min late", "Previous flight\n60+ min late"]
values = [13.5, 12.9, 66.3, 82.5]
flights = ["1.7M flights", "4.1M flights", "671K flights", "345K flights"]

# Same status colors docs/index.html already uses for good/warn/bad verdicts
# (--good/--amber/--bad, dark-surface variants) — brand-consistent, not a
# fresh categorical palette.
BOARD = "#161B26"
BOARD_LINE = "#2A3140"
AMBER = "#FFB300"
AMBER_DIM = "#B98200"
GOOD = "#4ADE9C"
BAD = "#FF6B6A"
colors = [GOOD, GOOD, AMBER, BAD]

plt.rcParams["font.family"] = "DejaVu Sans Mono"  # closest local stand-in for the board's IBM Plex Mono


def rounded_top_bar(ax, x_center, width, height, color, rx, ry, zorder=3):
    """A bar with only its top two corners rounded; baseline stays flat."""
    x0, x1 = x_center - width / 2, x_center + width / 2
    ry = min(ry, height)
    verts = [
        (x0, 0),
        (x0, height - ry),
        (x0, height), (x0 + rx, height),
        (x1 - rx, height),
        (x1, height), (x1, height - ry),
        (x1, 0),
        (x0, 0),
    ]
    codes = [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3,
             Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="none", zorder=zorder))


fig, ax = plt.subplots(figsize=(10, 6.2), dpi=220)
fig.patch.set_facecolor(BOARD)
ax.set_facecolor(BOARD)

x_positions = range(len(labels))
bar_width = 0.62
for x, v, color, n in zip(x_positions, values, colors, flights):
    rounded_top_bar(ax, x, bar_width, v, color, rx=0.05, ry=2.6)
    ax.text(x, v + 2.8, f"{v}%", ha="center", color="#ffffff", fontsize=17, fontweight="bold", zorder=4)
    ax.text(x, -16.5, n, ha="center", color=AMBER_DIM, fontsize=9.5)

ax.set_xlim(-0.6, len(labels) - 0.4)
ax.set_xticks(list(x_positions))
ax.set_xticklabels(labels, color=AMBER_DIM, fontsize=11)

ax.set_title("Flight delays are inherited, not random",
             color="#ffffff", fontsize=18, fontweight="bold", pad=30, loc="left")
ax.text(0, 1.045, "% of US flights departing 15+ min late, by what the aircraft did before · 6.9M flights, 2025",
        transform=ax.transAxes, color=AMBER_DIM, fontsize=10.5)

ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
ax.tick_params(colors=AMBER_DIM, labelsize=11, length=0)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.grid(axis="y", color=BOARD_LINE, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

fig.text(0.985, 0.015, "Source: US DOT/BTS · analysis in BigQuery",
         ha="right", color=AMBER_DIM, fontsize=8.5)

out_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "cascade_chart.png")

plt.tight_layout(rect=[0, 0.07, 1, 1])
plt.savefig(out_path, bbox_inches="tight", facecolor=BOARD, pad_inches=0.35)
print(f"saved {out_path}")
