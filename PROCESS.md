# Process

## Tools

I used Claude (Claude Code, an AI coding assistant, working in this folder through
the Claude app) for most of the code, the data analysis and the first drafts of the
writing. It suggested the "Mars breathes" idea and I chose it. It found the
Curiosity weather feed, checked the shape of the JSON, and wrote `fetch.py`,
`plot.py`, `animate.py`, `web.py`, `map.py` and `landers.py`. It also drafted the
README. I asked for the GIF, the web page and the map after reading
the week 3 and week 4 examples. I asked for more data when I did not trust one rover.
I wrote down my reasoning for this file myself, and Claude helped me put it into
English sentences.

## Kept

The idea of testing the result instead of just drawing it. My background is
computing mathematics, and when I saw the first picture my question was: is one
rover in one crater scientific enough to say anything about Mars? If I showed this
to someone, they could doubt it. So I asked Claude for more evidence, and I kept
two things it did with that question.

First, it took the rover's climb up Mount Sharp out of the numbers, using the
rover's height on each sol. After that, the eight years lie on top of each other:
at the same season they differ by about 6 Pa instead of 63 Pa. So the loops were
not shrinking because Mars is losing air.

Second, it added the two Viking landers, from 1976 to 1982, at two other places on
Mars. All three sites have their lowest pressure in southern winter and their
highest in southern summer. One site could be local weather. Three sites far apart,
forty years apart, agreeing on the timing is much harder to explain away. In
mathematics terms, the levelling removes a confounding variable, and the Vikings are
a replication. Three sites still do not prove how much air the whole planet loses.
What they support is a seasonal pattern that repeats at every site we have, which
fits a planet-wide cycle. I also
kept the radius of the circle starting at zero, so the picture does not exaggerate
how much air goes away.

## Rejected

The first version of the message. Claude first wrote that Mars "loses about a
quarter of its atmosphere's mass" every southern winter. I rejected this because
one weather station can only show what happens above Gale Crater, not the whole
planet. The README now says "a quarter of the air above Gale Crater". It says three
sites are still not a global average.

I also learned to check the numbers the assistant gives. It wrote the scale height
as 11.1 km and cited NASA's Mars fact sheet. The fact sheet says 11.0 km, so the
code and the README were changed to match the source.

Finally, I asked for more landers, but only seven have ever measured pressure on the
ground: Viking 1 and 2, Pathfinder, Phoenix, Curiosity, InSight, Perseverance and
Zhurong. Most of the others only cover a few months, or come as thousands of files
with gaps, so I left them out. I listed them in the README so a reader knows they
exist and why they are not here.
