"""
batch_update_all_reels.py - Batch Render All Reels with Cinematic Black Bars & Grounded Storytelling
Applies the tuned letterbox format, unhurried voiceover, kinetic word highlighting,
and multi-interval sidechain ducking across all active footage directories.
"""

import sys
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path("/home/tamoghna/Documents/Video_editing")

REELS = [
    {
        "name": "York Day 1 Part 2 (Medieval Shambles)",
        "footage": "raw_footage/york/day1_part2",
        "output": "edit/reels_9x16/york_day1_part2_medieval_reel.mp4",
        "qc": "edit/verify/qc_sheet_york_day1_part2.png",
        "title": "MEDIEVAL YORK",
        "subtitle": "THE SHAMBLES & STONEGATE",
        "outro_title": "TIMELESS YORK",
        "outro_subtitle": "Walk through history 📍",
        "voiceover": "Step off the modern streets, into fourteenth-century cobblestones. | Timber-framed houses leaning so close, you can almost touch across the alley. | You don't just visit York... you walk through seven hundred years of living history.",
        "music": "solas_jamie_duffy",
        "sfx": "gentle_rain_ambience",
        "lut": "CINECOLOR_GOLDEN_HOUR.CUBE",
        "duration": 36.0
    },
    {
        "name": "Northern Ireland: Castlerock",
        "footage": "raw_footage/Northern Ireland/castle_rock",
        "output": "edit/reels_9x16/castlerock_insta_reel_9x16.mp4",
        "qc": "edit/verify/qc_sheet_castlerock_reel.png",
        "title": "CASTLEROCK, NORTHERN IRELAND",
        "subtitle": "CAUSEWAY COASTAL ROUTE",
        "outro_title": "DISCOVER CASTLEROCK",
        "outro_subtitle": "Save for your Causeway trip 📍",
        "voiceover": "Where the road quietly turns toward the sea. | Salty Atlantic breezes rolling over the coastal moors and golden dunes. | Take a breath... this is the wild north coast at its most peaceful.",
        "music": "solas_jamie_duffy",
        "sfx": "ocean_waves_crashing.mp3",
        "lut": "CINECOLOR_GOLDEN_HOUR.CUBE",
        "duration": 36.0
    },
    {
        "name": "Northern Ireland: Dunluce Castle",
        "footage": "raw_footage/Northern Ireland/dunluce_castle",
        "output": "edit/reels_9x16/dunluce_castle_template_reel.mp4",
        "qc": "edit/verify/qc_sheet_dunluce_template.png",
        "title": "DUNLUCE CASTLE",
        "subtitle": "NORTH ANTRIM COAST • EST. 1500",
        "outro_title": "ANTRIM COASTLINE",
        "outro_subtitle": "Explore the ruins of Ireland 📍",
        "voiceover": "Emerging from the North Atlantic sea mist. | A medieval fortress clinging to the edge of a sheer hundred-foot basalt cliff. | Stories whispered by the waves... of kings, storms, and the wild Irish sea.",
        "music": "solas_jamie_duffy",
        "sfx": "ocean_waves_crashing.mp3",
        "lut": "CINECOLOR_GOLDEN_HOUR.CUBE",
        "duration": 36.0
    },
    {
        "name": "Whitby: Historic Harbour & Abbey",
        "footage": "raw_footage/whitby",
        "output": "edit/reels_9x16/whitby_portrait_cinematic.mp4",
        "qc": "edit/verify/qc_sheet_whitby_cinematic.png",
        "title": "WHITBY, YORKSHIRE",
        "subtitle": "HISTORIC HARBOUR & ABBEY",
        "outro_title": "EXPERIENCE WHITBY",
        "outro_subtitle": "Save this coastal escape 📍",
        "voiceover": "Crossing the river high above Whitby harbour. | Salt air, fishing boats swaying gently on the tide, and the ancient abbey standing watch. | A town that has inspired storytellers and mariners for centuries.",
        "music": "solas_jamie_duffy",
        "sfx": "ocean_waves_crashing.mp3",
        "lut": "CINECOLOR_GOLDEN_HOUR.CUBE",
        "duration": 36.0
    },
    {
        "name": "Scarborough: South Bay & Headland",
        "footage": "raw_footage/scarboro",
        "output": "edit/reels_9x16/scarborough_portrait_cinematic.mp4",
        "qc": "edit/verify/qc_sheet_scarboro_cinematic.png",
        "title": "SCARBOROUGH COAST",
        "subtitle": "SOUTH BAY & CASTLE HEADLAND",
        "outro_title": "YORKSHIRE COASTLINE",
        "outro_subtitle": "Save for your summer road trip 📍",
        "voiceover": "The open Yorkshire roads leading you straight to the sea. | Sweeping coastal views across the golden crescent of South Bay. | Standing high above the water, watching the summer tide gently roll in.",
        "music": "solas_jamie_duffy",
        "sfx": "ocean_waves_crashing.mp3",
        "lut": "CINECOLOR_GOLDEN_HOUR.CUBE",
        "duration": 36.0
    }
]

def main():
    print("=" * 80)
    print("🎬 VIDEOPY BATCH UPGRADE: UPDATING ALL REELS WITH CINEMATIC BLACK BARS")
    print("=" * 80)
    
    for i, r in enumerate(REELS, 1):
        print(f"\n[{i}/{len(REELS)}] Processing: {r['name']}")
        print(f"  📂 Footage : {r['footage']}")
        print(f"  🎯 Output  : {r['output']}")
        
        cmd = [
            sys.executable, str(WORKSPACE_ROOT / "render_template.py"),
            "--preset", "insta_catchy_reel",
            "--footage", str(WORKSPACE_ROOT / r["footage"]),
            "--title", r["title"],
            "--subtitle", r["subtitle"],
            "--outro-title", r["outro_title"],
            "--outro-subtitle", r["outro_subtitle"],
            "--voiceover", r["voiceover"],
            "--voiceover-speed", "0.92",
            "--black-bars",
            "--music", r["music"],
            "--sfx", r["sfx"],
            "--lut", r["lut"],
            "--accel", "auto",
            "--beat-sync",
            "--duration", str(r["duration"]),
            "--output", str(WORKSPACE_ROOT / r["output"]),
            "--qc", str(WORKSPACE_ROOT / r["qc"])
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"  ✅ Finished: {r['name']}")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed: {r['name']} ({e})")
            sys.exit(1)

    print("\n" + "=" * 80)
    print("🎉 ALL REELS SUCCESSFULLY UPDATED WITH CINEMATIC FRAMING & VOICE-STORYTELLING!")
    print("=" * 80)

if __name__ == "__main__":
    main()
