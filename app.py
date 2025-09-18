from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env
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

# Set system message (behavior)
chat.send_message("You are a helpful AI assistant giving health advice.")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a valid message."})

    print(f"User: {user_message}")  # Log user message

    try:
        # Send user message to chat
        response = chat.send_message(user_message)
        
        # Extract text from response
        bot_reply = getattr(response, "text", None)
        if not bot_reply and hasattr(response, "candidates"):
            bot_reply = response.candidates[0].content.parts[0].text
        
        print(f"Bot: {bot_reply}")  # Log bot reply

    except Exception as e:
        print("Error:", e)
        bot_reply = "Sorry, something went wrong. Please try again."

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    print("🚀 Backend server running at http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
