from flask import Blueprint, request, jsonify,render_template
import random
import re

# Define Blueprint for Chatbot
chatbot_bp = Blueprint("chatbot", __name__)

class SimpleBot:
    def __init__(self):
        self.responses = {
            r'hi|hello|hey': [
                "Hello! How can I help you today?",
                "Hi there! Nice to meet you!",
                "Hey! What's on your mind?"
            ],
            r'how are you': [
                "I'm doing great, thanks for asking! How about you?",
                "I'm functioning well! How are you?",
                "All good here! How's your day going?"
            ],
            r'what is your name|who are you': [
                "I'm Respira Bot, your friendly chatbot!",
                "You can call me Respira Bot!",
                "I'm Respira Bot, ready to chat with you!"
            ],
            r'bye|goodbye': [
                "Goodbye! Have a great day!",
                "See you later! Take care!",
                "Bye! Come back soon!"
            ],
            r'thank you|thanks': [
                "You're welcome!",
                "Glad I could help!",
                "Anytime!"
            ],
            r'what is pneumonia': [
                "Pneumonia is an infection that inflames the air sacs in one or both lungs.",
            ],
            r'pneumonia symptoms': [
                "Persistent cough, Coughing up blood, Chest pain, Fever & night sweats, Unintentional weight loss."
            ],
            r'pneumonia causes': [
                "Bacterial, Viral, Fungal"
            ],
            r'pneumonia risk factors': [
                "Age, Weakened immune system, Smoking and alcohol use, Chronic lung diseases, Hospitalization."
            ],
            r'pneumonia diagnosis': [
                "Clinical examination, Chest X-ray or CT scan, Blood tests, Sputum test, Pulse oximetry."
            ],
            r'pneumonia prevention': [
                "Vaccination, Good hygiene, Avoiding smoking & excessive alcohol, Strengthening the immune system."
            ],
            r'what is tuberculosis': [
                "Tuberculosis (TB) is an infectious disease caused by the bacterium Mycobacterium tuberculosis.",
                "It primarily affects the lungs but can also impact other parts of the body, such as the kidneys, spine, and brain."
            ],
            r'tuberculosis types|types of tuberculosis': [
                "Latent TB, Active TB, Extrapulmonary TB."
            ],
            r'tuberculosis causes|causes of tb': [
                "airborne droplets, weak immune systems"
            ],
            r'tuberculosis symptoms|symptoms of tb': [
                "Persistent cough, Fever & night sweats, Unintentional weight loss, Fatigue & weakness, Chest pain & difficulty breathing."
            ],
            r'tuberculosis diagnosis|diagnosis of tb': [
                "Tuberculin skin test (Mantoux test), Chest X-ray or CT scan, Sputum test."
            ],
            r'tuberculosis treatment|treatment for tb': [
                "Isoniazid (INH), Rifampin (RIF), Ethambutol (EMB), Pyrazinamide (PZA)."
            ],
            r'tuberculosis prevention|prevention of tb': [
                "BCG vaccine, Early detection & treatment, Good ventilation, Wearing masks."
            ]
        }

        self.default_responses = [
            "I'm not sure I understand. Could you rephrase that?",
            "That's interesting, but I'm not sure how to respond.",
            "I'm still learning and don't know how to answer that.",
            "Could you try asking that in a different way?"
        ]

    def get_response(self, user_input):
        """Get chatbot response based on user input"""
        if not user_input.strip():
            return "Please enter a valid question."

        user_input = user_input.lower()
        for pattern, responses in self.responses.items():
            if re.search(pattern, user_input):
                return random.choice(responses)

        return random.choice(self.default_responses)

# Initialize the chatbot
bot = SimpleBot()

@chatbot_bp.route("/chatbot", methods=["GET"])
def chatbot_page():
    """Render chatbot UI"""
    return render_template("chatbot.html")

@chatbot_bp.route("/get_response", methods=["POST"])
def chatbot_api():
    try:
        user_message = request.form.get('message', '').strip()
        response = bot.get_response(user_message)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

