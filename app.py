from flask import Flask, request, jsonify, render_template, redirect, url_for
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Replace these with your bot token and chat IDs
BOT_TOKEN = '7293431359:AAH3QLzmiod9Lf1SQ0bkqgHzk1rMxVLqqOQ'
CHAT_ID_A = '101883112'
CHAT_ID_B = '109566532'
CHAT_ID_C = '85607859'

# Use an in-memory store to keep track of submissions and reviews
forms = {}

# Helper function to send a Telegram message
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to chat ID {chat_id}: {e}")
        return {"error": "Failed to send message"}
    return response.json()

# Dashboard for all reviewers to see the history of forms
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', forms=forms)

# Route to handle form submission (submitted by 'd')
@app.route('/submit', methods=['POST'])
def submit_form():
    form_data = request.json
    submitter_chat_id = request.headers.get('X-Telegram-Chat-Id')
    form_id = len(forms) + 1

    forms[form_id] = {
        'submitter': submitter_chat_id,
        'data': form_data,
        'stage': 'a',
        'review_comments': [],
        'status': 'Pending'
    }

    review_link = f"https://tele-f3f3.onrender.com/review_form/{form_id}"
    send_telegram_message(CHAT_ID_A, f"New form submitted for review.\n\n[Review the form]({review_link})")

    return jsonify({"message": "Form submitted and sent to reviewer A", "nextStage": "a"})

# Route to render the review form for reviewers (a single form)
@app.route('/review_form/<int:form_id>', methods=['GET'])
def review_form(form_id):
    if form_id not in forms:
        return "Form not found", 404

    form = forms[form_id]
    return render_template('review.html', form=form, form_id=form_id)

# Route to handle review decision (accept/reject + comment)
@app.route('/submit_review/<int:form_id>', methods=['POST'])
def submit_review(form_id):
    if form_id not in forms:
        return "Form not found", 404

    form = forms[form_id]
    decision = request.form['decision']
    comment = request.form.get('comment', '')

    # Save the comment and decision
    form['review_comments'].append({
        'stage': form['stage'],
        'decision': decision,
        'comment': comment
    })

    # Move to the next stage or complete the process
    if form['stage'] == 'a' and decision == 'accept':
        form['stage'] = 'b'
        review_link = f"https://tele-f3f3.onrender.com/review_form/{form_id}"
        send_telegram_message(CHAT_ID_B, f"Form approved by A. [Review the form]({review_link})")
    elif form['stage'] == 'b' and decision == 'accept':
        form['stage'] = 'c'
        review_link = f"https://tele-f3f3.onrender.com/review_form/{form_id}"
        send_telegram_message(CHAT_ID_C, f"Form approved by B. [Review the form]({review_link})")
    elif form['stage'] == 'c' and decision == 'accept':
        form['status'] = 'Approved'
        form['stage'] = 'completed'
        send_telegram_message(CHAT_ID_A, "Form fully approved by all reviewers.")
        send_telegram_message(CHAT_ID_B, "Form fully approved by all reviewers.")
    elif decision == 'reject':
        form['status'] = 'Rejected'
        form['stage'] = 'completed'
        send_telegram_message(forms[form_id]['submitter'], f"Form rejected at stage {form['stage']}.")
        return jsonify({"message": f"Form rejected at stage {form['stage']}"})

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
