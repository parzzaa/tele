from flask import Flask, request, jsonify, render_template
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Replace these with your bot token and chat IDs
BOT_TOKEN = '7293431359:AAH3QLzmiod9Lf1SQ0bkqgHzk1rMxVLqqOQ'  # Get the Telegram bot token from an environment variable
CHAT_ID_A = '101883112'  # Replace with user A's chat ID
CHAT_ID_B = '109566532'  # Replace with user B's chat ID
CHAT_ID_C = '85607859'   # Replace with user C's chat ID

# Helper function to send a Telegram message
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to chat ID {chat_id}: {e}")
        return {"error": "Failed to send message"}
    return response.json()

# Route to serve the form (HTML)
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission (submitted by 'd')
@app.route('/submit', methods=['POST'])
def submit_form():
    form_data = request.json
    # Notify reviewer 'a'
    send_telegram_message(CHAT_ID_A, f"New form submitted for review:\n{form_data}")
    return jsonify({"message": "Form submitted and sent to reviewer A", "nextStage": "a"})

# Route to handle review decision
@app.route('/review/<stage>', methods=['POST'])
def review_form(stage):
    decision = request.json.get('decision')

    if stage == 'a' and decision == 'accept':
        # Notify reviewer 'b'
        send_telegram_message(CHAT_ID_B, "Form approved by A, now it's your turn to review.")
        return jsonify({"nextStage": "b"})

    elif stage == 'b' and decision == 'accept':
        # Notify reviewer 'c'
        send_telegram_message(CHAT_ID_C, "Form approved by B, now it's your turn to review.")
        return jsonify({"nextStage": "c"})

    elif stage == 'c' and decision == 'accept':
        # Notify both 'a' and 'b' that the review process is complete
        send_telegram_message(CHAT_ID_A, "Form fully approved by all reviewers.")
        send_telegram_message(CHAT_ID_B, "Form fully approved by all reviewers.")
        return jsonify({"nextStage": None, "message": "Review process completed"})

    elif decision == 'reject':
        return jsonify({"message": f"Form rejected at stage {stage}"})

    return jsonify({"error": "Invalid decision"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
