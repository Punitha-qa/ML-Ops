# Program 1 video

Watch [the narrated video](program-1-explained.mp4) to follow the small beginner example from training messages to a saved pipeline and a prediction after loading it. Download the MP4 if GitHub does not show a video player.

The video is about 3 minutes 28 seconds, with computer-generated English narration, on-screen captions and a group discussion pause. Captions are also available in [SRT format](captions.srt).

The story uses six synthetic training messages to make each step visible. It does not demonstrate reliable spam detection. Continue to [the full Program 1 lab](../../labs/1_model_packaging/README.md) for the larger dataset, held-out evaluation and artifact metadata.

The decimal feature values and the `ham` prediction shown in the video come from the included [beginner example](example.py). Its demonstration artifact is named `learning-spam-filter.joblib`, so it does not replace the full lab's model.

After the root repository setup, run these commands from the repository root with the same virtual environment activated.

**First run: train and save.**

```bash
python videos/program-1/example.py
```

Wait until the script finishes and the terminal prompt returns. Its Python process has ended; the fitted objects are no longer held in that process's memory. The file remains at `artifacts/learning-spam-filter.joblib`.

**Second run: start a new Python process to load and predict.**

```bash
python videos/program-1/predict.py
```

[The prediction script](predict.py) has no training examples and never calls `fit`. It reloads both fitted steps from disk and prints the predicted label. You do not need to close your editor or terminal: finishing the first script and running the second starts two separate Python processes.

The video introduces the save/load operations; the runnable example separates them into these two scripts to demonstrate persistence across processes.

## Video source

`storyboard.json` contains the narration and scene order. `render_video.py` creates the animated MP4 and captions. `feature_examples.json` records selected feature values from the executed beginner example. `video_info.json` records the duration and encoding settings.

Rebuilding needs macOS with the installed Samantha voice, Python, Pillow and imageio-ffmpeg. Use a separate environment for the video tools so the model's pinned environment stays consistent:

```bash
python3.12 -m venv .video-venv
source .video-venv/bin/activate
python -m pip install pillow==12.3.0 imageio-ffmpeg==0.8.1
python videos/program-1/render_video.py --audio-only
python videos/program-1/render_video.py
```

The default temporary build directory is `/private/tmp/mlops-video-build`. If you change the narration or voice, use a fresh `--build-dir` so old cached speech is not reused. This builder uses local text-to-speech and video encoding, with no external generation API.

References: [scikit-learn text features](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction), [Pipeline](https://scikit-learn.org/stable/modules/compose.html), and [joblib persistence](https://joblib.readthedocs.io/en/latest/persistence.html).
