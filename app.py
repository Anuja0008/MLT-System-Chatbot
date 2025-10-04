from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# Configure Gemini API key
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY not found in environment variables!")
genai.configure(api_key=GENAI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")
chat = model.start_chat()

# System message
chat.send_message("You are a helpful AI assistant giving health advice.")

# Predefined lab info
LAB_HOURS = "Ariana Labs is open from 8:00 AM to 6:00 PM."
TESTS = [
    "Insulin Dose Calculator",
    "Blood Urea Nitrogen (BUN) to Creatinine Ratio",
    "Estimated Glomerular Filtration Rate (eGFR)",
    "INR (International Normalized Ratio)",
    "Lipid Profile Calculation"
]

# Predefined test guidance (concise and safe)
TEST_GUIDANCE = {
    "insulin dose calculator": (
        "To use the Insulin Dose Calculator safely:\n"
        "1. Consult your healthcare team to set your insulin-to-carb ratio and correction factor.\n"
        "2. Know your target blood glucose range.\n"
        "3. Accurately count carbs in meals.\n"
        "4. Never adjust settings on your own; always follow professional guidance."
    ),
    # Add other test guidance as needed, e.g.:
    # "egfr": "Short explanation about eGFR test..."
}

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_message = data.get("message", "").strip().lower()  # lowercase for easier matching

    if not user_message:
        return jsonify({"reply": "Please enter a valid message."})

    print(f"User: {user_message}")

    # 1️⃣ Predefined Lab Hours
    lab_hours_keywords = ["lab hours", "open", "what time", "working hours"]
    if any(kw in user_message for kw in lab_hours_keywords):
        bot_reply = LAB_HOURS

    # 2️⃣ Predefined Lab Tests / Services
    elif any(kw in user_message for kw in ["tests", "test names", "services", "diagnostic"]):
        bot_reply = "Here are the tests offered at Ariana Labs:\n" + \
                    "\n".join(f"{i+1}. {test}" for i, test in enumerate(TESTS))

    # 3️⃣ Predefined guidance for specific tests
    elif any(test_name in user_message for test_name in TEST_GUIDANCE):
        for test_name, guidance in TEST_GUIDANCE.items():
            if test_name in user_message:
                bot_reply = guidance
                break

    # 4️⃣ Fallback to AI for other queries
    else:
        try:
            response = chat.send_message(user_message)
            bot_reply = getattr(response, "text", None)
            if not bot_reply and hasattr(response, "candidates"):
                bot_reply = response.candidates[0].content.parts[0].text
        except Exception as e:
            print("Error:", e)
            bot_reply = "Sorry, something went wrong. Please try again."

    print(f"Bot: {bot_reply}")
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    print("🚀 Backend server running at http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
