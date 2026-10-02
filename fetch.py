# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

"""
Fetch Curiosity's daily weather from Gale Crater once, save the raw reply to data/,
and never fetch again.

    uv run fetch.py

The feed is the one behind NASA's "Mars Weather" page: one entry per sol (a Martian
day) since the rover landed in August 2012, measured by REMS, the rover's weather
station. No key needed.
"""

from pathlib import Path

import requests

URL = "https://mars.nasa.gov/rss/api/?feed=weather&category=msl&feedtype=json"
FILE = "curiosity-rems-weather.json"

HERE = Path(__file__).parent
DATA = HERE / "data"


def fetch(url, path):
    """Ask for the file once. If it is already in data/, do nothing."""
    if path.exists():
        print(f"data/{path.name} is already here ({path.stat().st_size // 1024} KB). "
              "Delete it to fetch again.")
        return path
    DATA.mkdir(exist_ok=True)
    print(f"asking {url}")
    reply = requests.get(url, timeout=60, headers={"User-Agent": "SD5913 PolyU student"})
    reply.raise_for_status()
    path.write_bytes(reply.content)      # the raw reply, byte for byte
    print(f"saved data/{path.name} ({path.stat().st_size // 1024} KB). Now: git add data")
    return path


if __name__ == "__main__":
    fetch(URL, DATA / FILE)
