# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""
Read Curiosity's weather from data/, make one picture, save it to out/.

    uv run plot.py

Each Martian year becomes one loop around a circle. The angle is the season
(solar longitude, Ls: 0° is the northern spring equinox, 360° is the next one),
the distance from the centre is the air pressure at Gale Crater that sol.
"""

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt

FILE = "curiosity-rems-weather.json"
PICTURE = "mars-breathes.png"

FIRST_MARS_YEAR = 31      # Curiosity landed at Ls 150 of Mars Year 31 (August 2012)
GAP = 10                  # more sols than this without a reading breaks the line

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"


def number(text):
    """REMS writes '--' when it has no reading. Turn the text into a number, or None."""
    try:
        return float(text)
    except ValueError:
        return None


def mars_years(soles):
    """Split the sols into Martian years, oldest first.

    The file gives no year, only the season (Ls). A new year starts whenever Ls
    wraps around from the high 300s back to near 0, so walk through the sols in
    order and count the wraps. Each year is a list of (sol, ls, pressure); sols
    with no pressure reading are left out, so a hole in the list is a gap."""
    years = {}
    year = FIRST_MARS_YEAR
    previous_ls = None
    for entry in sorted(soles, key=lambda e: int(e["sol"])):     # the loop over the numbers
        ls = number(entry["ls"])
        if ls is None:
            continue
        if previous_ls is not None and ls < previous_ls - 180:
            year += 1
        previous_ls = ls
        pressure = number(entry["pressure"])
        if pressure is None:
            continue
        years.setdefault(year, []).append((int(entry["sol"]), ls, pressure))
    return years


def with_breaks(readings):
    """Angles (radians) and radii for one year, with a NaN wherever more than GAP
    sols went by without a reading, so matplotlib lifts the pen instead of drawing
    a straight line across the hole."""
    angles, radii = [], []
    for i, (sol, ls, pressure) in enumerate(readings):
        if i and sol - readings[i - 1][0] > GAP:
            angles.append(math.nan)
            radii.append(math.nan)
        angles.append(math.radians(ls))
        radii.append(pressure)
    return angles, radii


def load(path=DATA):
    """Every sol in the file, as a list of dicts with text values.
    The Spanish disclaimer at the top is not valid UTF-8, so replace what breaks."""
    return json.loads(path.read_bytes().decode("utf-8", errors="replace"))["soles"]


def main():
    soles = load()
    print(f"{DATA.name}: {len(soles)} sols")

    years = mars_years(soles)
    for year, readings in years.items():
        pressures = [p for _, _, p in readings]
        print(f"Mars year {year}: {len(readings):4d} sols with pressure, "
              f"Ls {readings[0][1]:3.0f} to {readings[-1][1]:3.0f}, "
              f"{min(pressures):.0f} to {max(pressures):.0f} Pa")

    fig = plt.figure(figsize=(10, 10.6), facecolor="#14100e")
    ax = fig.add_subplot(projection="polar", facecolor="#14100e")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)           # clockwise, like a clock: the year turns

    colours = plt.get_cmap("YlOrRd")
    first, last = min(years), max(years)
    for year, readings in years.items():
        angles, radii = with_breaks(readings)
        shade = 0.25 + 0.75 * (year - first) / (last - first)
        ax.plot(angles, radii, color=colours(shade), linewidth=1.0, label=f"Mars year {year}")

    every = [p for readings in years.values() for _, _, p in readings]
    mean = sum(every) / len(every)
    ring = [math.radians(a) for a in range(361)]
    ax.plot(ring, [mean] * len(ring), color="#e8ddd4", linewidth=0.8, linestyle=(0, (4, 4)))
    ax.text(math.radians(40), mean - 75, f"average, {mean:.0f} Pa", color="#e8ddd4",
            fontsize=8.5, ha="center", rotation=-40)
    print(f"average over every sol: {mean:.0f} Pa")

    ax.set_rlim(0, 950)                 # from zero, so the size of the dent is honest
    ax.set_rticks([300, 600, 900])
    ax.set_yticklabels(["300 Pa", "600 Pa", "900 Pa"], color="#a89a90", fontsize=9)
    ax.set_rlabel_position(22)
    ax.set_xticks([math.radians(a) for a in (0, 90, 180, 270)])
    ax.set_xticklabels(["Ls 0°\nnorthern spring", "Ls 90°\nnorthern summer",
                        "Ls 180°\nnorthern autumn", "Ls 270°\nnorthern winter"],
                       color="#e8ddd4", fontsize=10)
    ax.tick_params(axis="x", pad=14)
    ax.grid(color="#3a302b", linewidth=0.6)
    ax.spines["polar"].set_color("#3a302b")

    note = dict(color="#e8ddd4", fontsize=9.5, ha="center", va="center")
    ax.text(math.radians(150), 450, "southern winter:\nCO₂ freezes onto\nthe south pole,\nthe air thins", **note)
    ax.text(math.radians(255), 450, "southern summer:\nthe ice turns\nback into air", **note)

    fig.text(0.5, 0.965, "Mars breathes", color="#f4ece6", fontsize=22,
             ha="center", va="top", weight="bold")
    fig.text(0.5, 0.925, "Air pressure at Gale Crater, one loop per Martian year, "
             f"{first}–{last} (2012–2026)", color="#c9bcb2", fontsize=11, ha="center", va="top")
    fig.text(0.5, 0.03, "Angle: season (solar longitude, Ls). Distance from centre: daily pressure in pascals.\n"
             "Data: NASA/JPL-Caltech, CAB (CSIC-INTA), Curiosity REMS. Gaps are sols with no reading.",
             color="#8f8279", fontsize=8.5, ha="center", va="bottom")
    legend = fig.legend(loc="lower right", bbox_to_anchor=(0.98, 0.08), frameon=False,
                        fontsize=8.5, labelcolor="#e8ddd4", handlelength=1.5)
    for line in legend.get_lines():
        line.set_linewidth(3)

    fig.subplots_adjust(top=0.83, bottom=0.12)

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=150, facecolor=fig.get_facecolor())
    print(f"saved out/{PICTURE}")


if __name__ == "__main__":
    main()
