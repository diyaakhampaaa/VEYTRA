from ai.verification.scoring import find_best_candidate, score_candidate


def test_score_candidate_with_reid_similarity():
    score = score_candidate("DL01AB1284", "DL01AB1234", ["C13", "C15"], reid_similarity=0.93)
    assert 0.0 <= score <= 1.0
    assert score > 0.7  # strong evidence should score high


def test_score_candidate_without_reid_similarity_is_capped():
    """Missing appearance evidence must never let confidence exceed the safety ceiling."""
    score = score_candidate("DL01AB1284", "DL01AB1234", ["C13", "C15"], reid_similarity=None)
    assert score <= 0.85


def test_find_best_candidate_with_no_evidence_returns_none():
    result = find_best_candidate("DL01AB9999", [], reid_similarity=None)
    assert result["candidate_plate"] is None
    assert result["verification_confidence"] == 0.0


def test_find_best_candidate_picks_the_better_supported_conflicting_candidate():
    """Conflicting evidence: two different plates suggested. Must pick the
    one with MORE supporting cameras / higher similarity, not just the first one."""
    supporting_events = [
        {"camera_id": "C13", "plate": "DL01AB1234"},
        {"camera_id": "C15", "plate": "DL01AB1234"},
        {"camera_id": "C20", "plate": "DL01AB9999"},  # weaker, single-camera candidate
    ]
    result = find_best_candidate("DL01AB1284", supporting_events, reid_similarity=None)
    assert result["candidate_plate"] == "DL01AB1234"
    assert len(result["supporting_cameras"]) == 2
