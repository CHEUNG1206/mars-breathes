# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib", "plotly"]
# ///

"""
The Mars breathes loops as a web page you can hover, toggle and play.

    uv run web.py        # writes site/index.html; open it in a browser

No window opens. Python writes one HTML file and the browser does the drawing:
Plotly turns the same years plot.py draws into JavaScript. Hover a point for its
sol, date and temperatures; click a year in the legend to hide it; press Play to
watch the years arrive one at a time. GitHub Actions runs this same command on
every push and publishes site/ (see .github/workflows/pages.yml).
"""

from pathlib import Path

import plotly.graph_objects as go

from plot import load, mars_years, number

GAP = 10                   # same rule as plot.py: more sols than this without a reading breaks the line
PAPER = "#14100e"
INK = "#e8ddd4"
FAINT = "#3a302b"
# YlOrRd from light to dark, one colour per Mars year, like the PNG
COLOURS = ["#fed976", "#feb24c", "#fd8d3c", "#fc6c33", "#f03b20", "#e31a1c", "#bd0026", "#800026"]

HERE = Path(__file__).parent
SITE = HERE / "site"


def trace(year, readings, details, colour):
    """One Mars year as one Plotly line, with None where the rover had no reading,
    and a hover label built from that sol's entry in the file."""
    angles, radii, labels = [], [], []
    for i, (sol, ls, pressure) in enumerate(readings):
        if i and sol - readings[i - 1][0] > GAP:
            angles.append(None)
            radii.append(None)
            labels.append(None)
        entry = details[sol]
        low, high = number(entry["min_temp"]), number(entry["max_temp"])
        temps = f"{low:.0f} to {high:.0f} °C" if low is not None and high is not None else "no temperature"
        angles.append(ls)
        radii.append(pressure)
        labels.append(f"Mars year {year} · sol {sol}<br>{entry['terrestrial_date']} · Ls {ls:.0f}°"
                      f"<br><b>{pressure:.0f} Pa</b> · {temps}")
    return go.Scatterpolar(theta=angles, r=radii, mode="lines", name=f"Mars year {year}",
                           line=dict(color=colour, width=1.5), text=labels,
                           hovertemplate="%{text}<extra></extra>", connectgaps=False)


def main():
    soles = load()
    details = {int(entry["sol"]): entry for entry in soles}
    years = mars_years(soles)
    traces = [trace(year, readings, details, COLOURS[i % len(COLOURS)])
              for i, (year, readings) in enumerate(years.items())]
    every = [p for readings in years.values() for _, _, p in readings]
    mean = sum(every) / len(every)
    ring = go.Scatterpolar(theta=list(range(361)), r=[mean] * 361, mode="lines",
                           name=f"average, {mean:.0f} Pa", hoverinfo="skip",
                           line=dict(color=INK, width=1, dash="dash"))

    # Play: frame k shows the first k years; the rest are drawn as empty lines.
    blank = [go.Scatterpolar(theta=[], r=[]) for _ in traces]
    frames = [go.Frame(name=str(year), data=traces[:k + 1] + blank[k + 1:])
              for k, year in enumerate(years)]

    fig = go.Figure(data=traces + [ring], frames=frames)
    fig.update_layout(
        title=dict(text="<b>Mars breathes</b><br><sup>Air pressure at Gale Crater, "
                        "one loop per Martian year, 2012–2026</sup>", x=0.5, font=dict(size=24)),
        paper_bgcolor=PAPER, font=dict(color=INK, family="system-ui, sans-serif"),
        polar=dict(
            bgcolor=PAPER,
            angularaxis=dict(rotation=90, direction="clockwise", gridcolor=FAINT, linecolor=FAINT,
                             tickmode="array", tickvals=[0, 90, 180, 270],
                             ticktext=["Ls 0° northern spring", "Ls 90° northern summer",
                                       "Ls 180° northern autumn", "Ls 270° northern winter"]),
            radialaxis=dict(range=[0, 950], tickvals=[300, 600, 900], ticktext=["300 Pa", "600 Pa", "900 Pa"],
                            angle=22, gridcolor=FAINT, linecolor=FAINT, tickfont=dict(size=10)),
        ),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.07, font=dict(size=12)),
        margin=dict(t=110, b=150, l=60, r=60), height=860,
        updatemenus=[dict(type="buttons", x=0.0, y=1.02, xanchor="left", showactive=False,
                          bgcolor=FAINT, font=dict(color=INK),
                          buttons=[dict(label="▶ Play the years", method="animate",
                                        args=[None, dict(frame=dict(duration=900, redraw=True),
                                                         transition=dict(duration=0),
                                                         fromcurrent=False)])])],
        annotations=[dict(text="Angle: season (solar longitude, Ls). Distance from centre: daily "
                               "pressure in pascals. Gaps are sols with no reading.<br>"
                               "Data: NASA/JPL-Caltech, CAB (CSIC-INTA), Curiosity REMS · "
                               "<a href='https://mars.nasa.gov/msl/mission/weather/' "
                               "style='color:#e8ddd4'>mars.nasa.gov</a>",
                          x=0.5, y=-0.2, xref="paper", yref="paper", showarrow=False,
                          font=dict(size=11, color="#8f8279"))],
    )

    SITE.mkdir(exist_ok=True)
    fig.write_html(SITE / "index.html", include_plotlyjs="cdn", full_html=True, auto_play=False,
                   config={"displaylogo": False})
    print(f"wrote site/index.html ({(SITE / 'index.html').stat().st_size // 1024} KB) "
          f"from {len(every)} readings in {len(years)} years")


if __name__ == "__main__":
    main()
