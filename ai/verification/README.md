# Member 4 — Smart Verification + Self-Correction

VEYTRA's core USP module. Owns VERIFY and CORRECT in the pipeline:

DETECT -> READ -> TRACK -> MATCH (Re-ID) -> **VERIFY -> CORRECT** -> RECONSTRUCT -> ANALYZE -> VISUALIZE -> ALERT

Given a vehicle event, decides whether the plate reading is suspicious,
searches nearby cameras for supporting evidence, scores how confident
we are, corrects the record if warranted (while always preserving the
original reading), and logs every decision for audit.

## Current status

| Component | Status |
|---|---|
| Suspicion detection, evidence search, scoring, correction, logging | Complete, tested |
| FastAPI wrapper (`POST /verify`, `GET /verification-logs`) | Complete |
| Async/background worker | Complete |
| Camera network + event data | **Placeholder** (own test data) — real data pending Member 3 (see below) |

## Known integration gap (flagged with the team)

Member 3's current `matcher.py` rejects any cross-camera match where
plate text differs (`reject_reason="plate_mismatch"`), before this
module would ever see the event. This module's whole purpose is to
handle exactly those plate-mismatch cases — this needs to be resolved
with Member 3 so mismatched-but-plausible events reach `/verify`
instead of being dropped upstream.

## Install

```bash
cd ai/verification
pip install -r requirements.txt
```

## Usage

### As Python functions
```python
from ai.verification.suspicion import check_suspicion
from ai.verification.evidence import find_supporting_evidence
from ai.verification.scoring import find_best_candidate
from ai.verification.correction import apply_correction
from ai.verification.logger import log_verification_decision

event = {
    "event_id": "EVT1023", "camera_id": "C14", "plate": "DL01AB1284",
    "ocr_confidence": 0.61, "timestamp": "2026-09-06T15:30:00",
}
verdict = check_suspicion(event)
if verdict["is_suspicious"]:
    supporting = find_supporting_evidence(event)
    best = find_best_candidate(event["plate"], supporting, reid_similarity=0.93)
    result = apply_correction(event["event_id"], event["plate"], best, reid_similarity=0.93)
    log_verification_decision(result, original_confidence=event["ocr_confidence"])
```

### HTTP API
```bash
uvicorn ai.verification.api:app --reload
```
```bash
curl -X POST "http://127.0.0.1:8000/verify" -H "Content-Type: application/json" -d '{
  "event_id": "EVT1023", "camera_id": "C14", "plate": "DL01AB1284",
  "ocr_confidence": 0.61, "timestamp": "2026-09-06T15:30:00", "reid_similarity": 0.93
}'
```

### Async / background
```python
import asyncio
from ai.verification.worker import verify_many_events_async
results = asyncio.run(verify_many_events_async([event1, event2, ...]))
```

## Sample I/O (the USP scenario)

Input:
```json
{
  "event_id": "EVT1023", "camera_id": "C14", "plate": "DL01AB1284",
  "ocr_confidence": 0.61, "timestamp": "2026-09-06T15:30:00", "reid_similarity": 0.93
}
```

Output:
```json
{
  "event_id": "EVT1023",
  "original_plate": "DL01AB1284",
  "corrected_plate": "DL01AB1234",
  "supporting_cameras": ["C13", "C15"],
  "reid_similarity": 0.93,
  "verification_confidence": 0.93,
  "reason": "Neighbouring camera agreement (C13, C15) + high Re-ID similarity"
}
```

## Data contract

Input: a vehicle event (`event_id`, `camera_id`, `plate`, `ocr_confidence`,
`timestamp`, optional `reid_similarity`).

Output: exact shape shown above. If no correction is made,
`corrected_plate` equals `original_plate`, and `reason` explains why.

## Testing

```bash
pytest ai/verification/tests/ -v
```
10/10 passing. Covers: clean events, low-confidence flagging, neighbour
disagreement (independent of confidence), missing plate data, scoring
with/without `reid_similarity` (confidence-ceiling fallback), conflicting
evidence resolution, no-evidence handling, and the full USP scenario
(wrong plate at one camera, correct at two neighbours -> caught,
corrected, logged) plus a negative case (lone vehicle, no evidence ->
never force-corrected).

## Files

```
ai/verification/
  suspicion.py         # flags suspicious events (low confidence, neighbour disagreement)
  camera_network.py    # placeholder camera-connection graph (swap for Member 3's real one)
  fake_event_store.py  # placeholder event "database" (swap for real PostgreSQL query)
  evidence.py           # finds nearby supporting events within a travel-time window
  scoring.py            # combines plate similarity + reid_similarity + evidence count -> confidence
  correction.py         # decides correct/don't-correct, always preserves original_plate
  logger.py             # writes verification_logs audit trail
  api.py                # FastAPI: POST /verify, GET /verification-logs
  worker.py             # async/background verification path
  tests/                # pytest suite, incl. test_end_to_end.py (USP scenario)
```
