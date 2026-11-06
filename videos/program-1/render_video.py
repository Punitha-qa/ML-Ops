"""Build a narrated MP4 locally. Requires Pillow, imageio-ffmpeg and macOS say.

The video uses the checked beginner example, not a video-generation API.
Intermediate audio stays outside the repository under --build-dir.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import textwrap
import wave
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H, FPS = 1280, 720, 20
BG, PANEL, INK = "#0C1427", "#17243D", "#F3F7FF"
MUTED, CYAN, GREEN, RED = "#B4C3DC", "#68DBEE", "#86E6BD", "#FFACAD"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def font(size, bold=False, mono=False):
    candidates = []
    if os.environ.get("VIDEO_FONT_DIR"):
        filename = "DejaVuSansMono.ttf" if mono else "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        candidates.append(Path(os.environ["VIDEO_FONT_DIR"]) / filename)
    name = "Courier New.ttf" if mono else "Arial Bold.ttf" if bold else "Arial.ttf"
    candidates.append(Path("/System/Library/Fonts/Supplemental") / name)
    name = "DejaVuSansMono.ttf" if mono else "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates.append(Path("/usr/share/fonts/truetype/dejavu") / name)
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


F = {"title": font(43, True), "body": font(29), "small": font(22),
     "tiny": font(17), "code": font(22, mono=True), "big": font(78, True),
     "caption": font(25), "bold": font(32, True)}


def txt(d, xy, value, style="body", color=INK, spacing=9):
    d.multiline_text(xy, value, font=F[style], fill=color, spacing=spacing)


def box(d, rect, fill=PANEL, outline=None, width=2, radius=18):
    d.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=width)


def arrow(d, start, end, color=CYAN, width=4):
    d.line([start, end], fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    points = [end]
    for a in [angle + 2.6, angle - 2.6]:
        points.append((end[0] + 17 * math.cos(a), end[1] + 17 * math.sin(a)))
    d.polygon(points, fill=color)


def two_steps(d, y=285, fitted=False):
    for x, title, subtitle in [(115, "Text converter", "TfidfVectorizer"),
                               (735, "Classifier", "LogisticRegression")]:
        box(d, (x, y, x + 430, y + 155), outline=GREEN if fitted else CYAN)
        txt(d, (x + 28, y + 28), title, "bold")
        txt(d, (x + 28, y + 87), subtitle, "small", MUTED)
    arrow(d, (565, y + 78), (714, y + 78))


def memory_file(d, mode):
    box(d, (95, 220, 525, 455), outline=CYAN)
    txt(d, (127, 241), "Python memory", "bold")
    txt(d, (127, 307), "Fitted text converter\nTrained classifier", "body", MUTED, 17)
    box(d, (770, 220, 1180, 455), outline=GREEN)
    txt(d, (800, 242), "File on disk", "bold")
    txt(d, (800, 310), "learning-spam-\nfilter.joblib", "code", GREEN)
    txt(d, (800, 398), "Both fitted steps", "small", MUTED)
    if mode == "save":
        arrow(d, (550, 335), (744, 335))
        txt(d, (563, 380), "dump()", "small", CYAN)
    else:
        arrow(d, (744, 335), (550, 335))
        txt(d, (563, 380), "load()", "small", CYAN)


def base_frame(scene, example):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    txt(d, (64, 30), "PROGRAM 01   /   SMS SPAM FILTER", "tiny", CYAN)
    txt(d, (64, 82), scene["title"], "title")
    kind = scene["kind"]
    if kind in {"title", "overview"}:
        labels = [("TRAIN", "fit()"), ("SAVE", "dump()"), ("LOAD", "load()"), ("PREDICT", "predict()")]
        for i, (label, method) in enumerate(labels):
            x = 85 + i * 306
            box(d, (x, 265, x + 210, 415), outline=CYAN if i < 2 else GREEN)
            txt(d, (x + 23, 291), label, "bold")
            txt(d, (x + 23, 355), method, "code", MUTED)
            if i < 3:
                arrow(d, (x + 225, 340), (x + 286, 340))
        txt(d, (85, 465), "One fitted pipeline, saved and reused.", "body", MUTED)
    elif kind == "messages":
        for y, message, label, color in [(220, "Can we meet for lunch?", "HAM", GREEN),
                                         (365, "Claim your free prize now!", "SPAM", RED)]:
            box(d, (105, y, 1175, y + 110))
            txt(d, (137, y + 33), message, "bold")
            box(d, (990, y + 27, 1145, y + 83), fill=color)
            txt(d, (1010, y + 38), label, "body", BG)
    elif kind == "training_data":
        messages = ["Claim your free prize now", "You have won a cash reward",
                    "Call now to claim your winnings", "Can we meet for lunch",
                    "Please bring your laptop tomorrow", "I will reach home by evening"]
        txt(d, (115, 190), "MESSAGE", "small", MUTED)
        txt(d, (1020, 190), "LABEL", "small", MUTED)
        for i, message in enumerate(messages):
            y = 231 + i * 46
            txt(d, (115, y), f"{i+1}.  {message}", "small")
            txt(d, (1020, y), "spam" if i < 3 else "ham", "small", RED if i < 3 else GREEN)
    elif kind in {"pipeline", "fit", "answer"}:
        two_steps(d, 275, fitted=kind != "pipeline")
        note = {"pipeline": "Message text                  Feature vector                  Prediction",
                "fit": "Vocabulary + term statistics                 Weights learned from labels",
                "answer": "One saved file keeps these fitted steps together."}[kind]
        txt(d, (115, 470), note, "small", MUTED)
        if kind == "fit":
            txt(d, (115, 205), "Training examples + correct labels", "body", CYAN)
    elif kind == "features":
        widths = [480, 155, 155, 155, 155]
        x = 90
        for col, width in zip(["Message", *example["columns"]], widths):
            txt(d, (x, 235), col, "small", CYAN)
            x += width
        rows = [("Can we meet for lunch tomorrow?", example["rows"][0]["values"]),
                ("Claim your free prize now", example["rows"][1]["values"])]
        for r, (message, values) in enumerate(rows):
            y = 310 + r * 90
            txt(d, (90, y), message, "small")
            x = 570
            for width, value in zip(widths[1:], values):
                txt(d, (x, y), f"{value:.3f}", "small", GREEN if value else MUTED)
                x += width
        txt(d, (90, 475), "Selected word columns. The full vector contains more positions.", "small", MUTED)
    elif kind == "memory":
        box(d, (250, 220, 1030, 455), outline=CYAN)
        txt(d, (290, 245), "RUNNING PYTHON PROCESS", "small", CYAN)
        txt(d, (290, 310), "Fitted text converter\nTrained classifier", "bold", INK, 19)
        txt(d, (250, 480), "Closing the process clears these in-memory objects.", "small", MUTED)
    elif kind in {"save", "load"}:
        memory_file(d, kind)
        txt(d, (95, 480), "The file preserves trained work. Loading restores it into memory.", "small", MUTED)
    elif kind == "new_message":
        box(d, (110, 195, 1170, 275))
        txt(d, (140, 215), '"Can we meet for lunch tomorrow?"', "bold")
        two_steps(d, 325, fitted=True)
    elif kind == "result":
        txt(d, (160, 205), '"Can we meet for lunch tomorrow?"', "bold")
        box(d, (400, 295, 880, 460), outline=GREEN)
        txt(d, (534, 307), "ham", "big", GREEN)
        txt(d, (465, 415), "ordinary message", "small", MUTED)
        txt(d, (250, 485), "Actual output from the saved beginner model.", "small", MUTED)
    elif kind == "question":
        txt(d, (130, 240), "Which TWO fitted parts\nmust we save together?", "title", INK, 25)
        txt(d, (130, 425), "Pause the video. Agree on one group answer.", "body", CYAN)
    elif kind == "finish":
        for i, line in enumerate(["Run the small example.", "Read the prediction.", "Change the message and try again."]):
            txt(d, (120, 225 + i * 70), f"{i+1}   {line}", "bold", GREEN if i == 0 else INK)
        txt(d, (120, 470), "Only load joblib files from trusted sources.", "small", MUTED)
    box(d, (64, 535, 1216, 588), fill="#22314C", radius=10)
    txt(d, (83, 551), scene["code"], "code", CYAN)
    return im


def caption_chunks(text):
    words = text.split()
    return [" ".join(words[i:i + 13]) for i in range(0, len(words), 13)]


def srt_time(seconds):
    millis = round(seconds * 1000)
    return f"{millis//3600000:02}:{millis//60000%60:02}:{millis//1000%60:02},{millis%1000:03}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=Path("/private/tmp/mlops-video-build"))
    parser.add_argument("--voice", default="Samantha")
    parser.add_argument("--audio-only", action="store_true")
    args = parser.parse_args()
    args.build_dir.mkdir(parents=True, exist_ok=True)
    scenes = json.loads((HERE / "storyboard.json").read_text())
    example = json.loads((HERE / "feature_examples.json").read_text())
    timings, all_captions, timeline = [], [], 0.0
    for i, scene in enumerate(scenes):
        stem = args.build_dir / f"scene-{i:02}"
        narration = stem.with_suffix(".txt")
        narration.write_text(scene["narration"])
        aiff, wav = stem.with_suffix(".aiff"), stem.with_suffix(".wav")
        if not aiff.exists() or aiff.stat().st_size < 5000:
            subprocess.run(["say", "-v", args.voice, "-r", "145", "-f", str(narration), "-o", str(aiff)], check=True)
        spoken_wav = stem.with_name(stem.name + "-spoken.wav")
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(aiff), "-ar", "44100", "-ac", "1", str(spoken_wav)], check=True)
        with wave.open(str(spoken_wav)) as audio:
            spoken_duration = audio.getnframes() / audio.getframerate()
        if spoken_duration < 1:
            raise ValueError("Narration is empty. Run the audio step with access to macOS speech services.")
        duration = math.ceil((spoken_duration + scene.get("pause", 1.5)) * FPS) / FPS
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(spoken_wav), "-af", "apad", "-t", str(duration), str(wav)], check=True)
        chunks = caption_chunks(scene["narration"])
        count = sum(len(c.split()) for c in chunks)
        relative = 0.0
        caps = []
        for chunk in chunks:
            end = relative + spoken_duration * len(chunk.split()) / count
            caps.append((relative, end, chunk))
            all_captions.append((timeline + relative, timeline + end, chunk))
            relative = end
        timings.append({"duration": duration, "spoken": spoken_duration, "wav": str(wav), "captions": caps})
        timeline += duration
        print(f"Audio {i+1}/{len(scenes)}: {duration:.1f}s", flush=True)
    stats = {"duration_seconds": round(timeline, 2), "narration_words": sum(len(s["narration"].split()) for s in scenes),
             "narration_characters": sum(len(s["narration"]) for s in scenes), "voice": args.voice,
             "width": W, "height": H, "fps": FPS, "scenes": len(scenes)}
    (HERE / "video_info.json").write_text(json.dumps(stats, indent=2) + "\n")
    (HERE / "captions.srt").write_text("\n\n".join(f"{i+1}\n{srt_time(start)} --> {srt_time(end)}\n{textwrap.fill(text, 72)}" for i, (start, end, text) in enumerate(all_captions)) + "\n")
    if args.audio_only:
        print(json.dumps(stats), flush=True)
        return
    audio_list = args.build_dir / "audio-list.txt"
    audio_list.write_text("\n".join(f"file '{x['wav']}'" for x in timings))
    joined_audio = args.build_dir / "narration.wav"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(audio_list), "-c", "copy", str(joined_audio)], check=True)
    output = HERE / "program-1-explained.mp4"
    encoder = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "pipe:0", "-i", str(joined_audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264",
        "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", "-shortest", str(output)], stdin=subprocess.PIPE)
    total_frames = 0
    stage_names = ["EXAMPLES", "TRAIN", "SAVE", "LOAD", "PREDICT"]
    for i, (scene, timing) in enumerate(zip(scenes, timings)):
        base = base_frame(scene, example)
        base.save(args.build_dir / f"review-{i:02}.png")
        frames = round(timing["duration"] * FPS)
        for j in range(frames):
            t = j / FPS
            im = base.copy()
            d = ImageDraw.Draw(im)
            if scene["kind"] in {"pipeline", "fit", "new_message", "answer"}:
                y = 353 if scene["kind"] != "new_message" else 403
                x = 567 + (t % 2) / 2 * 138
                d.ellipse((x-7, y-7, x+7, y+7), fill=INK)
            if scene["kind"] in {"save", "load"}:
                phase = (t % 2.5) / 2.5
                x = 550 + phase * 194 if scene["kind"] == "save" else 744 - phase * 194
                d.ellipse((x-8, 327, x+8, 343), fill=INK)
            if scene["kind"] == "training_data":
                row = int(t / 2) % 6
                y = 226 + row * 46
                d.rounded_rectangle((96, y-2, 1180, y+36), radius=7, outline=CYAN, width=2)
            if scene["kind"] in {"title", "overview"}:
                x = 85 + (int(t / 2) % 4) * 306
                d.rounded_rectangle((x-3, 262, x+213, 418), radius=20, outline=INK, width=3)
            caption = next((c for start, end, c in timing["captions"] if start <= t < end), "")
            if caption:
                lines = textwrap.wrap(caption, width=82)
                for line_index, line in enumerate(lines):
                    width = d.textlength(line, font=F["caption"])
                    txt(d, ((W-width)/2, 610+line_index*32), line, "caption", INK)
            for stage, name in enumerate(stage_names):
                txt(d, (83 + stage * 244, 689), name, "tiny", CYAN if stage == scene["stage"] else "#7B8CA8")
            overall = (total_frames + j + 1) / (timeline * FPS)
            d.rectangle((0, 716, round(W * overall), 719), fill=CYAN)
            encoder.stdin.write(im.tobytes())
        total_frames += frames
        print(f"Rendered {i+1}/{len(scenes)}: {scene['title']}", flush=True)
    encoder.stdin.close()
    if encoder.wait() != 0:
        raise RuntimeError("Video encoding failed")
    print(json.dumps({**stats, "output": str(output), "megabytes": round(output.stat().st_size/1_000_000, 2)}), flush=True)


if __name__ == "__main__":
    main()
