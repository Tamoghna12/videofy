#!/usr/bin/env python3
"""
create_lboro_landscape_film.py - Render Loughborough University Cinematic 16:9 Landscape Film (99.5s).
Features:
- 16:9 Widescreen (1920x1080) with 2.34:1 Anamorphic Black Letterbox Bars
- Dedicated Top Bar: Location branding + dynamic scene tags synchronized to footage
- Dedicated Bottom Bar: Kinetic radiant gold highlighted ASS subtitles
- Unhurried Local AI Voiceover cloned with QwenTTSService on cuda:0
- Background Music: Beethoven Symphony No. 6 'Pastoral' Allegro with dynamic sidechain ducking
- Ambient SFX: Autumn breeze & woodland birdsong (forest_birds_wind.mp3)
- Kodak 2383 D65 Print Film Emulation & EBU R128 Loudness Mastering
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path("/home/tamoghna/Documents/Video_editing")
sys.path.insert(0, str(WORKSPACE_ROOT))

from video_templates.presets.cinematic_landscape import render as render_cinematic_landscape

LOUGHBOROUGH_FILM = {
    "title": "LOUGHBOROUGH UNIVERSITY",
    "subtitle": "LEICESTERSHIRE • CAMPUS WALK",
    "outro_title": "LOUGHBOROUGH UNIVERSITY",
    "outro_subtitle": "Where Passion Shapes the Future 📍",
    "handle": "@tamoghna.travels",
    "footage_dir": WORKSPACE_ROOT / "01_raw_footage" / "lboro_university",
    "output_file": WORKSPACE_ROOT / "edit" / "cinematic_16x9" / "lboro_university_campus_journey.mp4",
    "qc_file": WORKSPACE_ROOT / "edit" / "verify" / "qc_sheet_lboro_journey.png",
    "lut": "Rec709 Kodak 2383 D65.cube",
    "grade": "clean_landscape",
    "music": "beethoven_symphony_no6_pastoral.mp3",
    "sfx": "forest_birds_wind.mp3",
    "voiceover_speed": 0.91,
    "voiceover_text": (
        "There is a quiet clarity in the morning air when you start walking towards campus, "
        "with the autumn sunlight filtering through the trees. | "
        "Passing down Epinal Way, you are greeted by Loughborough University. "
        "A campus renowned worldwide for innovation, sporting excellence, and drive. | "
        "Beyond the vibrant bustle of the Students' Union, the historic Hazlerigg Building "
        "stands proudly, framing the central fountain quadrangle. | "
        "There is an incredible sense of openness across these sprawling lawns. "
        "Room to breathe, room to think, and space to find your path. | "
        "Boarding the campus Sprint shuttle, watching the endless sports pitches drift by. "
        "In these quiet moments of commute, clarity always finds you. | "
        "Stepping back out into the academic precinct, ready for what lies ahead. "
        "Another day, another chapter written. Until next time."
    ),
    "shots": [
        ("DJI_20251027141310_0022_D.MP4", 0.5, 6.0, "MORNING COMMUTE // LEICESTERSHIRE APPROACH"),
        ("DJI_20251027141421_0023_D.MP4", 0.5, 5.5, "RESIDENTIAL CORRIDOR // SHADED WALKWAYS"),
        ("DJI_20251027141504_0024_D.MP4", 1.0, 9.0, "AVENUE GLIDE // HEADING TOWARDS CAMPUS"),
        ("DJI_20251027142035_0025_D.MP4", 0.5, 9.5, "LOUGHBOROUGH UNIVERSITY // MAIN GATEWAY"),
        ("DJI_20251027142035_0025_D.MP4", 17.5, 26.5, "THE GREEN SPINE // CANOPY WALKWAY"),
        ("DJI_20251027142246_0026_D.MP4", 1.0, 9.5, "STUDENTS' UNION // THE VIBRANT HEART"),
        ("DJI_20251027142602_0027_D.MP4", 0.5, 10.5, "HAZLERIGG BUILDING // HISTORIC CLOCK TOWER"),
        ("DJI_20251027142602_0027_D.MP4", 12.5, 22.5, "CENTRAL LAWNS // FOUNTAIN QUADRANGLE"),
        ("DJI_20251027142920_0028_D.MP4", 0.5, 6.5, "CAMPUS PROMENADE // AUTUMN SUNSHINE"),
        ("DJI_20251027142952_0029_D.MP4", 0.2, 3.2, "CAMPUS TRANSIT // SPRINT SHUTTLE ARRIVAL"),
        ("DJI_20251027143323_0030_D.MP4", 0.5, 5.0, "ATHLETIC FIELDS // HOME OF SPORTING EXCELLENCE"),
        ("DJI_20251027143343_0031_D.MP4", 1.0, 11.5, "SOLO COMMUTER // MOMENTS OF REFLECTION"),
        ("DJI_20251027143556_0032_D.MP4", 0.5, 6.0, "ACADEMIC PRECINCT // INNOVATION QUAD"),
        ("DJI_20251027143614_0033_D.MP4", 0.5, 5.5, "S BUILDING // MATERIALS & CHEMICAL ENGINEERING"),
    ]
}


def main():
    print("=" * 70)
    print("🎬 RENDERING LOUGHBOROUGH UNIVERSITY CINEMATIC 16:9 FILM (90s - 120s)")
    print("=" * 70)

    cfg = LOUGHBOROUGH_FILM
    shots = cfg["shots"]
    planned_dur = sum(et - st for _, st, et, _ in shots)
    print(f"📊 Planned Shot Sequence : {len(shots)} shots, total {planned_dur:.1f}s")
    print(f"🎵 Background Music      : {cfg['music']} (Beethoven Symphony No. 6 Pastoral)")
    print(f"🍃 Ambient SFX           : {cfg['sfx']}")
    print(f"🎙️ Voiceover Narration   : 6 Spaced Storytelling Phrases (speed={cfg['voiceover_speed']})")
    print(f"🎨 Color Grade           : Kodak 2383 D65 Print Film Emulation")
    print(f"📐 Canvas Format         : 16:9 Landscape (1920x1080) with 2.34:1 Black Letterbox Bars")

    res = render_cinematic_landscape(
        footage_dir=cfg["footage_dir"],
        output_file=cfg["output_file"],
        qc_file=cfg["qc_file"],
        title=cfg["title"],
        subtitle=cfg["subtitle"],
        outro_title=cfg["outro_title"],
        outro_subtitle=cfg["outro_subtitle"],
        handle=cfg["handle"],
        lut_name=cfg["lut"],
        grade_preset=cfg["grade"],
        music_track=cfg["music"],
        sfx_track=cfg["sfx"],
        max_duration=120.0,
        black_bars=True,
        shots=cfg["shots"],
        voiceover_text=cfg["voiceover_text"],
        voiceover_speed=cfg["voiceover_speed"]
    )

    out_file = Path(res["output_file"])
    qc_file = Path(res["qc_file"])
    print(f"\n🎉 Successfully rendered: {out_file.name}")
    print(f"   Size: {out_file.stat().st_size / (1024*1024):.1f} MB")
    print(f"   QC Contact Sheet: {qc_file.name}")


if __name__ == "__main__":
    main()
