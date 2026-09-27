from pathlib import Path

path = Path("scripts/persist_video_pipeline.py")
text = path.read_text()

old = 'print(f"Total trajectories: {len(trajectories)}")'

new = '''print(f"Total trajectories: {len(trajectories)}")
for trajectory in trajectories:
    print(
        trajectory.get("vehicle_id"),
        repr(trajectory.get("plate")),
        repr(trajectory.get("ocr_confidence")),
    )'''

if old not in text:
    raise SystemExit("Target line not found.")

path.write_text(text.replace(old, new))
print("Debug print added.")
