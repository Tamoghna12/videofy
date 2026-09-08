#!/usr/bin/env python3
"""
download_assets.py - Download and generate audio & visual assets for video editing.
Populates:
- bg_music/: Classical & cinematic masterpieces (Debussy, Beethoven, Vivaldi, Bach, Satie)
- assets/ambient_sfx/: Environmental audio (rain, church bells, train, wind)
- assets/overlays/: 1080x1920 35mm film grain & anamorphic light leak loops
"""

import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MUSIC_DIR = BASE_DIR / "bg_music"
SFX_DIR = BASE_DIR / "assets/ambient_sfx"
OVERLAYS_DIR = BASE_DIR / "assets/overlays"

MUSIC_DIR.mkdir(exist_ok=True)
SFX_DIR.mkdir(parents=True, exist_ok=True)
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Background Music Library (Direct high-fidelity recordings)
MUSIC_TRACKS = [
    {
        "filename": "debussy_clair_de_lune.mp3",
        "url": "https://archive.org/download/pascal-roge-debussy-clair-de-lune/01%20-%20Clair%20de%20lune%20%28Suite%20bergamasque%29.mp3",
        "title": "Debussy - Clair de Lune (Pascal Rogé, Piano)"
    },
    {
        "filename": "debussy_arabesque_no1.mp3",
        "url": "https://archive.org/download/pascal-roge-debussy-clair-de-lune/05%20-%20Arabesque%20No.1%20-%20Andante%20con%20moto.mp3",
        "title": "Debussy - Arabesque No. 1 (Pascal Rogé, Piano)"
    },
    {
        "filename": "debussy_reverie.mp3",
        "url": "https://archive.org/download/pascal-roge-debussy-clair-de-lune/11%20-%20Reverie.mp3",
        "title": "Debussy - Rêverie (Pascal Rogé, Piano)"
    },
    {
        "filename": "beethoven_pathetique_adagio.mp3",
        "url": "https://archive.org/download/jamendo-175593/09-1532973-OnClassical-alessandro_taverna_beethoven_sonatas_op._27_13_variations_op._35_09_sonata_no._8_in_c_minor_op._13_ii._adagio_cantabile.mp3",
        "title": "Beethoven - Sonata No. 8 'Pathétique', II. Adagio cantabile"
    },
    {
        "filename": "vivaldi_winter_largo.mp3",
        "url": "https://archive.org/download/jamendo-508706/01-1999731-Abydos%20Music-Vivaldi%20-%20Winter%20Largo%20-%20The%20Four%20Seasons.mp3",
        "title": "Vivaldi - The Four Seasons: Winter (Largo)"
    },
    {
        "filename": "bach_cello_suite_no1_prelude.mp3",
        "url": "https://archive.org/download/Bach-siloti-PreludeFromCelloSuiteNo.1Bwv1007felipeSarro/15.mp3",
        "title": "Bach - Cello Suite No. 1 in G Major: Prelude"
    },
    {
        "filename": "satie_gymnopedie_no1.mp3",
        "url": "https://archive.org/download/GymnopedieNo.1MachineMelancholy/Gymnopedie%20No.%201%20%28Machine%20Melancholy%29.mp3",
        "title": "Erik Satie - Gymnopédie No. 1"
    }
]

# 2. Ambient Sound Effects (Commons field recordings)
SFX_TRACKS = [
    {
        "filename": "gentle_rain_ambience.mp3",
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Sound_of_rain.ogg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
        "is_ogg": True
    },
    {
        "filename": "train_rolling_ambience.mp3",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/d1/Train_sounds_from_Rome_01.ogg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
        "is_ogg": True
    },
    {
        "filename": "church_bells_cathedral.mp3",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Samariter_Church_Bell_I_%28Es%29.ogg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
        "is_ogg": True
    },
    {
        "filename": "gentle_wind_breeze.mp3",
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/90/Breeze_birds_and_geese.ogg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
        "is_ogg": True
    }
]


def download_file(url, target_path):
    """Download a file with user agent header."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req) as resp, open(target_path, "wb") as f:
        while chunk := resp.read(65536):
            f.write(chunk)


def convert_to_mp3(src_path, dst_path):
    """Convert audio to high quality mp3 using ffmpeg."""
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src_path), "-b:a", "192k", str(dst_path)]
    subprocess.run(cmd, check=True)
    src_path.unlink(missing_ok=True)


def generate_film_grain_overlay(out_path, width=1080, height=1920, duration=10):
    """Generate a clean 35mm film grain video loop (portrait 9:16)."""
    print(f"Generating authentic 35mm film grain overlay ({width}x{height}, {duration}s)...")
    # Generates organic 35mm grain pattern with gentle temporal flicker
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"color=c=gray:s={width}x{height}:d={duration}:r=24",
        "-filter_complex",
        "noise=alls=18:allf=t+u,eq=contrast=1.15:brightness=-0.02,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)


def generate_light_leak_overlay(out_path, width=1080, height=1920, duration=8):
    """Generate an organic warm anamorphic light leak flare loop."""
    print(f"Generating cinematic light leak overlay ({width}x{height}, {duration}s)...")
    # Generates breathing warm amber flare drifting across the frame
    expr = (
        "color=c=black:s=1080x1920:d=8:r=24[bg];"
        "nullsrc=s=1080x1920:d=8:r=24,"
        "geq=r='255*exp(-((X-w*(0.5+0.3*sin(2*PI*t/8)))^2 + (Y-h*(0.3+0.2*cos(2*PI*t/8)))^2)/(2*(w*0.35)^2))':"
        "g='160*exp(-((X-w*(0.5+0.3*sin(2*PI*t/8)))^2 + (Y-h*(0.3+0.2*cos(2*PI*t/8)))^2)/(2*(w*0.35)^2))':"
        "b='40*exp(-((X-w*(0.5+0.3*sin(2*PI*t/8)))^2 + (Y-h*(0.3+0.2*cos(2*PI*t/8)))^2)/(2*(w*0.35)^2))'[flare];"
        "[bg][flare]blend=all_mode=addition,boxblur=20:2,format=yuv420p"
    )
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-filter_complex", expr,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-t", f"{duration}",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)


def main():
    print("=== Downloading Background Music Masters ===")
    for item in MUSIC_TRACKS:
        target = MUSIC_DIR / item["filename"]
        if target.exists():
            print(f"  [OK] {item['filename']} already exists.")
            continue
        print(f"  Downloading {item['title']}...")
        try:
            download_file(item["url"], target)
            print(f"    -> Saved {item['filename']} ({target.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"    -> Error downloading {item['filename']}: {e}")

    print("\n=== Downloading Ambient Foley & Sound Effects ===")
    for item in SFX_TRACKS:
        target = SFX_DIR / item["filename"]
        if target.exists():
            print(f"  [OK] {item['filename']} already exists.")
            continue
        print(f"  Downloading {item['filename']}...")
        tmp_target = SFX_DIR / f"_tmp_{item['filename']}.ogg" if item.get("is_ogg") else target
        try:
            download_file(item["url"], tmp_target)
            if item.get("is_ogg"):
                convert_to_mp3(tmp_target, target)
            print(f"    -> Saved {item['filename']} ({target.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"    -> Error downloading {item['filename']}: {e}")

    print("\n=== Generating Cinematic Visual Overlays ===")
    grain_path = OVERLAYS_DIR / "film_grain_35mm_portrait.mp4"
    if not grain_path.exists():
        generate_film_grain_overlay(grain_path)
        print(f"  -> Saved {grain_path.name}")
    else:
        print(f"  [OK] {grain_path.name} already exists.")

    leak_path = OVERLAYS_DIR / "light_leak_anamorphic_portrait.mp4"
    if not leak_path.exists():
        generate_light_leak_overlay(leak_path)
        print(f"  -> Saved {leak_path.name}")
    else:
        print(f"  [OK] {leak_path.name} already exists.")

    print("\n=================================================")
    print("Asset library successfully expanded!")
    print(f"Music Folder:    {MUSIC_DIR}")
    print(f"SFX Folder:      {SFX_DIR}")
    print(f"Overlays Folder: {OVERLAYS_DIR}")
    print("=================================================")


if __name__ == "__main__":
    main()
