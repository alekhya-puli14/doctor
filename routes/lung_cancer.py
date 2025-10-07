from flask import Blueprint, request, jsonify, send_from_directory, render_template
import os
import numpy as np
import tensorflow as tf
import cv2
from werkzeug.utils import secure_filename

lung_cancer_bp = Blueprint("lung_cancer", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '../static/uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, '../static/processed')
MODEL_PATH = os.path.join(BASE_DIR, '../models/lung_cancer_model.h5')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Load the trained lung cancer model
model = tf.keras.models.load_model(MODEL_PATH)

# Class labels
CLASS_NAMES = ["Benign", "Malignant", "Normal"]

def process_and_save_image(image_path, prediction, confidence):
    """Overlay prediction + confidence on image and save."""
    img = cv2.imread(image_path)
    img = cv2.resize(img, (300, 300))

    overlay_text = f"{prediction} ({confidence:.2f}%)"
    
    # Define text parameters
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    text_color = (255, 255, 255)  # White text
    bg_color = (0, 0, 0)  # Black background
    text_size = cv2.getTextSize(overlay_text, font, font_scale, font_thickness)[0]
    
    # Positioning text at top
    text_x = (img.shape[1] - text_size[0]) // 2
    text_y = 40  # Top position

    # Draw black rectangle behind text
    cv2.rectangle(img, (text_x - 5, text_y - 30), (text_x + text_size[0] + 5, text_y + 5), bg_color, -1)
    
    # Put the text on the image
    cv2.putText(img, overlay_text, (text_x, text_y), font, font_scale, text_color, font_thickness)

    processed_path = os.path.join(RESULT_FOLDER, os.path.basename(image_path))
    cv2.imwrite(processed_path, img)
    return processed_path

@lung_cancer_bp.route("/lung_cancer")
def lung_cancer_home():
    return render_template("cancer.html")

@lung_cancer_bp.route("/lung_cancer/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"})

    # Save uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Preprocess image
    img = tf.keras.preprocessing.image.load_img(filepath, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Predict
    predictions = model.predict(img_array)[0]
    predicted_class_idx = np.argmax(predictions)
    predicted_label = CLASS_NAMES[predicted_class_idx]
    confidence = predictions[predicted_class_idx] * 100  # Convert to percentage

    # Process image with text overlay
    processed_img_path = process_and_save_image(filepath, predicted_label, confidence)

    # Return JSON response
    return jsonify({
        "prediction": predicted_label,
        "confidence": round(float(confidence), 2),
        'uploaded_img': '/static/uploads/' + os.path.basename(filepath),
        'processed_img': '/static/processed/' + os.path.basename(processed_img_path)
    })

@lung_cancer_bp.route("/lung_cancer/results/<filename>")
def get_result_image(filename):
    return send_from_directory(RESULT_FOLDER, filename)
