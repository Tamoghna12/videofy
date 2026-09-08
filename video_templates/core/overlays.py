"""
overlays.py - Kinetic Typography, Progress Bar & Overlays Engine
Supports 9:16 Portrait and 16:9 Landscape layouts with safe string escaping.
"""

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def clean_text(s):
    """Sanitize strings for FFmpeg drawtext parameters."""
    if not s:
        return ""
    return s.replace("'", "’").replace(":", " -").replace("\\", "")


def build_timeline_overlays(
    total_duration,
    shot_captions=None,
    intro_title="DISCOVER IRELAND",
    intro_subtitle="WILD ATLANTIC WAY",
    outro_title="TRAVEL MOMENTS",
    outro_subtitle="Save this for your next adventure 📍",
    handle="@travel.moments",
    aspect="9:16",
    black_bars=False
):
    """
    Build FFmpeg drawtext and drawbox filtergraph for 9:16 Portrait or 16:9 Landscape.
    Supports black_bars mode for top and bottom cinematic framing with dedicated text canvases.
    """
    filters = []
    is_portrait = (aspect == "9:16")

    if black_bars and is_portrait:
        # =========================================================================
        # CINEMATIC BLACK BARS LAYOUT (Top: h=200px, Bottom: h=240px)
        # =========================================================================
        # 1. Top black matte bar
        filters.append("drawbox=x=0:y=0:w=1080:h=200:color=black@1.0:t=fill")
        # Gold accent hairline at base of top frame
        filters.append("drawbox=x=0:y=198:w=1080:h=2:color=0xE5A93C@0.85:t=fill")
        # Animated top progress bar along the accent line
        filters.append(
            f"drawbox=x=0:y=196:w='1080*(t/{total_duration:.3f})':h=3:color=0xFFD700@1:t=fill"
        )

        # Top Text: Location / Context representing the video journey
        clean_in_title = clean_text(intro_title)
        clean_in_sub = clean_text(intro_subtitle)
        if clean_in_title:
            filters.append(
                f"drawtext=fontfile='{FONT_BOLD}':text='{clean_in_title}':fontsize=32:fontcolor=white:x=(w-text_w)/2:y=72"
            )
        if clean_in_sub:
            filters.append(
                f"drawtext=fontfile='{FONT_REG}':text='{clean_in_sub}':fontsize=19:fontcolor=0xE5A93C:x=(w-text_w)/2:y=122"
            )

        # 2. Bottom black matte bar (dedicated canvas for kinetic highlighted subtitles)
        filters.append("drawbox=x=0:y=1660:w=1080:h=260:color=black@1.0:t=fill")
        # Gold accent hairline at top of bottom frame
        filters.append("drawbox=x=0:y=1660:w=1080:h=2:color=0xE5A93C@0.85:t=fill")

        # 3. Outro CTA Card (final 4.0s) centered in visual viewport
        outro_start = max(0.0, total_duration - 4.0)
        outro_alpha = f"if(between(t,{outro_start:.2f},{total_duration:.2f}),if(lt(t,{outro_start+0.4:.2f}),(t-{outro_start:.2f})/0.4,1),0)"
        clean_out_title = clean_text(outro_title)
        clean_out_sub = clean_text(outro_subtitle)

        if clean_out_title:
            filters.append(
                f"drawbox=x=120:y=800:w=840:h=220:color=black@0.85:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
            )
            filters.append(
                f"drawbox=x=120:y=800:w=840:h=4:color=0xE5A93C@0.95:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
            )
            filters.append(
                f"drawtext=fontfile='{FONT_BOLD}':text='{clean_out_title}':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=840:alpha='{outro_alpha}'"
            )
            filters.append(
                f"drawtext=fontfile='{FONT_REG}':text='{clean_out_sub}':fontsize=24:fontcolor=0xE5A93C:x=(w-text_w)/2:y=915:alpha='{outro_alpha}'"
            )

        return ",".join(filters)

    if black_bars and not is_portrait:
        # =========================================================================
        # CINEMATIC 16:9 LANDSCAPE BLACK BARS LAYOUT (Top: h=120px, Bottom: h=140px)
        # =========================================================================
        # 1. Top black matte bar
        filters.append("drawbox=x=0:y=0:w=1920:h=120:color=black@1.0:t=fill")
        # Gold accent hairline at base of top frame
        filters.append("drawbox=x=0:y=118:w=1920:h=2:color=0xE5A93C@0.85:t=fill")
        # Animated top progress bar along the accent line
        filters.append(
            f"drawbox=x=0:y=116:w='1920*(t/{total_duration:.3f})':h=3:color=0xFFD700@1:t=fill"
        )

        # Top Text: Location / Context representing the video journey
        clean_in_title = clean_text(intro_title)
        clean_in_sub = clean_text(intro_subtitle)
        if clean_in_title:
            filters.append(
                f"drawtext=fontfile='{FONT_BOLD}':text='{clean_in_title}':fontsize=28:fontcolor=white:x=(w-text_w)/2:y=38"
            )
        if clean_in_sub:
            filters.append(
                f"drawtext=fontfile='{FONT_REG}':text='{clean_in_sub}':fontsize=17:fontcolor=0xE5A93C:x=(w-text_w)/2:y=76"
            )

        # 2. Bottom black matte bar (dedicated canvas for kinetic highlighted subtitles)
        filters.append("drawbox=x=0:y=940:w=1920:h=140:color=black@1.0:t=fill")
        # Gold accent hairline at top of bottom frame
        filters.append("drawbox=x=0:y=940:w=1920:h=2:color=0xE5A93C@0.85:t=fill")

        # 3. Outro CTA Card (final 4.0s) centered in visual viewport
        outro_start = max(0.0, total_duration - 4.0)
        outro_alpha = f"if(between(t,{outro_start:.2f},{total_duration:.2f}),if(lt(t,{outro_start+0.4:.2f}),(t-{outro_start:.2f})/0.4,1),0)"
        clean_out_title = clean_text(outro_title)
        clean_out_sub = clean_text(outro_subtitle)

        if clean_out_title:
            filters.append(
                f"drawbox=x=560:y=450:w=800:h=180:color=black@0.85:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
            )
            filters.append(
                f"drawbox=x=560:y=450:w=800:h=4:color=0xE5A93C@0.95:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
            )
            filters.append(
                f"drawtext=fontfile='{FONT_BOLD}':text='{clean_out_title}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=485:alpha='{outro_alpha}'"
            )
            filters.append(
                f"drawtext=fontfile='{FONT_REG}':text='{clean_out_sub}':fontsize=20:fontcolor=0xE5A93C:x=(w-text_w)/2:y=545:alpha='{outro_alpha}'"
            )

        return ",".join(filters)

    # Standard full-bleed layout
    pw = 1080 if is_portrait else 1920
    ph = 8 if is_portrait else 6
    filters.append(
        f"drawbox=x=0:y=0:w='{pw}*(t/{total_duration:.3f})':h={ph}:color=0xE5A93C@1:t=fill"
    )

    # 2. Intro Card (0.4s - 4.0s)
    intro_start = 0.4
    intro_end = 4.0
    intro_alpha = f"if(between(t,{intro_start},{intro_end}),if(lt(t,{intro_start+0.4}),(t-{intro_start})/0.4,if(gt(t,{intro_end-0.4}),({intro_end}-t)/0.4,1)),0)"
    
    clean_in_title = clean_text(intro_title)
    clean_in_sub = clean_text(intro_subtitle)

    if is_portrait:
        filters.append(
            f"drawbox=x=120:y=360:w=840:h=180:color=black@0.65:t=fill:enable='between(t,{intro_start},{intro_end})'"
        )
        filters.append(
            f"drawbox=x=115:y=360:w=6:h=180:color=0xE5A93C@0.95:t=fill:enable='between(t,{intro_start},{intro_end})'"
        )
        filters.append(
            f"drawtext=fontfile='{FONT_BOLD}':text='{clean_in_title}':fontsize=48:fontcolor=white:x=150:y=390:alpha='{intro_alpha}'"
        )
        filters.append(
            f"drawtext=fontfile='{FONT_REG}':text='{clean_in_sub}':fontsize=22:fontcolor=0xE0E0E0:x=152:y=465:alpha='{intro_alpha}'"
        )
    else:
        # Landscape: Lower-left position
        filters.append(
            f"drawbox=x=100:y=720:w=720:h=150:color=black@0.65:t=fill:enable='between(t,{intro_start},{intro_end})'"
        )
        filters.append(
            f"drawbox=x=95:y=720:w=5:h=150:color=0xE5A93C@0.95:t=fill:enable='between(t,{intro_start},{intro_end})'"
        )
        filters.append(
            f"drawtext=fontfile='{FONT_BOLD}':text='{clean_in_title}':fontsize=46:fontcolor=white:x=125:y=745:alpha='{intro_alpha}'"
        )
        filters.append(
            f"drawtext=fontfile='{FONT_REG}':text='{clean_in_sub}':fontsize=24:fontcolor=0xE0E0E0:x=127:y=808:alpha='{intro_alpha}'"
        )

    # 3. Lower-third captions
    if shot_captions:
        curr_time = 0.0
        for dur, caption in shot_captions:
            if caption:
                c_clean = clean_text(caption)
                cap_start = curr_time + 0.3
                cap_end = curr_time + dur - 0.3
                if cap_end > cap_start + 0.6:
                    cap_alpha = f"if(between(t,{cap_start:.2f},{cap_end:.2f}),if(lt(t,{cap_start+0.3:.2f}),(t-{cap_start:.2f})/0.3,if(gt(t,{cap_end-0.3:.2f}),({cap_end:.2f}-t)/0.3,1)),0)"
                    if is_portrait:
                        filters.append(
                            f"drawbox=x=80:y=1640:w=920:h=90:color=black@0.60:t=fill:enable='between(t,{cap_start:.2f},{cap_end:.2f})'"
                        )
                        filters.append(
                            f"drawtext=fontfile='{FONT_BOLD}':text='{c_clean}':fontsize=28:fontcolor=white:x=(w-text_w)/2:y=1672:alpha='{cap_alpha}'"
                        )
                    else:
                        filters.append(
                            f"drawbox=x=(w-1050)/2:y=950:w=1050:h=56:color=black@0.60:t=fill:enable='between(t,{cap_start:.2f},{cap_end:.2f})'"
                        )
                        filters.append(
                            f"drawtext=fontfile='{FONT_BOLD}':text='{c_clean}':fontsize=26:fontcolor=white:x=(w-text_w)/2:y=965:alpha='{cap_alpha}'"
                        )
            curr_time += dur

    # 4. Outro CTA Card (final 4.0s)
    outro_start = max(0.0, total_duration - 4.0)
    outro_alpha = f"if(between(t,{outro_start:.2f},{total_duration:.2f}),if(lt(t,{outro_start+0.4:.2f}),(t-{outro_start:.2f})/0.4,1),0)"
    clean_out_title = clean_text(outro_title)
    clean_out_sub = clean_text(outro_subtitle)

    if is_portrait:
        filters.append(
            f"drawbox=x=120:y=770:w=840:h=240:color=black@0.75:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
        )
        filters.append(
            f"drawbox=x=120:y=770:w=840:h=4:color=0xE5A93C@0.95:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
        )
        filters.append(
            f"drawtext=fontfile='{FONT_BOLD}':text='{clean_out_title}':fontsize=50:fontcolor=white:x=(w-text_w)/2:y=805:alpha='{outro_alpha}'"
        )
        filters.append(
            f"drawtext=fontfile='{FONT_REG}':text='{clean_out_sub}':fontsize=26:fontcolor=0xE5A93C:x=(w-text_w)/2:y=885:alpha='{outro_alpha}'"
        )
    else:
        filters.append(
            f"drawbox=x=(w-760)/2:y=(h-180)/2:w=760:h=180:color=black@0.75:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
        )
        filters.append(
            f"drawbox=x=(w-760)/2:y=(h-180)/2:w=760:h=4:color=0xE5A93C@0.95:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
        )
        filters.append(
            f"drawtext=fontfile='{FONT_BOLD}':text='{clean_out_title}':fontsize=46:fontcolor=white:x=(w-text_w)/2:y=485:alpha='{outro_alpha}'"
        )
        filters.append(
            f"drawtext=fontfile='{FONT_REG}':text='{clean_out_sub}':fontsize=26:fontcolor=0xE5A93C:x=(w-text_w)/2:y=555:alpha='{outro_alpha}'"
        )

    # 5. Watermark Handle
    if handle:
        clean_h = clean_text(handle)
        hy = 1820 if is_portrait else 1030
        hx = 80 if is_portrait else 100
        filters.append(
            f"drawtext=fontfile='{FONT_REG}':text='{clean_h}':fontsize=22:fontcolor=white@0.6:x={hx}:y={hy}"
        )

    return ",".join(filters)
