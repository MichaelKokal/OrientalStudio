"""Download the free sound engine and instrument sounds (run once).

    FluidSynth     - plays instrument sounds   -> third_party/fluidsynth/
    GeneralUser GS - a free bank of 250+ sounds -> soundfonts/GeneralUser-GS.sf2
"""

import io
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
FLUIDSYNTH_URL = (
    "https://github.com/FluidSynth/fluidsynth/releases/download/"
    "v2.6.2/fluidsynth-v2.6.2-win10-x64-cpp11.zip"
)
SOUNDFONT_URL = "https://github.com/mrbumpy409/GeneralUser-GS/raw/main/GeneralUser-GS.sf2"

FLUIDSYNTH_DIR = ROOT / "third_party" / "fluidsynth"
SOUNDFONT = ROOT / "soundfonts" / "GeneralUser-GS.sf2"


def download(url):
    print(f"Downloading {url.rsplit('/', 1)[-1]} ...")
    with urllib.request.urlopen(url) as r:
        return r.read()


def main():
    if not any(FLUIDSYNTH_DIR.glob("**/libfluidsynth*.dll")):
        FLUIDSYNTH_DIR.mkdir(parents=True, exist_ok=True)
        zipfile.ZipFile(io.BytesIO(download(FLUIDSYNTH_URL))).extractall(FLUIDSYNTH_DIR)
    else:
        print("FluidSynth already downloaded.")

    if not SOUNDFONT.exists():
        SOUNDFONT.parent.mkdir(exist_ok=True)
        SOUNDFONT.write_bytes(download(SOUNDFONT_URL))
    else:
        print("Sounds already downloaded.")

    print("Done.")


if __name__ == "__main__":
    main()
