# /// script
# requires-python = ">=3.10"
# dependencies = ["folium", "matplotlib"]
# ///

"""
Where the rover was while it measured: Curiosity's drive up Mount Sharp on an
open-source map of Mars, coloured by Mars year like the loops.

    uv run map.py        # writes site/map.html; open it in a browser

Why it matters for the picture: the loops in plot.py shrink a little every year.
Mars is not losing its air. The weather station is climbing a mountain, and air
thins with height. Click a year's stretch of road for how high the rover was that
year, what pressure it measured on average, and what height alone would predict.
"""

import json
import math
from pathlib import Path

import folium

from plot import load, mars_years

SCALE_HEIGHT = 11_000      # metres: on Mars the air thins by a factor e every ~11 km of climb
TILES = ("https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/"
         "opm-mars-basemap-v0-2/all/{z}/{x}/{y}.png")
CREDIT = ("map: <a href='https://www.openplanetary.org/opm'>OpenPlanetaryMap</a> (CC BY) · "
          "route: NASA/JPL-Caltech MMGIS · weather: NASA/JPL-Caltech, CAB (CSIC-INTA), REMS")
# YlOrRd from light to dark, one colour per Mars year, the same as web.py
COLOURS = ["#fed976", "#feb24c", "#fd8d3c", "#fc6c33", "#f03b20", "#e31a1c", "#bd0026", "#800026"]

HERE = Path(__file__).parent
ROUTE = HERE / "data" / "curiosity-waypoints.json"
SITE = HERE / "site"


def expected(pressure, climb):
    """The pressure a barometer reading `pressure` would show after climbing `climb`
    metres, if nothing changed but the height: p = p0 * e^(-climb / H)."""
    return pressure * math.exp(-climb / SCALE_HEIGHT)


def main():
    years = mars_years(load())
    starts = {year: readings[0][0] for year, readings in years.items()}   # first sol of each year
    stops = json.loads(ROUTE.read_text(encoding="utf-8"))["features"]
    print(f"{ROUTE.name}: {len(stops)} waypoints, sol {stops[0]['properties']['sol']} "
          f"to {stops[-1]['properties']['sol']}")

    # Put every waypoint into the Mars year its sol falls in.
    route = {year: [] for year in years}
    for stop in stops:                                   # the loop over the numbers
        where = stop["properties"]
        year = max((y for y, first in starts.items() if first <= where["sol"]), default=min(years))
        route[year].append((where["lat"], where["lon"], where["elev_geoid"]))

    # The first full year is the baseline the others are compared against.
    base_year = min(years) + 1
    base_height = sum(h for _, _, h in route[base_year]) / len(route[base_year])
    base_pressure = sum(p for _, _, p in years[base_year]) / len(years[base_year])

    everywhere = [(lat, lon) for points in route.values() for lat, lon, _ in points]
    world = folium.Map(location=everywhere[-1], zoom_start=11, tiles=None, max_zoom=16,
                       control_scale=False, prefer_canvas=True)
    folium.TileLayer(TILES, attr=CREDIT, name="OpenPlanetaryMap Mars",
                     max_native_zoom=9, max_zoom=16).add_to(world)

    for i, (year, points) in enumerate(route.items()):
        if not points:
            continue
        height = sum(h for _, _, h in points) / len(points)
        pressure = sum(p for _, _, p in years[year]) / len(years[year])
        climb = height - base_height
        line = (f"<b>Mars year {year}</b><br>"
                f"{len(points)} stops, {points[0][2]:,.0f} to {points[-1][2]:,.0f} m elevation<br>"
                f"average pressure measured: <b>{pressure:.0f} Pa</b>")
        if year > base_year:
            line += (f"<br>{climb:+.0f} m since Mars year {base_year}: height alone predicts "
                     f"{expected(base_pressure, climb):.0f} Pa")
        if year in (min(years), max(years)):
            line += "<br><i>(a part year: its average leans on the seasons it has)</i>"
        print(line.replace("<br>", " | ").replace("<b>", "").replace("</b>", "")
                  .replace("<i>", "").replace("</i>", ""))
        folium.PolyLine([(lat, lon) for lat, lon, _ in points], color=COLOURS[i % len(COLOURS)],
                        weight=5, opacity=0.95, tooltip=f"Mars year {year}",
                        popup=folium.Popup(line, max_width=320)).add_to(world)

    landing, latest = everywhere[0], everywhere[-1]
    folium.CircleMarker(landing, radius=7, color="#14100e", fill=True, fill_color="#fed976",
                        fill_opacity=1, tooltip="Landing site, sol 0, August 2012").add_to(world)
    folium.CircleMarker(latest, radius=7, color="#14100e", fill=True, fill_color="#800026",
                        fill_opacity=1,
                        tooltip=f"Latest stop, sol {stops[-1]['properties']['sol']}").add_to(world)
    world.fit_bounds([[min(a for a, _ in everywhere), min(b for _, b in everywhere)],
                      [max(a for a, _ in everywhere), max(b for _, b in everywhere)]])

    note = (
        "<div style='position:fixed;top:12px;left:56px;z-index:9999;max-width:340px;"
        "background:#14100eee;color:#e8ddd4;padding:12px 14px;border-radius:6px;"
        "font:13px/1.45 system-ui,sans-serif'>"
        "<b style='font-size:16px'>Why the loops shrink</b><br>"
        f"Curiosity has driven up Mount Sharp, from {route[min(years)][0][2]:,.0f} m to "
        f"{route[max(years)][-1][2]:,.0f} m. Air thins with height, so its "
        "barometer reads lower each year. Click a year's stretch of road for the numbers; "
        "zoom out to see Gale Crater and the mountain. "
        "<a href='index.html' style='color:#fd8d3c'>← back to the loops</a></div>"
    )
    world.get_root().html.add_child(folium.Element(note))
    world.get_root().header.add_child(folium.Element(
        "<title>Mars breathes: where the rover was</title>"))

    SITE.mkdir(exist_ok=True)
    world.save(SITE / "map.html")
    print(f"wrote site/map.html ({(SITE / 'map.html').stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
