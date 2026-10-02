# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""
Read Curiosity's weather from data/, make one picture, save it to out/.

    uv run plot.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

FILE = "curiosity-rems-weather.json"
PICTURE = "mars-breathes.png"

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"


def number(text):
    """REMS writes '--' when it has no reading. Turn the text into a number, or None."""
    try:
        return float(text)
    except ValueError:
        return None


def main():
    # The Spanish disclaimer is not valid UTF-8, so read the bytes and replace what breaks.
    soles = json.loads(DATA.read_bytes().decode("utf-8", errors="replace"))["soles"]
    print(f"{DATA.name}: {len(soles)} sols. The first one: {soles[0]}")

    sols, pressures = [], []
    for entry in soles:                          # the loop over the numbers
        pressure = number(entry["pressure"])
        if pressure is None:
            continue
        sols.append(int(entry["sol"]))
        pressures.append(pressure)
    print(f"{len(pressures)} pressures, from {min(pressures)} to {max(pressures)} Pa")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(sols, pressures)
    ax.set_xlabel("sol")
    ax.set_ylabel("pressure, Pa")
    fig.tight_layout()

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=150)
    print(f"saved out/{PICTURE}")


if __name__ == "__main__":
    main()
