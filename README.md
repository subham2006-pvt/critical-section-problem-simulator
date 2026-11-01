# Critical Section Problem Simulator

An educational Flask dashboard for visualizing mutual exclusion and synchronization using:
- Mutex lock
- Binary semaphore
- Peterson's algorithm (two processes only)

## Requirements
- Python 3.10+
- pip

## Run on macOS
```bash
cd critical_section_simulator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Controls
- Choose an algorithm and process count.
- Click **Run one step** to advance the educational simulation by one transition.
- Click **Run 8 steps** to advance several transitions.
- Reset to clear the current run.

## Important model notes
This is a deterministic, step-driven educational model. It is not a kernel scheduler and does not create real concurrent OS processes. Waiting times and throughput are simulated metrics, not benchmark results. Peterson's algorithm is restricted to two processes. The UI shows zero mutual-exclusion violations in the modeled transitions; this is not a formal proof of correctness.

## Project structure
- `app.py`: Flask routes and API
- `simulator.py`: simulation state and algorithm behavior
- `templates/index.html`: dashboard markup
- `static/style.css`: responsive dark dashboard styling
- `static/app.js`: controls and rendering
