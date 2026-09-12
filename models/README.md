# Member 3 Re-ID model assets

VEYTRA's Re-ID adapter is implemented in `ai/reid/reid_model.py` and expects:

- a FastReID-compatible configuration file
- a compatible vehicle Re-ID checkpoint trained for the VeRi-776 task

Model weights are intentionally **not committed to Git**. They are large
binary artifacts and should be stored locally or in the team's model-artifact
storage.

Recommended local layout:

```text
models/
  reid/
    veri_fastreid_config.yaml
    veri_fastreid_model.pth
```

Then initialize:

```python
from ai.reid import FastReIDModel

model = FastReIDModel(
    config_path="models/reid/veri_fastreid_config.yaml",
    weights_path="models/reid/veri_fastreid_model.pth",
    device="cuda",
)
model.load()
embedding = model.embed(vehicle_crop)
```

The rest of Member 3 does not depend on the checkpoint being present:
unit tests can run without FastReID/PyTorch.

Do not commit `.pth`, `.pt`, `.onnx`, or other large model binaries.
