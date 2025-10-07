from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
import firebase_admin
from firebase_admin import credentials, auth, firestore
import boto3
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routes.pneumonia import pneumonia_bp
from routes.tuberculosis import tuberculosis_bp
from routes.chatbot import chatbot_bp
from routes.lung_cancer import lung_cancer_bp
from routes.covid import covid_bp




app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ✅ Firebase Initialization
# Create Firebase credentials from environment variables
firebase_cred = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
}

cred = credentials.Certificate(firebase_cred)
firebase_admin.initialize_app(cred)
db = firestore.client()

# ✅ Firebase Web API Key (For Authentication)
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")

# ✅ AWS S3 Configuration (For Profile Pictures)
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# ✅ Register Blueprints
app.register_blueprint(pneumonia_bp)
app.register_blueprint(tuberculosis_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(lung_cancer_bp) 
app.register_blueprint(covid_bp)


@app.route("/session_login", methods=["POST"])
def session_login():
    try:
        data = request.json
        id_token = data.get("idToken")

        if not id_token:
            return jsonify({"success": False, "error": "Missing ID token"}), 400

        # ✅ Verify Firebase ID token
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]  # Extract user ID

        # ✅ Store user ID in Flask session
        session["user"] = user_id
        print(f"✅ Session set for user: {user_id}")

        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"❌ Session login error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ✅ Route: Home (Login Page)
@app.route('/')
def home():
    return render_template('login.html')

# ✅ Route: Login (Session Management)
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password required!"}), 400

        # Firebase Authentication Request
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        response = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
        firebase_response = response.json()

        if "idToken" in firebase_response:
            session["user"] = firebase_response["localId"]
            return jsonify({"success": True, "redirect": "/dashboard"}), 200
        else:
            return jsonify({"success": False, "error": firebase_response.get("error", {}).get("message", "Unknown error")}), 401
    except Exception as e:
        return jsonify({"success": False, "error": "Internal Server Error"}), 500

# ✅ Route: Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)  # Remove user session
    return jsonify({"success": True, "redirect": "/"})


# ✅ Route: Profile Page
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        user_id = session["user"]  # Get logged-in user ID
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            print(f"✅ User Data from Firestore: {user_data}")  # Debugging step
        else:
            print("❌ User not found in Firestore")  # Debugging step
            user_data = {"name": "", "phone": "", "profilePic": ""}

        return render_template("dashboard.html", user=user_data)

    print("❌ User not in session, redirecting to home.")
    return redirect(url_for("home"))  # Redirect if no session exists

@app.route('/profile')
def profile():
    if "user" not in session:
        return redirect(url_for("home"))  # Redirect to login if user is not in session

    return render_template('profile.html', 
                           name=session.get("name"),
                           contact=session.get("contact"),
                           clinic=session.get("clinic"),
                           profile=session.get("profile"),
                           disease=session.get("disease"))


# ✅ Route: Update Profile (Name & Phone)
@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user" not in session:
        return redirect(url_for("home"))

    user_id = session["user"]
    name = request.form.get("name")
    phone = request.form.get("phone")

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    # ✅ Update Name & Phone
    if not user_doc.exists:
        user_ref.set({"name": name, "phone": phone, "profilePic": ""})
    else:
        user_ref.update({"name": name, "phone": phone})

    # ✅ Check if a new profile picture is uploaded
    if "profile_pic" in request.files and request.files["profile_pic"].filename != "":
        file = request.files["profile_pic"]
        try:
            file_extension = file.filename.split(".")[-1]
            file_key = f"profile_pics/{user_id}.{file_extension}"

            # Upload file to AWS S3
            s3.upload_fileobj(
                file, S3_BUCKET, file_key,
                ExtraArgs={"ContentType": file.content_type}
            )

            # ✅ Generate public URL of the uploaded profile pic
            file_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{file_key}"

            # ✅ Update Firestore with new profile picture URL
            user_ref.update({"profilePic": file_url})
            print(f"✅ Profile picture updated for {user_id}: {file_url}")

        except Exception as e:
            print(f"❌ S3 Upload Error: {e}")
            return f"Upload Failed: {e}", 500

    print(f"✅ Profile updated successfully for {user_id}")
    return redirect(url_for("dashboard"))


# ✅ Route: Upload Profile Picture
@app.route("/upload_profile_pic", methods=["POST"])
def upload_profile_pic():
    if "user" not in session:
        return redirect(url_for("home"))

    user_id = session["user"]
    
    if "profile_pic" not in request.files:
        return "No file uploaded", 400
    
    file = request.files["profile_pic"]
    if file.filename == "":
        return "No selected file", 400

    try:
        file_extension = file.filename.split(".")[-1]
        file_key = f"profile_pics/{user_id}.{file_extension}"

        # Upload to AWS S3
        s3.upload_fileobj(
            file, S3_BUCKET, file_key,
            ExtraArgs={"ContentType": file.content_type, "ACL": "public-read"}
        )

        file_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{file_key}"

        # Update Firestore
        db.collection("users").document(user_id).update({"profilePic": file_url})

        return redirect(url_for("profile"))

    except Exception as e:
        return f"Upload Failed: {e}", 500

# ✅ Other Routes
@app.route('/home')
def main():
    if "user" in session:
        user_id = session["user"]  # Get logged-in user ID
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            print(f"✅ User Data from Firestore: {user_data}")  # Debugging step
        else:
            print("❌ User not found in Firestore")  # Debugging step
            user_data = {"name": "", "phone": "", "profilePic": ""}

        return render_template("landing.html", user=user_data)

    print("❌ User not in session, redirecting to home.")
    return redirect(url_for("home"))

@app.route('/online')
def online():
    return render_template('online.html')

@app.route('/offline')
def offline():
    return render_template('offline.html')

@app.route('/Pneumonia')
def pneumonia():
    return render_template('pneumonia.html')

@app.route('/appointment')
def appointment():
    if "user" not in session:
        return redirect(url_for("home"))
    return render_template("index2.html")

@app.route("/videocall/<room_id>")
def video_call(room_id):
    return render_template("videocall.html", room_id=room_id)

@app.route('/xrays')
def xrays():
    return render_template('xrays.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/queries')
def queries():
    return render_template('queries.html')

@app.route('/Tuberculosis')
def tuberculosis():
    return render_template('tuberculosis.html')

@app.route('/videocall')
def videocall():
    return render_template('index.html')
@app.route('/lung_cancer')
def lung_cancer():
    return render_template('cancer.html')


# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "True").lower() == "true")
