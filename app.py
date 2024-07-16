from flask import Flask, render_template, request, redirect, url_for, session
import pyotp
import qrcode
from io import BytesIO
import base64
import random

app = Flask(__name__)
app.secret_key = '1234#####$' 

# Define a dictionary to store user IDs and passwords
user_credentials = {
    "john_doe": "p@ssw0rd!Doe",
    "jane_doe": "J@ne_2p@ss!",
    "alice_smith": "Al!c3Sm!th&20",
    "bob_jones": "B0bJones@123",
    "emily_wang": "3m!lyP@ssw0rd",
    "michael_brown": "M1ch@elBr0wn!",
    "sarah_garcia": "$@r@hG@rc!@123",
    "david_miller": "D@v!dMi11erP@$$",
    "lisa_taylor": "L!$@T@yl0r#2024",
    "matthew_clark": "M@tthewC!@rk&!23"
}


# Dictionary to store secret keys
secret_keys = {}

# Fake data for the dashboard
def generate_fake_data():
    return {
        "total_sales": random.randint(1000, 10000),
        "total_orders": random.randint(50, 200),
        "total_customers": random.randint(10, 50),
        "total_products": random.randint(100, 500)
    }

@app.route("/")
def index():
    return render_template("index.html", user_credentials=user_credentials)

@app.route("/login", methods=["POST"])
def login():
    user_id = request.form["user_id"]
    password = request.form["password"]

    if user_id in user_credentials and user_credentials[user_id] == password:
        # Generate a random secret key
        secret_key = pyotp.random_base32()

        # Store the secret key for the user
        secret_keys[user_id] = secret_key

        # Generate OTP URI
        otp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(user_id, issuer_name="MFA Demo")

        # Generate QR Code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(otp_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to base64 string
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return render_template("qr_code.html", img_str=img_str, user_id=user_id)
    else:
        return "Invalid credentials. Please try again."

@app.route("/authenticate", methods=["POST"])
def authenticate():
    user_id = request.form["user_id"]
    provided_code = request.form["code"]

    if user_id in secret_keys:
        secret_key = secret_keys[user_id]
        totp = pyotp.TOTP(secret_key)
        if totp.verify(provided_code):
            fake_data = generate_fake_data()
            session["user_id"] = user_id  # Store the user ID in the session
            return render_template("dashboard.html", user_id=user_id, fake_data=fake_data)
        else:
            return "Authentication failed. Invalid code."
    else:
        return "User not found."
    
@app.route("/logout")
def logout():
    # Clear the user's session data
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
