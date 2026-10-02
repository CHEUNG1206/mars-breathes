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

import bisect
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt

FILE = "curiosity-rems-weather.json"
PICTURE = "mars-breathes.png"

FIRST_MARS_YEAR = 31      # Curiosity landed at Ls 150 of Mars Year 31 (August 2012)
GAP = 10                  # more sols than this without a reading breaks the line
SCALE_HEIGHT = 11_000     # metres: Mars's air thins by a factor e every 11 km up (NASA Mars fact sheet)

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
ROUTE = HERE / "data" / "curiosity-waypoints.json"
OUT = HERE / "out"

PAPER = "#14100e"
INK = "#e8ddd4"
FAINT = "#3a302b"


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


def heights(path=ROUTE):
    """Where the rover's barometer was: (sol, elevation in metres) for every waypoint,
    in order of sol."""
    stops = json.loads(path.read_text(encoding="utf-8"))["features"]
    return sorted((stop["properties"]["sol"], stop["properties"]["elev_geoid"]) for stop in stops)


def height_on(sol, route):
    """The rover's elevation on any sol: between two waypoints, a straight line from
    one to the next; before the first or after the last, the nearest one."""
    sols = [s for s, _ in route]
    i = bisect.bisect_right(sols, sol)
    if i == 0:
        return route[0][1]
    if i == len(route):
        return route[-1][1]
    (s0, z0), (s1, z1) = route[i - 1], route[i]
    return z0 if s1 == s0 else z0 + (z1 - z0) * (sol - s0) / (s1 - s0)


def level(years, route):
    """The same years, with every pressure moved to the height of the landing site.
    Air thins by a factor e for every SCALE_HEIGHT metres of climb, so a reading
    taken z - z0 metres higher is multiplied back up by e^((z - z0) / H)."""
    z0 = route[0][1]
    return {year: [(sol, ls, pressure * math.exp((height_on(sol, route) - z0) / SCALE_HEIGHT))
                   for sol, ls, pressure in readings]
            for year, readings in years.items()}


def draw(ax, years, heading, mean):
    """One panel: every Mars year as a loop, the average as a dashed ring."""
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)           # clockwise, like a clock: the year turns
    ax.set_facecolor(PAPER)
    colours = plt.get_cmap("YlOrRd")
    first, last = min(years), max(years)
    for year, readings in years.items():
        angles, radii = with_breaks(readings)
        shade = 0.25 + 0.75 * (year - first) / (last - first)
        ax.plot(angles, radii, color=colours(shade), linewidth=1.0, label=f"Mars year {year}")

    ring = [math.radians(a) for a in range(361)]
    ax.plot(ring, [mean] * len(ring), color=INK, linewidth=0.8, linestyle=(0, (4, 4)))
    ax.text(math.radians(40), mean - 75, f"average, {mean:.0f} Pa", color=INK,
            fontsize=8.5, ha="center", rotation=-40)

    ax.set_rlim(0, 950)                 # from zero, so the size of the dent is honest
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
    ax.set_title(heading, color="#f4ece6", fontsize=13, pad=48, linespacing=1.6)


def average(years):
    every = [p for readings in years.values() for _, _, p in readings]
    return sum(every) / len(every)


def main():
    soles = load()
    print(f"{DATA.name}: {len(soles)} sols")

    years = mars_years(soles)
    route = heights()
    flat = level(years, route)
    for year, readings in years.items():
        pressures = [p for _, _, p in readings]
        levelled = [p for _, _, p in flat[year]]
        print(f"Mars year {year}: {len(readings):4d} sols with pressure, "
              f"Ls {readings[0][1]:3.0f} to {readings[-1][1]:3.0f}, "
              f"{min(pressures):.0f} to {max(pressures):.0f} Pa measured, "
              f"{min(levelled):.0f} to {max(levelled):.0f} Pa levelled")
    print(f"climb from {route[0][1]:.0f} m to {route[-1][1]:.0f} m; "
          f"average {average(years):.0f} Pa measured, {average(flat):.0f} Pa levelled")

    fig = plt.figure(figsize=(20, 10.6), facecolor=PAPER)
    left = fig.add_subplot(1, 2, 1, projection="polar")
    right = fig.add_subplot(1, 2, 2, projection="polar")
    draw(left, years, "As measured\n"
         "the loops shrink as the rover climbs Mount Sharp", average(years))
    draw(right, flat, f"As if the rover had stayed at the landing site ({route[0][1]:,.0f} m)\n"
         "the years land on top of each other", average(flat))

    note = dict(color=INK, fontsize=9.5, ha="center", va="center")
    for ax in (left, right):
        ax.text(math.radians(150), 450, "southern winter:\nCO₂ freezes onto\nthe south pole,\nthe air thins", **note)
        ax.text(math.radians(255), 450, "southern summer:\nthe ice turns\nback into air", **note)

    first, last = min(years), max(years)
    fig.text(0.5, 0.965, "Mars breathes", color="#f4ece6", fontsize=24,
             ha="center", va="top", weight="bold")
    fig.text(0.5, 0.92, "Air pressure at Gale Crater, one loop per Martian year, "
             f"{first}–{last} (2012–2026)", color="#c9bcb2", fontsize=12, ha="center", va="top")
    fig.text(0.5, 0.025, "Angle: season (solar longitude, Ls). Distance from centre: daily pressure in pascals. "
             "Gaps are sols with no reading.\nRight: each reading scaled to the landing-site height with "
             f"p × e^(climb / {SCALE_HEIGHT / 1000:.1f} km), using the rover's elevation on that sol.\n"
             "Data: NASA/JPL-Caltech, CAB (CSIC-INTA), Curiosity REMS; route: NASA/JPL-Caltech MMGIS.",
             color="#8f8279", fontsize=9, ha="center", va="bottom", linespacing=1.6)
    handles, labels = left.get_legend_handles_labels()
    legend = fig.legend(handles, labels, loc="center", bbox_to_anchor=(0.5, 0.5), frameon=False,
                        fontsize=9, labelcolor=INK, handlelength=1.5)
    for line in legend.get_lines():
        line.set_linewidth(3)

    fig.subplots_adjust(top=0.78, bottom=0.13, left=0.06, right=0.94, wspace=0.62)

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=150, facecolor=fig.get_facecolor())
    print(f"saved out/{PICTURE}")


if __name__ == "__main__":
    main()
