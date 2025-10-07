from flask import Blueprint, request, jsonify, render_template
import os
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2

pneumonia_bp = Blueprint('pneumonia', __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '../static/uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, '../static/processed')
MODEL_PATH = os.path.join(BASE_DIR, '../models/pneumonia_model.h5')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

model = tf.keras.models.load_model(MODEL_PATH)

def process_and_save_image(image_path, prediction, confidence):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (300, 300))
    plt.figure(figsize=(4, 4))
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.title(f"Prediction: {prediction} ({confidence:.2f}%)")
    processed_path = os.path.join(PROCESSED_FOLDER, os.path.basename(image_path))
    plt.savefig(processed_path)
    plt.close()
    return processed_path

@pneumonia_bp.route('/pneumonia')
def home():
    return render_template('pneumonia.html')

@pneumonia_bp.route('/pneumonia/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    img = tf.keras.preprocessing.image.load_img(filepath, target_size=(150, 150))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    prediction = model.predict(img_array)[0][0]
    label = "Pneumonia" if prediction > 0.5 else "Normal"
    confidence = round(float(prediction) * 100, 2) if prediction > 0.5 else round((1 - float(prediction)) * 100, 2)

    processed_img_path = process_and_save_image(filepath, label, confidence)

    return jsonify({
        'prediction': label,
        'confidence': confidence,
        'uploaded_img': '/static/uploads/' + os.path.basename(filepath),
        'processed_img': '/static/processed/' + os.path.basename(processed_img_path)
    })
