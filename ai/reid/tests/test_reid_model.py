from ai.reid.reid_model import FastReIDModel, cosine_similarity


def test_cosine_similarity_is_bounded():
    assert cosine_similarity([1, 0], [1, 0]) == 1.0
    assert cosine_similarity([1, 0], [0, 1]) == 0.0


def test_missing_fastreid_assets_are_reported():
    model = FastReIDModel("missing-config.yml", "missing-weights.pth")
    assert model.available is False
