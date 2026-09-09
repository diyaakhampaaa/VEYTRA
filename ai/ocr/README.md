# Member 2 — License-plate OCR (READ stage)

READ module for VEYTRA (SIH 2026, PS 26127). This package is the **READ** stage:

DETECT -> **READ** -> TRACK -> MATCH (Re-ID) -> VERIFY -> CORRECT -> RECONSTRUCT -> ANALYZE -> VISUALIZE -> ALERT

It consumes a **plate crop** from Member 1 (`plate_bbox`) and returns normalized
Indian plate text plus a confidence score. It does not call detection, tracking,
or Re-ID. Recognition uses **pretrained PaddleOCR** (no training).

## Input / output contract

**Input:** a plate crop image (path, encoded bytes, or OpenCV `ndarray`).

**Output JSON** (consumed by Member 3 and Member 4):

```json
{
  "plate": "DL01AB1234",
  "confidence": 0.94,
  "alternatives": ["DL01AB1284"]
}
```

If OCR fails entirely (blank crop, decode failure, empty recognition):

```json
{
  "plate": null,
  "confidence": 0.0,
  "alternatives": []
}
```

`read_plate` **never raises**. `confidence` is always a float in `[0, 1]`.

Invalid strings that cannot match an Indian plate regex are **not** rewritten
into a different valid-looking plate. They are returned as the normalized OCR
text with **capped low confidence** so downstream modules can flag them.

## Setup

From the repository root (PaddlePaddle wheels are typically Python 3.9–3.12; unit tests mock OCR and also run on 3.13):

```bash
pip install -r ai/ocr/requirements.txt
```

This installs `paddleocr`, `paddlepaddle`, `opencv-python`, FastAPI, and test deps.
The first PaddleOCR run downloads pretrained recognition weights (network required).
Point `VEYTRA_OCR_REC_MODEL_DIR` at a local model directory to skip the download.

On Windows, use the official CPU wheel if the default install fails:

```bash
python -m pip install paddlepaddle==2.6.2 -f https://www.paddlepaddle.org.cn/whl/windows/cpu/avx/stable.html
pip install -r ai/ocr/requirements.txt
```

## Python API

```python
from ai.ocr import read_plate

result = read_plate("ai/ocr/tests/sample_crops/crop1.jpg")
# {"plate": "DL01AB1234", "confidence": 0.94, "alternatives": [...]}
```

Preprocessing (always applied before OCR): grayscale, upscale of tiny crops,
CLAHE contrast, optional deskew (`VEYTRA_OCR_DESKEW`, default on).

## CLI

From `ai/ocr/`:

```bash
python run_ocr.py --image tests/sample_crops/crop1.jpg
```

From the repository root:

```bash
python ai/ocr/run_ocr.py --image ai/ocr/tests/sample_crops/crop1.jpg
```

Confirm the printed JSON matches the contract (`plate`, `confidence`, `alternatives`).

Regenerate synthetic sample crops:

```bash
python ai/ocr/tests/generate_sample_crops.py
```

| File | Condition |
|------|-----------|
| `crop1.jpg` | Clean plate (`DL01AB1234`) |
| `crop2.jpg` | Blurry |
| `crop3.jpg` | Angled / deskew candidate |
| `crop4.jpg` | Partially occluded |
| `crop_unreadable.jpg` | Black / unreadable garbage crop |

## FastAPI

From the repository root:

```bash
uvicorn ai.ocr.api:app --reload
```

In Postman: `POST http://127.0.0.1:8000/ocr` as `form-data` with key `file`
(type File) set to a plate crop. The response body is the same JSON contract.

## Tests

```bash
pytest ai/ocr/tests/ -v
```

PaddleOCR is mocked in unit tests so they do not download weights. The suite
includes an unreadable/garbage crop that must return
`plate: null`, `confidence: 0.0`, `alternatives: []` without calling OCR.

## Sample I/O

**Input:** `ai/ocr/tests/sample_crops/crop1.jpg` (synthetic clean crop of `DL01AB1234`).

**Output** (shape is fixed; the numeric confidence comes from PaddleOCR and can vary):

```json
{
  "plate": "DL01AB1234",
  "confidence": 0.94,
  "alternatives": ["DL01AB1284"]
}
```

`alternatives` is filled when confidence is below `VEYTRA_OCR_LOW_CONFIDENCE`
(default `0.75`) or the primary string fails regex validation. Common swaps:
`0/O`, `1/I`, `8/B`, `5/S`, `2/Z`, plus digit `8/3`. A high-confidence valid
read may return `"alternatives": []`.

CLI one-liner to reprint JSON:

```bash
python ai/ocr/run_ocr.py --image ai/ocr/tests/sample_crops/crop1.jpg
```

## Environment variables

| Variable | Default | Meaning |
|----------|---------|---------|
| `VEYTRA_OCR_LANG` | `en` | PaddleOCR language |
| `VEYTRA_OCR_USE_GPU` | `0` | `1` to use GPU paddle |
| `VEYTRA_OCR_USE_DET` | `0` | `1` to run text detection on the crop (recognition-only is default) |
| `VEYTRA_OCR_REC_MODEL_DIR` | unset | Local recognition model directory |
| `VEYTRA_OCR_DET_MODEL_DIR` | unset | Local detection model directory |
| `VEYTRA_OCR_DESKEW` | `1` | Deskew in preprocessing |
| `VEYTRA_OCR_MIN_SIDE` | `48` | Upscale crops shorter than this (pixels) |
| `VEYTRA_OCR_LOW_CONFIDENCE` | `0.75` | Below this, emit confusion alternatives |
| `VEYTRA_OCR_INVALID_CONF_CAP` | `0.45` | Max confidence for regex-invalid reads |
| `VEYTRA_OCR_ALT_LIMIT` | `5` | Max alternatives |
| `VEYTRA_OCR_EXTRA_PLATE_REGEX` | unset | Extra comma-separated regexes for validation only |

## Layout

```
ai/ocr/
  __init__.py
  ocr_engine.py         # PaddleOCR wrapper + preprocessing + read_plate()
  plate_validator.py    # Indian plate regex + normalization + alternatives
  api.py                # FastAPI app: POST /ocr
  run_ocr.py            # CLI
  requirements.txt
  README.md
  tests/
    test_ocr_engine.py
    generate_sample_crops.py
    sample_crops/
```
