#!/usr/bin/env python3
"""
create_bradford_landscape_reels.py - Render Bradford Reels in 16:9 Landscape with
Cinematic Black Bars, Grounded Storytelling Voiceover, and Kinetic Gold Highlighted ASS Subtitles.
"""

import os
import sys
from pathlib import Path

WORKSPACE_ROOT = Path("/home/tamoghna/Documents/Video_editing")
sys.path.insert(0, str(WORKSPACE_ROOT))

from video_templates.presets.cinematic_landscape import render as render_cinematic_landscape

BRADFORD_REELS = [
    {
        "id": "reel1",
        "name": "Bradford Reel 1: The Journey Begins",
        "footage": "raw_footage/bradford",
        "output": "edit/cinematic_16x9/bradford_reel1_the_journey.mp4",
        "qc": "edit/verify/qc_sheet_bradford_reel1.png",
        "title": "BRADFORD • THE JOURNEY BEGINS",
        "subtitle": "CROSSING YORKSHIRE BY TRAIN • 1850 ARCHES",
        "outro_title": "YORKSHIRE TRAVELS",
        "outro_subtitle": "Save for your northern railway journey 📍",
        "voiceover": "Leaving the open Yorkshire fields behind... as the train cuts quietly through the morning light. | Stepping into Bradford. Beneath towering Victorian railway arches that have stood since eighteen fifty. | You walk past honey-colored stone and quiet streets... and let the rhythm of the city take over.",
        "music": "experience_einaudi.mp3",
        "sfx": "train_rolling_ambience.mp3",
        "lut": "CINECOLOR_GOLDEN_HOUR.CUBE",
        "grade": "clean_landscape",
        "shots": [
            ("DJI_20260531141209_0261_D.MP4", 3.0, 7.0, "Travelling through Yorkshire countryside"),
            ("DJI_20260723171555_0262_D.MP4", 1.5, 5.0, "Arriving at Bradford Interchange"),
            ("DJI_20260723171615_0263_D.MP4", 2.0, 5.5, "Stepping onto the platform"),
            ("DJI_20260723171641_0264_D.MP4", 1.0, 4.5, "Bradford city center welcome"),
            ("DJI_20260723171744_0265_D.MP4", 2.0, 6.0, "Stepping into the historic city"),
            ("DJI_20260723171945_0266_D.MP4", 2.0, 6.5, "Victorian Railway Arches • Built 1850"),
            ("DJI_20260723173540_0270_D.MP4", 4.0, 8.5, "Exploring historic Little Germany"),
            ("DJI_20260723174010_0271_D.MP4", 2.0, 6.0, "Timeless Yorkshire stone architecture"),
            ("DJI_20260723180816_0273_D.MP4", 1.0, 4.5, "Checking into our room"),
            ("DJI_20260723183212_0274_D.MP4", 1.0, 4.5, "Journey complete • Relaxing evening ahead"),
        ]
    },
    {
        "id": "reel2",
        "name": "Bradford Reel 2: Solo Dining & Evening Reset",
        "footage": "raw_footage/bradford",
        "output": "edit/cinematic_16x9/bradford_reel2_solo_dining.mp4",
        "qc": "edit/verify/qc_sheet_bradford_reel2.png",
        "title": "SOLO DINING & EVENING RESET",
        "subtitle": "WINDOW VIEWS & SLOW TRAVEL • BRADFORD",
        "outro_title": "SLOW TRAVEL JOURNAL",
        "outro_subtitle": "Savoring every quiet moment 📍",
        "voiceover": "After hours on the move, there is nothing quite like a quiet window and a moment to breathe. | A warm plate, crisp greens, and the slow, comforting unwinding of a long travel day. | No rush, no itinerary... just the simple comfort of watching dusk settle over the city.",
        "music": "debussy_clair_de_lune.mp3",
        "sfx": "gentle_rain_ambience.mp3",
        "lut": None,
        "grade": "culinary_warm",
        "shots": [
            ("DJI_20260723195704_0275_D.MP4", 1.5, 5.5, "Golden afternoon light by the window"),
            ("DJI_20260723200841_0277_D.MP4", 2.0, 5.5, "Taking time to pause and slow down"),
            ("DJI_20260723202023_0278_D.MP4", 508.0, 513.0, "Fresh salad & grilled dinner is served"),
            ("DJI_20260723202023_0278_D.MP4", 630.0, 634.5, "The best feeling after a day of travel"),
            ("DJI_20260723202023_0278_D.MP4", 750.0, 755.0, "Quiet comfort & delicious food"),
            ("DJI_20260723202023_0278_D.MP4", 1110.0, 1114.5, "A cold refreshing drink to finish"),
            ("DJI_20260723202023_0278_D.MP4", 1228.0, 1233.0, "Watching dusk settle over the city"),
            ("DJI_20260723214931_0284_D.MP4", 1.5, 5.5, "Goodnight Bradford"),
        ]
    },
    {
        "id": "reel3",
        "name": "Bradford Reel 3: City Hall & Twilight Glow",
        "footage": "raw_footage/bradford",
        "output": "edit/cinematic_16x9/bradford_reel3_city_hall_twilight.mp4",
        "qc": "edit/verify/qc_sheet_bradford_reel3.png",
        "title": "BRADFORD CITY HALL",
        "subtitle": "A VICTORIAN GOTHIC MASTERPIECE • 1873",
        "outro_title": "DISCOVER YORKSHIRE",
        "outro_subtitle": "Bradford • UK City of Culture 📍",
        "voiceover": "As evening deepens, the sandstone heart of Bradford begins to glow in twilight. | Walking through Centenary Square, beneath the grand Venetian Gothic arches of City Hall. | Two hundred and twenty feet above, the clock tower chimes into the cool Yorkshire night.",
        "music": "can_you_hear_the_music.mp3",
        "sfx": "church_bells_cathedral.mp3",
        "lut": "Rec709 Kodak 2383 D65.cube",
        "grade": "clean_landscape",
        "shots": [
            ("DJI_20260723174010_0271_D.MP4", 3.0, 7.0, "Historic Victorian bank architecture"),
            ("DJI_20260723204601_0280_D.MP4", 12.0, 16.5, "Approaching Centenary Square at dusk"),
            ("DJI_20260723205102_0281_D.MP4", 5.0, 9.5, "Strolling through City Park promenade"),
            ("DJI_20260723205159_0282_D.MP4", 4.0, 8.5, "The grand civic heart of Bradford"),
            ("DJI_20260723205446_0283_D.MP4", 0.5, 6.0, "The Iconic 220-ft Clock Tower"),
            ("DJI_20260723205446_0283_D.MP4", 18.0, 23.0, "Venetian Gothic Elegance • Built 1873"),
            ("DJI_20260723205446_0283_D.MP4", 30.0, 34.5, "Grade I Listed Heritage in golden light"),
            ("DJI_20260723204601_0280_D.MP4", 28.0, 32.5, "Twilight magic falling over Yorkshire"),
        ]
    }
]


def update_backward_compatible_links(out_file: Path):
    """Ensure symlinks in edit/ and edit/reels_9x16/ point to the new 16x9 deliverable."""
    edit_dir = WORKSPACE_ROOT / "edit"
    reels_dir = edit_dir / "reels_9x16"
    
    # In edit/
    sym1 = edit_dir / out_file.name
    if sym1.is_symlink() or sym1.exists():
        sym1.unlink()
    sym1.symlink_to(f"cinematic_16x9/{out_file.name}")
    
    # In edit/reels_9x16/
    sym2 = reels_dir / out_file.name
    if sym2.is_symlink() or sym2.exists():
        sym2.unlink()
    sym2.symlink_to(f"../cinematic_16x9/{out_file.name}")


def main():
    print("=" * 85)
    print("🎬 RENDERING BRADFORD REELS: 16:9 LANDSCAPE WITH CINEMATIC BLACK BARS & VOICEOVER")
    print("=" * 85)
    
    for idx, r in enumerate(BRADFORD_REELS, 1):
        print(f"\n[{idx}/{len(BRADFORD_REELS)}] Rendering {r['name']}...")
        out_path = WORKSPACE_ROOT / r["output"]
        qc_path = WORKSPACE_ROOT / r["qc"]
        
        render_cinematic_landscape(
            footage_dir=WORKSPACE_ROOT / r["footage"],
            output_file=out_path,
            qc_file=qc_path,
            title=r["title"],
            subtitle=r["subtitle"],
            outro_title=r["outro_title"],
            outro_subtitle=r["outro_subtitle"],
            lut_name=r["lut"],
            grade_preset=r["grade"],
            music_track=r["music"],
            sfx_track=r["sfx"],
            voiceover_text=r["voiceover"],
            voiceover_speed=0.92,
            black_bars=True,
            shots=r["shots"],
            accel="auto"
        )
        
        update_backward_compatible_links(out_path)
        print(f"  ✅ Rendered: {out_path.name}")
        print(f"  ✅ Contact Sheet: {qc_path.name}")

    print("\n" + "=" * 85)
    print("🎉 ALL 3 BRADFORD REELS SUCCESSFULLY RENDERED IN 16:9 LANDSCAPE WITH BLACK BARS!")
    print("=" * 85)


if __name__ == "__main__":
    main()
