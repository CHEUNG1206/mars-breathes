# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""
Is it just Gale Crater? Three landers, three places, forty years apart, on one circle.

    uv run landers.py

Writes out/three-landers.png. Viking Lander 1 (Chryse Planitia, 1976-1982) and
Viking Lander 2 (Utopia Planitia, 1976-1980) next to Curiosity (Gale Crater,
2012-2026). Same circle as plot.py: angle is the season (Ls), distance from the
centre is the daily pressure. If the breath were local weather, the three would
disagree about when to breathe in and out. They do not.
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt

from plot import FAINT, INK, PAPER, load, mars_years, with_breaks

VIKING = Path(__file__).parent / "data" / "viking-daily-pressure.dat"
OUT = Path(__file__).parent / "out"
PICTURE = "three-landers.png"

MISSING = -9.999           # the Viking file's word for "no reading" (see the .lbl file)
LANDERS = {                # name in the file: (label, colour); drawn in this order
    "MSL": ("Curiosity, Gale Crater, 2012–2026", "#fd8d3c"),
    "VL1": ("Viking Lander 1, Chryse Planitia, 1976–1982", "#5ec4c4"),
    "VL2": ("Viking Lander 2, Utopia Planitia, 1976–1980", "#a99be0"),
}


def viking(path):
    """Each Viking lander's sols as (sol, ls, pressure in pascals).

    One row per sol, columns separated by spaces: lander, Viking year, Ls, sol,
    daily mean pressure in millibars, then fourteen columns this picture does not
    use. A millibar is 100 pascals."""
    landers = {}
    for line in path.read_text(encoding="ascii").splitlines():   # the loop over the numbers
        columns = line.split()
        if len(columns) < 5:
            continue
        name, ls, sol, mbar = columns[0], float(columns[2]), int(columns[3]), float(columns[4])
        if mbar == MISSING:
            continue
        landers.setdefault(name, []).append((sol, ls, mbar * 100))
    return landers


def split_years(readings):
    """Cut one lander's sols into Mars years wherever the season wraps past Ls 360,
    so each year is drawn as its own loop instead of a line back across the circle."""
    years, current = [], []
    for reading in readings:
        if current and reading[1] < current[-1][1] - 180:
            years.append(current)
            current = []
        current.append(reading)
    if current:
        years.append(current)
    return years


def main():
    sites = viking(VIKING)
    sites["MSL"] = [r for readings in mars_years(load()).values() for r in readings]
    for name, readings in sites.items():
        pressures = [p for _, _, p in readings]
        print(f"{name}: {len(readings)} sols, {len(split_years(readings))} loops, "
              f"{min(pressures):.0f} to {max(pressures):.0f} Pa, "
              f"average {sum(pressures) / len(pressures):.0f} Pa")

    fig = plt.figure(figsize=(10, 10.8), facecolor=PAPER)
    ax = fig.add_subplot(projection="polar", facecolor=PAPER)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    for name, (label, colour) in LANDERS.items():
        readings = sites[name]
        for i, year in enumerate(split_years(readings)):
            ax.plot(*with_breaks(year), color=colour, linewidth=0.9, alpha=0.6 if name == "MSL" else 0.95,
                    label=label if i == 0 else None)

    ax.set_rlim(0, 1100)
    ax.set_rticks([300, 600, 900])
    ax.set_yticklabels(["300 Pa", "600 Pa", "900 Pa"], color="#a89a90", fontsize=9)
    ax.set_rlabel_position(22)
    ax.set_xticks([math.radians(a) for a in (0, 90, 180, 270)])
    ax.set_xticklabels(["Ls 0°\nnorthern spring", "Ls 90°\nnorthern summer",
                        "Ls 180°\nnorthern autumn", "Ls 270°\nnorthern winter"],
                       color=INK, fontsize=10)
    ax.tick_params(axis="x", pad=14)
    ax.grid(color=FAINT, linewidth=0.6)
    ax.spines["polar"].set_color(FAINT)

    note = dict(color=INK, fontsize=9.5, ha="center", va="center")
    ax.text(math.radians(150), 420, "all three thin out\nin southern winter", **note)
    ax.text(math.radians(260), 420, "and fill up again\nin southern summer", **note)

    fig.text(0.5, 0.965, "Mars breathes everywhere", color="#f4ece6", fontsize=22,
             ha="center", va="top", weight="bold")
    fig.text(0.5, 0.925, "Daily air pressure at three landing sites, one loop per Martian year",
             color="#c9bcb2", fontsize=11, ha="center", va="top")
    legend = fig.legend(loc="lower center", bbox_to_anchor=(0.5, 0.075), frameon=False,
                        fontsize=10, labelcolor=INK, ncol=1)
    for line in legend.get_lines():
        line.set_linewidth(3)
    fig.text(0.5, 0.02, "Angle: season (solar longitude, Ls). Distance from centre: daily mean pressure in pascals, "
             "as measured.\nThe sites sit at different heights, so their averages differ; the timing does not.\n"
             "Data: NASA PDS Atmospheres Node (Viking MET); NASA/JPL-Caltech, CAB (CSIC-INTA) (Curiosity REMS).",
             color="#8f8279", fontsize=8, ha="center", va="bottom", linespacing=1.6)
    fig.subplots_adjust(top=0.84, bottom=0.2)

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=150, facecolor=PAPER)
    print(f"saved out/{PICTURE}")


if __name__ == "__main__":
    main()
