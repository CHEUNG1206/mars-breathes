# Process

<!-- DRAFT. Ivan: the facts below are what happened in the Claude Code session that
built this repo. The "Kept" and "Rejected" sections need to be in your own words,
about choices you actually agree with or would make differently. Delete this comment
and every [IVAN: ...] note before you submit. -->

## Tools

I used Claude (Claude Code, an AI coding assistant) to find the source, check the
shape of the JSON, write `fetch.py` and `plot.py`, and draft this README. I chose the
phenomenon and the idea of drawing each Martian year as a loop on a circle.
[IVAN: add anything else you used, and what you changed by hand.]

## Kept

The polar chart with the radius starting from zero. The first polar version started the
radius at 600 Pa, which made the dent in southern winter look dramatic, almost like the
air disappeared. Starting from zero makes the loops look like a slightly squashed egg,
which is less exciting but true: a quarter of the air, not all of it. The dashed
average ring was added so the bulge and the dent are still easy to see.
[IVAN: say in your own words why you kept this, or pick a different thing.]

## Rejected

[IVAN: one thing the assistant suggested that you threw away, and why it was wrong.
Candidates from the session: the first version's annotations were placed with
coordinates that put them on top of the legend in the middle of the circle; the
assistant's first idea for the message ("the atmosphere loses a quarter of its mass")
was stronger than what one weather station at one spot can show, so the README says
"a quarter of the air above Gale Crater" instead; the loops shrinking each year could
be misread as Mars losing air, when it is mostly the rover driving uphill.
More from the GIF/web/map round: the web script could not be called site.py because
that name clashes with a module built into Python, so it is web.py; Plotly's web page
played its animation by itself on load and showed only the first year until that was
switched off; OpenStreetMap only covers Earth, so the map uses OpenPlanetaryMap, whose
Mars tiles go blurry past zoom 9.
From the "more data" round: the assistant first wrote the scale height as 11.1 km
and cited NASA's Mars fact sheet, but the fact sheet says 11.0 km, so the code and
README were corrected to match the source.]
