#!/usr/bin/env python3
"""Inserisce un pezzo generato da AI dentro un video originale, nel punto di aggancio.

Uso: python3 insert_ai_clip.py originale.mp4 pezzo_ai.mp4 t_aggancio uscita.mp4

Il pezzo AI deve iniziare e finire sul frame dell'originale a t_aggancio (start/end frame uguali).
Video: originale [0, t) + pezzo AI + originale [t, fine]. Audio: originale continuo fino a t, poi
ambiente ripreso da prima di t per la durata del pezzo, poi originale da t: la risalita resta in sync.
"""
import subprocess, sys

src, ai, t, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ai],
                           capture_output=True, text=True).stdout)
fc = (f"[0:v]trim=0:{t},setpts=PTS-STARTPTS,fps=30,format=yuv420p[a];"
      f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p,"
      f"setpts=PTS-STARTPTS,setsar=1[b];"
      f"[0:v]trim=start={t},setpts=PTS-STARTPTS,fps=30,format=yuv420p,setsar=1[c];"
      f"[a]setsar=1[a2];[a2][b][c]concat=n=3:v=1:a=0[v];"
      f"[0:a]atrim=0:{t},asetpts=PTS-STARTPTS[x];"
      f"[0:a]atrim={max(t - dur, 0)}:{t},asetpts=PTS-STARTPTS,volume=0.8[y];"
      f"[0:a]atrim=start={t},asetpts=PTS-STARTPTS[z];[x][y][z]concat=n=3:v=0:a=1[au]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", ai, "-filter_complex", fc, "-map", "[v]", "-map", "[au]",
                "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", out], check=True)
print("OK ->", out)
