# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib", "pillow"]
# ///

"""
The Mars breathes loops, drawing themselves: a hand sweeps round the seasons and
each Martian year leaves its loop behind.

    uv run animate.py

Writes out/mars-breathes.gif. It takes a minute.

A frame is a function of time: frame(i) shows every reading up to the i-th step,
moves the hand to that sol's season, and writes the date and pressure underneath.
The years, the gaps and the colours come from plot.py, written once, used twice.
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from plot import load, mars_years, with_breaks

STEP = 12                  # sols per frame: about 56 frames per Martian year
FPS = 20
HOLD = 40                  # extra frames on the finished picture before the GIF loops
SIZE = 6                   # inches square
DPI = 80                   # 6 x 80 = 480 pixels; raise it and the file grows fast

PAPER = "#14100e"
INK = "#e8ddd4"
FAINT = "#3a302b"

HERE = Path(__file__).parent
OUT = HERE / "out"
PICTURE = "mars-breathes.gif"


def main():
    soles = load()
    dates = {int(entry["sol"]): entry["terrestrial_date"] for entry in soles}
    years = mars_years(soles)
    first, last = min(years), max(years)
    last_sol = max(sol for readings in years.values() for sol, _, _ in readings)
    steps = list(range(STEP, last_sol + STEP, STEP))
    print(f"{len(steps)} frames, {STEP} sols each, plus {HOLD} to hold the end")

    fig = plt.figure(figsize=(SIZE, SIZE), facecolor=PAPER)
    ax = fig.add_subplot(projection="polar", facecolor=PAPER)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rlim(0, 950)
    ax.set_rticks([300, 600, 900])
    ax.set_yticklabels(["300 Pa", "600 Pa", "900 Pa"], color="#a89a90", fontsize=7)
    ax.set_rlabel_position(22)
    ax.set_xticks([math.radians(a) for a in (0, 90, 180, 270)])
    ax.set_xticklabels(["Ls 0°", "Ls 90°", "Ls 180°", "Ls 270°"], color=INK, fontsize=8)
    ax.grid(color=FAINT, linewidth=0.5)
    ax.spines["polar"].set_color(FAINT)
    fig.subplots_adjust(top=0.82, bottom=0.15)
    fig.text(0.5, 0.96, "Mars breathes", color="#f4ece6", fontsize=15,
             ha="center", va="top", weight="bold")
    fig.text(0.5, 0.91, "Air pressure at Gale Crater, one loop per Martian year",
             color="#c9bcb2", fontsize=8.5, ha="center", va="top")
    fig.text(0.5, 0.02, "Data: NASA/JPL-Caltech, CAB (CSIC-INTA), Curiosity REMS",
             color="#8f8279", fontsize=6.5, ha="center", va="bottom")

    colours = plt.get_cmap("YlOrRd")
    lines = {}
    for year in years:
        shade = 0.25 + 0.75 * (year - first) / (last - first)
        lines[year], = ax.plot([], [], color=colours(shade), linewidth=1.0)
    hand, = ax.plot([], [], color=INK, linewidth=0.8, alpha=0.6)
    label = fig.text(0.5, 0.055, "", color=INK, fontsize=9, ha="center", va="bottom")

    def frame(i):
        """Draw everything up to sol `upto`, and point the hand at the newest reading."""
        upto = steps[min(i, len(steps) - 1)]
        newest = None
        for year, readings in years.items():         # the loop over the numbers, again
            shown = [r for r in readings if r[0] <= upto]
            lines[year].set_data(*with_breaks(shown))
            if shown:
                newest = (year, *shown[-1])
        year, sol, ls, pressure = newest
        hand.set_data([math.radians(ls)] * 2, [0, pressure])
        label.set_text(f"Mars year {year}  ·  sol {sol}  ·  {dates[sol]}  ·  {pressure:.0f} Pa")
        return [*lines.values(), hand, label]

    animation = FuncAnimation(fig, frame, frames=len(steps) + HOLD, blit=False)
    OUT.mkdir(exist_ok=True)
    animation.save(OUT / PICTURE, writer=PillowWriter(fps=FPS), dpi=DPI,
                   savefig_kwargs={"facecolor": PAPER})
    print(f"saved out/{PICTURE} ({(OUT / PICTURE).stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
