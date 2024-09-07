from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace these with your bot token and chat IDs
BOT_TOKEN = '7293431359:AAH3QLzmiod9Lf1SQ0bkqgHzk1rMxVLqqOQ'  # Telegram bot token from BotFather
CHAT_ID_A = '101883112'  # Replace with user A's chat ID
CHAT_ID_B = '109566532'  # Replace with user B's chat ID
CHAT_ID_C = '85607859'  # Replace with user C's chat ID


# Helper function to send a Telegram message to a specific chat ID
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response.json()


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
        # Notify the form submitter (can use a stored submitter ID if available)
        return jsonify({"message": f"Form rejected at stage {stage}"})

    return jsonify({"error": "Invalid decision"}), 400


if __name__ == '__main__':
    app.run(debug=True)
