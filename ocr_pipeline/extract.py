from paddleocr import PaddleOCR
from PIL import Image, ImageOps, ImageEnhance
import os
import tempfile

ocr = PaddleOCR(use_angle_cls=True, lang="en")

def _prepare_image(path):
    img = Image.open(path).convert("L")
    img = ImageOps.autocontrast(img)
    img = ImageEnhance.Contrast(img).enhance(1.8)
    img = img.convert("RGB")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp_file.name)
    return temp_file.name

def extract(path):
    prepared_path = _prepare_image(path)
    try:
        result = ocr.ocr(prepared_path, cls=True)
        text = []

        if result and isinstance(result, list):
            for page in result:
                if page is None:
                    continue
                for word in page:
                    if word and len(word) >= 2 and word[1]:
                        txt = str(word[1][0]).strip()
                        conf = float(word[1][1])
                        if txt and conf >= 0.35:
                            text.append(txt)

        return text
    finally:
        if os.path.exists(prepared_path):
            os.remove(prepared_path)