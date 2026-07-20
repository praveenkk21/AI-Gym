# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

AI-Gym is a Streamlit web app for AI-powered gym workout tracking. It uses a webcam (via WebRTC) to detect exercise form in real time using MediaPipe pose estimation, counts reps/sets, and persists workout history to a local SQLite database.

## Running the App

```bash
streamlit run main.py
```

There are no tests, no build step, and no linter configuration. Install dependencies with:

```bash
pip install -r requirements.txt
```

The app requires a `.env` file (gitignored) for the Groq API key used by the voice coaching pipeline.

## Architecture

### Entry Point and Lifecycle

`main.py` owns the entire page. On each Streamlit rerun it:
1. Injects CSS/font via `services/ui/style_loader.py`
2. Initializes the SQLite DB (idempotent DDL)
3. Runs the login wall — returns early if the user is not authenticated
4. Calls `initial_session_defaults()` to populate `st.session_state` without overwriting
5. Renders sidebar (workout config or live stats) and main panel
6. If workout is active, mounts the `webrtc_streamer` with `VideoProcessorClass`
7. Calls `sync_metrics_update()` to pull data from the WebRTC thread into `st.session_state`
8. Sleeps briefly and calls `st.rerun()` to poll while the camera is live

### Threading Boundary

`VideoProcessorClass` (in `services/vision/exercise_video_processor.py`) runs in a background thread managed by `streamlit-webrtc`. It stores results in `self._latest_metrics` behind a `threading.Lock`. The Streamlit main thread reads these via `processor.get_latest_metrics()` inside `sync_metrics_update()`. **Never access `st.session_state` from inside `VideoProcessorClass`** — it is not thread-safe.

### Exercise Detector Pattern

All detectors follow the same pattern:
- `core/base_exercise.py` — abstract base providing `calculate_angle()`, `get_point()`, and abstract `process(landmarks) -> dict` / `reset()`
- Each file in `detectors/` subclasses `BaseExercise` and implements a two-threshold state machine (`stage = "up"/"down"`) to count reps and assess form
- Detectors are registered by string key in `VideoProcessorClass._detectors` and selected via `self._exercise_type`

To add a new exercise: create `detectors/my_exercise.py` subclassing `BaseExercise`, implement `process()` and `reset()`, register the class in `VideoProcessorClass._detectors`, and add the exercise name to `services/config/workout_config.py`.

### State Management

All UI and workout state lives in `st.session_state`. `services/state/session_defaults.py` defines all keys and their defaults — consult it before adding new state to avoid key collisions.

### Persistence

SQLite (`data.db`, beside `main.py`). Two tables: `users` and `exercises`. All DB access goes through `services/persistence/exercise_repository.py`. The connection is cached with `@st.cache_resource`. The `add_exercise` function upserts by checking for a same-day row for the same user+exercise.

### Voice Coaching Pipeline

`requirements.txt` includes `groq` and `gtts`. The LLM system prompt is in `services/config/workout_config.py` as `PROMPT`. The pipeline is referenced in `sync_metrics_update()` via `st.session_state.voice_pipeline` but the implementation is not yet wired up in a visible file — treat this as an extension point.

### Styling

`static/style.css` is base64-injected into the page by `style_loader.py`, which also patches the WebRTC iframe's internal styles via injected JavaScript. Theme colors are defined in `.streamlit/config.toml`.
