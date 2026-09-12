import json
from pathlib import Path

from ai.tracking.matcher import CrossCameraMatcher
from ai.tracking.simulation.sumo.verification import verify_candidate
from ai.tracking.simulation.sumo.corrections import (
    create_correction_record,
    apply_correction,
)
from ai.tracking.reconstruct import reconstruct


BASE_DIR = Path(__file__).resolve().parent

TRACKS_FILE = BASE_DIR / "outputs" / "prepared_tracks.json"
OBSERVATIONS_FILE = BASE_DIR / "outputs" / "camera_observations.json"


def main() -> None:

    with TRACKS_FILE.open("r", encoding="utf-8") as file:
        tracks = json.load(file)["tracks"]

    with OBSERVATIONS_FILE.open("r", encoding="utf-8") as file:
        observations = json.load(file)["observations"]

    print("Input local tracks:", len(tracks))
    print("Public observations:", len(observations))

    # ------------------------------------------------------------
    # Controlled verification fault
    # ------------------------------------------------------------

    candidate_pair = None

    for i in range(len(tracks)):
        for j in range(i + 1, len(tracks)):

            a = tracks[i]
            b = tracks[j]

            if a.get("camera_id") == b.get("camera_id"):
                continue

            plate_a = a.get("plate_text") or a.get("plate")
            plate_b = b.get("plate_text") or b.get("plate")

            if plate_a and plate_a == plate_b:
                candidate_pair = (i, j)
                break

        if candidate_pair:
            break

    if candidate_pair is None:
        print("ERROR: Could not find suitable verification pair.")
        return

    i, j = candidate_pair

    track_a = tracks[i]
    track_b = tracks[j]

    original_plate = track_b.get("plate_text") or track_b.get("plate")

    # ------------------------------------------------------------
    # Simulated Re-ID evidence
    # ------------------------------------------------------------

    track_a["embedding"] = [1.0, 0.0, 0.0, 0.0]
    track_b["embedding"] = [1.0, 0.0, 0.0, 0.0]

    # ------------------------------------------------------------
    # Inject OCR error
    # ------------------------------------------------------------

    corrupted_plate = "DL99ZZ9999"

    if "plate_text" in track_b:
        track_b["plate_text"] = corrupted_plate
    else:
        track_b["plate"] = corrupted_plate

    # ------------------------------------------------------------
    # MATCH
    # ------------------------------------------------------------

    matcher = CrossCameraMatcher()
    result = matcher.match(tracks)

    verification_candidates = result[
        "verification_candidates"
    ]

    print()
    print("=== MATCHING ===")
    print("Accepted matches:", len(result["matches"]))
    print(
        "Verification candidates:",
        len(verification_candidates),
    )

    if not verification_candidates:
        print("FAILED: No verification candidate.")
        return

    candidate = verification_candidates[0]

    print()
    print("=== VERIFICATION CANDIDATE ===")
    print(json.dumps(candidate, indent=2))

    # ------------------------------------------------------------
    # EVIDENCE RETRIEVAL + VERIFICATION
    # ------------------------------------------------------------

    verification = verify_candidate(
        candidate,
        observations,
    )

    print()
    print("=== VERIFICATION RESULT ===")
    print(json.dumps(verification, indent=2))

    # ------------------------------------------------------------
    # CORRECTION + PROVENANCE
    # ------------------------------------------------------------

    if verification["status"] == "RESOLVED":

        correction = verification["correction"]

        print()
        print("=== CORRECTION ===")
        print(
            "Camera:",
            correction["camera_id"],
        )
        print(
            "Original:",
            correction["original_plate"],
        )
        print(
            "Corrected:",
            correction["corrected_plate"],
        )
        print(
            "Reason:",
            verification["reason"],
        )

        # Create immutable-style correction record.
        correction_record = create_correction_record(
            candidate,
            verification,
        )

        print()
        print("=== CORRECTION RECORD ===")
        print(
            json.dumps(
                correction_record,
                indent=2,
            )
        )

        # -------------------------------------------------------------
        # CLOSED LOOP: CORRECT -> MATCH AGAIN -> RECONSTRUCT
        # -------------------------------------------------------------
        corrected_tracks = apply_correction(
            result["tracks"],
            correction_record,
        )
        corrected_match = matcher.match(corrected_tracks)
        before_trajectory = reconstruct(result)
        after_trajectory = reconstruct(corrected_match)

        target = correction_record["camera_id"], correction_record["local_track_id"]
        corrected_target = next(
            (track for track in corrected_tracks
             if (track.get("camera_id"), track.get("local_track_id")) == target),
            None,
        )

        print()
        print("=== TRAJECTORY FEEDBACK ===")
        print("Corrected track:", target)
        print("Plate after correction:", corrected_target.get("plate_text") if corrected_target else None)
        print("Trajectories before correction:", len(before_trajectory["trajectories"]))
        print("Trajectories after correction:", len(after_trajectory["trajectories"]))
        print("Accepted matches after correction:", len(corrected_match["matches"]))

        target_plate = correction_record["corrected_plate"]
        target_traj = next(
            (traj for traj in after_trajectory["trajectories"]
             if traj.get("plate") == target_plate and len(traj.get("camera_sequence", [])) >= 2),
            None,
        )
        if target_traj is None:
            raise RuntimeError("Correction was not fed back into trajectory reconstruction")

        print("Corrected trajectory camera sequence:", target_traj["camera_sequence"])
        print()
        print("SUCCESS: OCR contradiction resolved and fed back into trajectory reconstruction.")

    else:
        print()
        print(
            "Verification unresolved. "
            "No automatic correction applied."
        )


if __name__ == "__main__":
    main()