import os
import numpy as np
import tensorflow as tf
import cv2
from flask import Blueprint, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

# Create Blueprint
covid_bp = Blueprint("covid", __name__)

# Load trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/covid_model.h5")  # Adjusted path
model = tf.keras.models.load_model(MODEL_PATH)

# Define upload and processed folders (adjusting for routes folder)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../static/uploads")
PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), "../static/processed")

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# Function to preprocess image for model input
def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Read as grayscale
    img = cv2.resize(img, (224, 224))  # Resize to match model input
    img = img / 255.0  # Normalize pixel values
    img = np.expand_dims(img, axis=-1)  # Add channel dimension → (224, 224, 1)
    img = np.expand_dims(img, axis=0)  # Add batch dimension → (1, 224, 224, 1)
    return img


# Function to predict class and confidence
def predict_image(img_path):
    try:
        img = preprocess_image(img_path)
        prediction = model.predict(img)[0][0]  # Get raw probability

        print(f"DEBUG: Raw Model Output for {img_path} -> {prediction:.4f}")

        # Classification logic
        predicted_class = "COVID" if prediction < 0.5 else "Normal"
        confidence = round(float(prediction) * 100, 2) if prediction > 0.5 else round((1 - float(prediction)) * 100, 2)

        print(f"DEBUG: Predicted -> {predicted_class}, Confidence -> {confidence}%")
        return predicted_class, confidence

    except Exception as e:
        print(f"Error: {e}")
        return "Error", 0


# Function to process and save image with text overlay
def process_and_save_image(image_path, predicted_class, confidence):
    img = cv2.imread(image_path)

    if img is None:
        print(f"DEBUG: Image read failed! Check path: {image_path}")
        return ""

    # Add prediction text overlay
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f"{predicted_class} ({confidence}%)"
    cv2.putText(img, text, (10, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    processed_filename = "processed_" + os.path.basename(image_path)
    processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)

    # Ensure directory exists
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)

    cv2.imwrite(processed_path, img)
    
    print(f"DEBUG: Processed image saved at {processed_path}")  # Debug print
    return processed_filename  # Return filename only (not full path)


# Home route
@covid_bp.route("/covid", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Predict
            predicted_class, confidence = predict_image(filepath)
            print(f"DEBUG: Prediction -> {predicted_class}, Confidence -> {confidence}")  # Debug print

            # Process image
            processed_filename = process_and_save_image(filepath, predicted_class, confidence)
            processed_path = f"/static/processed/{processed_filename}"  # Web-accessible path

            print(f"DEBUG: Processed Image Path -> {processed_path}")  # Debug print

            return render_template(
                "covid.html",
                processed_file=processed_path,
                result=predicted_class,
                confidence=confidence,
            )

    return render_template("covid.html", processed_file=None, result=None, confidence=None)


# Static file serving route (for uploaded and processed images)
@covid_bp.route('/static/uploads/<path:filename>')
def serve_uploaded_file(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), "../static/uploads"), filename)

@covid_bp.route('/static/processed/<path:filename>')
def serve_processed_file(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), "../static/processed"), filename)