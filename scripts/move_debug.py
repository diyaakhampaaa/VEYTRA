from pathlib import Path

p = Path("scripts/persist_video_pipeline.py")
text = p.read_text()

start = text.index('db = SessionLocal()')
debug_start = text.index('trajectories = match_result.get("trajectories", [])', start)
debug_end = text.index('\nfor trajectory in trajectories[:16]:', debug_start)

debug_block = text[debug_start:debug_end]
text = text[:start] + debug_block + '\n\n' + text[start:debug_start] + text[debug_end:]

p.write_text(text)
print("Diagnostic moved before database save.")
