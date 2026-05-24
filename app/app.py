import streamlit as st
import tempfile
import numpy as np

from PIL import Image

from cnn_backbone.backbone import UPIDetector

from forensic_features.ela import run_ela
from forensic_features.noise import noise_score
from forensic_features.block import blockiness
from forensic_features.metadata import metadata
from forensic_features.copymove import orb_features
from forensic_features.phash import phash

try:
    from ocr_pipeline.extract import extract
    from ocr_pipeline.embed import embed
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

try:
    from fusion_model.vector import combine
    from fusion_model.model import model as fusion_model
    FUSION_AVAILABLE = True
except:
    FUSION_AVAILABLE = False


detector = UPIDetector()


def detect(file):

    with tempfile.NamedTemporaryFile(delete=False) as temp:

        temp.write(file.read())

        path = temp.name


    cnn_result = detector.predict(path)


    ela_score = run_ela(path)

    image = np.array(Image.open(path))

    noise = noise_score(image)

    block_score = blockiness(image)

    keypoints = orb_features(image)

    meta = metadata(path)

    hash_value = phash(path)


    if OCR_AVAILABLE:

        text = extract(path)

        ocr_vector = embed(text)

    else:

        ocr_vector = np.zeros(384)


    if FUSION_AVAILABLE:

        try:

            vector = combine(
                ela_score,
                noise,
                block_score,
                len(meta),
                ocr_vector
            )

            prob = fusion_model.predict_proba([vector])[0][1]

            if prob > 0.5:

                fusion_result = f"FAKE screenshot detected (confidence {prob:.2f})"

            else:

                fusion_result = f"REAL screenshot detected (confidence {1-prob:.2f})"

            return f"{fusion_result} | CNN decision: {cnn_result}"

        except:

            return f"CNN decision: {cnn_result}"


    return f"CNN decision: {cnn_result}"


st.title("UPI Screenshot Fake Detector")

uploaded_file = st.file_uploader(
    "Upload screenshot",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:

    st.image(uploaded_file)

    prediction = detect(uploaded_file)

    st.success(prediction)